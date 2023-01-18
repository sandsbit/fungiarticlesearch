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


@dataclass
class Article:
    name: str
    year: int


@dataclass
class SearchStat:
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


