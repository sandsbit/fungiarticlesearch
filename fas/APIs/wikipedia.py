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

import wikipediaapi


def list_of_articles_in_category(category_name: str, language: str = 'en') -> list[str]:
    """
    Returns all articles in the given category excluding the ones that include the word "list" in their name.
    Doesn't return articles from subcategories.

    The function was tested only with Fungi_of_Europe category! Be careful while using.

    :param category_name: name of the category without spaces like in the url (e.g. Fungi_of_Europe)
    :param language: language of the wiki where to search. Default one is English.
        Format: https://meta.wikimedia.org/wiki/List_of_Wikipedias
    :return: list of titles of all the articles in the category exluding lists.
    """

    wiki = wikipediaapi.Wikipedia(language)
    category = wiki.page('Category:' + category_name)

    articles = []
    for page in category.categorymembers.values():
        if page.namespace == wikipediaapi.Namespace.MAIN and 'list' not in page.title.lower():
            articles.append(page.title)

    return articles
