# This file is part of fungiarticlesearch.
#
# fungiarticlesearch is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# fungiarticlesearch is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with fungiarticlesearch.
# If not, see <https://www.gnu.org/licenses/>.

import sys
import time
import json
import dataclasses
from pathlib import Path
from operator import attrgetter

from APIs import wikipedia
from api_key_manager import ApiKeyManager
from APIs.sciencedirect import ScopusArticleSearcher, SearchStat


def api_key_cli() -> str:
    """
    API key getting CLI.
    :return: the api key.
    """

    akm = ApiKeyManager()
    if akm.is_key_saved():
        for _ in range(3):
            passcode = input('Please, enter a passcode for the saved API key: ')
            try:
                key = akm.read_key(passcode)
            except ValueError:
                print('Invalid passcode.')
                continue
            break
        else:
            print('You failed to enter a passcode for three times. Sorry :(')
            sys.exit(1)
        return key
    else:
        key = input('Please, enter Elsevier API key (see https://dev.elsevier.com/apikey/manage): ')
        if input('Do you want to save it? (Y/n)').lower() == 'y':
            while True:
                pass1 = input('Come up with a passcode for the api key: ')
                pass2 = input('Repeat your passcode: ')
                if pass1 == pass2:
                    break
                print('Passcodes do not match. Please, try again.')
            akm.save_key(key, pass1)
        return key


FUNGI_CATEGORY = 'Fungi_of_Europe'
MINIMAL_YEAR = 2016
NEW_YEAR = 2020
REQUEST = '{} enzymes'

CACHE_FILE = Path('./.fasdata/cache.json')
SAVE_FILE = 'best_fungi_{}.json'

def main() -> None:
    print('Welcome to Fungi Article Search!')
    api_key = api_key_cli()

    print('Starting to parse wikipedia!')
    s = time.time()
    fungi_articles = wikipedia.list_of_articles_in_category(FUNGI_CATEGORY)
    fungi_count = len(fungi_articles)
    e = time.time()
    print('Parsed {} european fungi articles in {:.2f}s.'.format(len(fungi_articles), e - s))

    if not CACHE_FILE.exists():
        print('Searching Scopus with given request: "{}"'.format(REQUEST))
        search_results = []
        s = time.time()
        searcher = ScopusArticleSearcher(api_key)
        for i in range(fungi_count):
            article = fungi_articles[i]
            elapsed = int(time.time() - s)
            elapsed_minutes, elapsed_seconds = divmod(elapsed, 60)
            if i != 0:
                estimated = int((fungi_count - i) * (elapsed / i))
                est_minutes, est_seconds = divmod(estimated, 60)
            else:
                est_minutes = '-'
                est_seconds = '-'
            print('\rSearching fungi: {} ({}/{}). Elapsed time: {}m {}s. '
                  'Estimated time: {}m {}s'.format(article, i, fungi_count, elapsed_minutes, elapsed_seconds,
                                                   est_minutes, est_seconds), end='')
            search_results.append(searcher.theme_statistics(REQUEST.format(article), MINIMAL_YEAR, NEW_YEAR, article))
        elapsed = int(time.time() - s)
        minutes, seconds = divmod(elapsed, 60)
        print('Finished parsing Scopus in {}m {}s'.format(minutes, seconds))
        json.dump(list(map(dataclasses.asdict, search_results)), CACHE_FILE.open('w'))
        print('Parsing results were saved to cache!')
    else:
        print('Loading Scopus search results from cache...')
        search_results = list(map(lambda x: SearchStat(**x), json.load(CACHE_FILE.open('r'))))
        print('Parsing results were loaded from cache!')

    atype = ''
    while atype not in ['p', 'r']:
        atype = input('Select an article type (p for practical, r for review): ').lower()

    if atype == 'r':
        print('Selecting 50% of the most popular fungi...')
        search_results.sort(key=attrgetter('publications_number'))
        search_results = search_results[fungi_count//2:]

        print('Sorting by the percentage of new publications...')
        search_results.sort(key=attrgetter('new_publications_percentage'))
        search_results = search_results[::-1]
    else:
        print('Selecting 70% of the most popular fungi...')
        search_results.sort(key=attrgetter('publications_number'))
        new_fungi_count = int(fungi_count*0.8)
        search_results = search_results[0:new_fungi_count]

        print('Selecting fungi with more new articles percentage than average...')
        percentage_mean = sum(map(attrgetter('new_publications_percentage'), search_results)) / new_fungi_count
        search_results = list(filter(lambda x: x.new_publications_percentage >= percentage_mean, search_results))

        print('Sorting by the number of publications...')
        search_results.sort(key=attrgetter('publications_number'))

    print('Finished! TOP-10 best fungi: ')
    for i in range(0, 10):
        stat = search_results[i]
        print('{}. Fungi: {} (pub: {}, new_pub: {}%)'.format(i+1, stat.theme, stat.publications_number,
                                                             stat.new_publications_percentage))

    if input('Save all results to file? (Y/n)').lower == 'y':
        filename = SAVE_FILE.format(atype)
        json.dump(list(map(dataclasses.asdict, search_results)), open(filename, 'w'))
        print('Successfully saved all results to ' + filename)


if __name__ == '__main__':
    main()
