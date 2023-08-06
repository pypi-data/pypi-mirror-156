import re

from urllib.parse import urlencode, urljoin

import bs4
import requests

from .exceptions import MovieNotFound


class Backend(object):
    date_pattern = re.compile(r'\w{3} \d{1,2}, \d{4}')
    gross_pattern = re.compile(r'\$\d[\d,]+')
    currency_pattern = re.compile(r'[$,]')

    def search_movies(self, search_term):
        document = self.get_page(
            'https://www.boxofficemojo.com/search/',
            params={'q': search_term})
        return self.parse_search_results(document, search_term)

    def parse_search_results(self, document, search_term):
        raise NotImplementedError

    def get_box_office(self, movie_id):
        raise NotImplementedError

    # --- Helper methods ---

    def get_page(self, url, **kwargs):
        """Load and parse the HTML page at the given URL.

        Both relative and absolute URLs are supported. Relative URLs will be
        interpreted relative to https://www.boxofficemojo.com.
        """
        if not re.match(r'^https?://', url):
            url = urljoin('https://www.boxofficemojo.com', url)
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return bs4.BeautifulSoup(response.content, 'html.parser')

    def follow_link(self, document, link_text, parent_selector=None,):
        """Follow the link with the given text.

        This is a convenient shortcut for finding a link in the document and
        retrieving the page that it links to.

        The parent_selector argument is effectively a hint: if the specified
        element is present on the page, the query for the link will be
        restricted accordingly; if not, the entire page will be queried.
        """
        container = document

        if parent_selector:
            # Allow parent_selector to be either a standalone value or an
            # iterable collection of multiple values.
            if not hasattr(parent_selector, '__iter__'):
                parent_selector = (parent_selector,)

            # Look for a match within any of the given parent selectors: try
            # them one after another until finding a match.
            for selector in parent_selector:
                parent = container.select_one(selector)
                if parent:
                    container = parent
                    break

        link = container.find('a', text=link_text)
        return self.get_page(link['href'])

    def parse_date(self, value):
        """Parse just the date portion of some text.

        This method looks for something like "Jan 20, 2020" and ignores
        everything after that (to strip away names of holidays or other
        superfluous text).
        """
        match = self.date_pattern.match(value)
        if match:
            return match.group(0)
        return value

    def parse_int(self, value):
        """Parse a string representing a dollar amount into an integer.

        Essentially this just removes the leading '$' and any commas included
        for readability so that the value can be interpreted numerically.
        """
        try:
            return int(self.currency_pattern.sub('', value))
        except ValueError:
            return None


class LegacyBackend(Backend):
    def parse_search_results(self, document, search_term):
        movie_link_pattern = re.compile(r'/movies/\?id=([\w\-\.]+)')

        def movie_from_row(row):
            first_cell = row.select_one('td:nth-of-type(1)')
            if first_cell is None:
                return None, None

            movie_link = first_cell.find('a')
            if movie_link is None:
                return None, None

            movie_link_match = movie_link_pattern.search(movie_link['href'])
            if movie_link_match is None:
                return None, None

            return movie_link_match.group(1), first_cell.text.strip()

        results = []
        for row in document.find_all('tr'):
            movie_id, title = movie_from_row(row)
            if movie_id:
                # If there's a highlighted row, that's an exact match.
                results.append({
                    'movie_id': movie_id,
                    'title': title,
                    'exact': row['bgcolor'] == '#FFFF99'
                })

        return results

    def get_box_office(self, movie_id):
        url = 'https://www.boxofficemojo.com/movies/?' + urlencode({
            'id': movie_id,
            'page': 'daily',
            'view': 'chart'
        })
        document = self.get_page(url)

        title_match = re.search(r'(.*) - Daily Box Office Results',
                                document.title.text)
        if title_match is None:
            raise MovieNotFound(movie_id)

        result = {
            'title': title_match.group(1),
            'href': url,
            'box_office': []
        }

        chart = document.find(id='chart_container')

        if chart is None:
            return result

        table = chart.next_sibling
        rows = table.find_all('tr')

        box_office = result['box_office']

        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 10:
                continue

            day, date, rank, gross, _, _, theaters, _, cumulative = [
                cell.text for cell in cells[:9]]
            if not self.gross_pattern.match(gross):
                continue

            box_office.append({
                'day': day,
                'date': self.parse_date(date),
                'rank': self.parse_int(rank),
                'gross': self.parse_int(gross),
                'theaters': self.parse_int(theaters),
                'cumulative': self.parse_int(cumulative)
            })

        return result


class Dec2019Backend(Backend):
    def parse_search_results(self, document, search_term):
        movie_link_pattern = re.compile(r'/title/(\w+)')

        results = []
        for link in document.select('.titles a.a-size-medium'):
            movie_link_match = movie_link_pattern.search(link['href'])
            if movie_link_match is None:
                continue

            results.append({
                'movie_id': movie_link_match.group(1),
                'title': link.text,
                'exact': link.text.lower() == search_term.lower()
            })

        return results

    def get_box_office(self, movie_id):
        url = 'https://www.boxofficemojo.com/title/{}'.format(movie_id)
        landing_page = self.get_page(url)

        result = {
            'title': landing_page.find('h1').text,
            'href': url,
            'box_office': []
        }

        try:
            release_page = self.follow_link(landing_page, 'Original Release')
        except TypeError:
            # Handle the scenario where the landing page *is* the original
            # release page (might be the default for movies with only a single
            # release).
            release_page = landing_page

        box_office_page = self.follow_link(
            release_page, 'Domestic', parent_selector=('.releases-by-region',
                                                       '.mojo-body'))

        rows = box_office_page.select('#table tr')

        box_office = result['box_office']

        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 9:
                continue

            date, day, rank, gross, _, _, theaters, _, cumulative = [
                cell.text for cell in cells[:9]]
            if not self.gross_pattern.match(gross):
                continue

            box_office.append({
                'day': day,
                'date': self.parse_date(date),
                'rank': self.parse_int(rank),
                'gross': self.parse_int(gross),
                'theaters': self.parse_int(theaters),
                'cumulative': self.parse_int(cumulative)
            })

        return result


class June2022Backend(Dec2019Backend):
    def parse_search_results(self, document, search_term):
        movie_link_pattern = re.compile(r'/title/(\w+)')

        results = []

        # Search literally ALL links pointing to specific titles.
        for link in document.select('a'):
            movie_link_match = movie_link_pattern.search(link['href'])
            if movie_link_match is None:
                continue

            # Filter out links w/ no text (e.g. links from poster images)
            if not link.text:
                continue

            results.append({
                'movie_id': movie_link_match.group(1),
                'title': link.text,
                'exact': link.text.lower() == search_term.lower()
            })

        return results
