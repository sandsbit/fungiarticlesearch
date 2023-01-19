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

from dataclasses import dataclass

from elsapy.elsclient import ElsClient
from elsapy.elssearch import ElsSearch


@dataclass
class Article:
    name: str
    year: int


@dataclass
class SearchStat:
    theme: str
    articles: list[Article]
    publications_number: int
    new_publications: int

    @property
    def new_publications_percentage(self) -> float:
        return self.new_publications / self.publications_number * 100


class ScopusArticleSearcher:
    """
    A class to work with SD search statistics.
    """

    client = None

    def __init__(self, api_key: str):
        """
        :param api_key: Elsevier Developer Portal API key
        """
        self.client = ElsClient(api_key)

    def search_for_theme(self, search_request: str, minimal_year: int) -> list[Article]:
        """
        Searches for articles with given request and returns results.

        :param search_request: search request.
        :param minimal_year: minimal year of the publications.
        :return: array of Article dataclasses with results.
        """
        searcher = ElsSearch('TITLE-ABS-KEY("{}") AND PUBYEAR AFT {}'.format(search_request, minimal_year), 'scopus')
        searcher.execute(self.client, get_all=True)

        if 'error' in searcher.results[0].keys():
            if searcher.results['error'] == 'Result set was empty':
                return []
            else:
                raise RuntimeError('Got error while parsing Scopus: ' + searcher.results['error'])

        results = []
        for article in searcher.results:
            title = article['dc:title']
            year = int(article['prism:coverDate'][0:4])
            assert year >= minimal_year
            results.append(Article(title, year))

        return results

    def theme_statistics(self, search_request: str, minimal_year: int, new_year: int, theme: str) -> SearchStat:
        """
        Calculates statistics (number of articles and number of new articles) for a given request.

        :param search_request: search request.
        :param minimal_year: minimal year of the publications.
        :param new_year: year after which publications are considered new.
        :param theme: theme os the search.
        :return: SearchStat dataclass with all statistics
        """

        results = self.search_for_theme(search_request, minimal_year)
        number_of_articles = len(results)
        number_of_new_articles = sum([1 if art.year >= new_year else 0 for art in results])

        return SearchStat(theme, results, number_of_articles, number_of_new_articles)
