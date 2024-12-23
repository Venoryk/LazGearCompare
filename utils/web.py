# utils/web.py
import requests
import logging
import urllib3
import urllib.parse
from bs4 import BeautifulSoup
import lxml
import lxml.etree
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from utils.decorators import debug_log

# Disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebUtils:
    # Initialization
    def __init__(self):
        logging.debug("Initializing WebUtils")
        self.session = self.create_session()
        self.debug_var = None
        logging.debug("WebUtils initialized successfully")

    # Session Management Methods
    @debug_log
    def create_session(self):
        """Create requests session with retries"""
        try:
            logging.debug("Creating requests session with retry configuration")
            session = requests.Session()
            retries = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
            logging.debug(f"Retry configuration: total=3, backoff=0.5, status_forcelist={[500, 502, 503, 504]}")
            
            session.mount('http://', HTTPAdapter(max_retries=retries))
            session.mount('https://', HTTPAdapter(max_retries=retries))
            logging.debug("Session created with retry configuration")
            return session
        except Exception as e:
            logging.error(f"Failed to create session: {e}", exc_info=True)
            raise

    # URL Formatting Methods
    @debug_log
    def format_search_url(self, item_name):
        """Format the item name for the URL and return the complete search URL"""
        try:
            logging.debug(f"Formatting search URL for item: {item_name}")
            cleaned_name = re.sub(r'[^\w\s\-\'\+]', '', item_name).strip()
            logging.debug(f"Cleaned name: {cleaned_name}")
            
            encoded_name = urllib.parse.quote(cleaned_name)
            logging.debug(f"URL encoded name: {encoded_name}")
            
            url = f"https://www.lazaruseq.com/Alla/?a=items_search&&a=items&iname={encoded_name}&isearch=1"
            logging.debug(f"Generated search URL: {url}")
            return url
        except Exception as e:
            logging.error(f"Failed to format search URL: {e}", exc_info=True)
            raise

    @debug_log
    def format_item_url(self, item_id):
        """Format the URL for specific item details"""
        try:
            logging.debug(f"Formatting item URL for ID: {item_id}")
            url = f"https://www.lazaruseq.com/Alla/?a=item&id={item_id}"
            logging.debug(f"Generated item URL: {url}")
            return url
        except Exception as e:
            logging.error(f"Failed to format item URL: {e}", exc_info=True)
            raise

    @debug_log
    def format_spell_search_url(self, spell_name):
        """Format the spell name for URL and return the complete search URL"""
        try:
            logging.debug(f"Formatting spell search URL for: {spell_name}")
            formatted_name = urllib.parse.quote(spell_name)
            logging.debug(f"URL encoded spell name: {formatted_name}")
            
            url = f"https://www.lazaruseq.com/Alla/?a=spells&name={formatted_name}&type=0&level=&opt=2"
            logging.debug(f"Generated spell search URL: {url}")
            return url
        except Exception as e:
            logging.error(f"Failed to format spell search URL: {e}", exc_info=True)
            raise

    @debug_log
    def format_spell_details_url(self, spell_id):
        """Format the URL for specific spell details"""
        try:
            logging.debug(f"Formatting spell details URL for ID: {spell_id}")
            url = f"https://www.lazaruseq.com/Alla/?a=spell&id={spell_id}"
            logging.debug(f"Generated spell details URL: {url}")
            return url
        except Exception as e:
            logging.error(f"Failed to format spell details URL: {e}", exc_info=True)
            raise

    # Content Retrieval Methods
    @debug_log
    def get_page_content(self, url):
        """Get page content with specific headers and SSL verification disabled"""
        try:
            logging.debug(f"Fetching content from URL: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            logging.debug("Making request with headers and SSL verification disabled")
            
            response = self.session.get(url, headers=headers, verify=False)
            logging.debug(f"Response status code: {response.status_code}")
            
            if response.status_code != 200:
                logging.warning(f"Unexpected status code: {response.status_code}")
                
            return response.text
        except requests.exceptions.ConnectionError as e:
            logging.error(f"Connection error: {e}", exc_info=True)
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}", exc_info=True)
            raise

    @debug_log
    def parse_html(self, html_content):
        """Parse HTML content with fallback to html.parser if lxml fails"""
        try:
            logging.debug("Attempting to parse HTML content with lxml")
            return BeautifulSoup(html_content, 'lxml')
        except lxml.etree.ParserError as e:
            logging.error(f"LXML parsing error: {e}", exc_info=True)
            logging.debug("Falling back to html.parser")
            return BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            logging.error(f"HTML parsing error: {e}", exc_info=True)
            raise

    # Search Results Processing Methods
    @debug_log
    def search_item(self, item_name):
        """Search for an item and return search results"""
        try:
            logging.debug(f"Searching for item: {item_name}")
            search_url = self.format_search_url(item_name)
            content = self.get_page_content(search_url)
            soup = self.parse_html(content)
            
            return self._parse_search_results(soup)
        except Exception as e:
            logging.error(f"Failed to search for item: {e}", exc_info=True)
            raise

    @debug_log
    def _parse_search_results(self, soup):
        """Parse search results from HTML soup"""
        try:
            logging.debug("Parsing search results")
            results = []
            table = soup.find('table', {'class': 'items'})
            
            if not table:
                logging.debug("No results table found")
                return results

            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    item_link = cells[1].find('a')
                    if item_link:
                        item_id = re.search(r'id=(\d+)', item_link['href'])
                        if item_id:
                            results.append({
                                'id': item_id.group(1),
                                'name': item_link.text.strip(),
                                'url': self.format_item_url(item_id.group(1))
                            })

            logging.debug(f"Found {len(results)} search results")
            return results
        except Exception as e:
            logging.error(f"Failed to parse search results: {e}", exc_info=True)
            raise

    # Similar Items Processing Methods
    @debug_log
    def get_similar_items(self, item_name):
        """Get list of similar items based on name"""
        try:
            logging.debug(f"Finding similar items for: {item_name}")
            search_results = self.search_item(item_name)
            
            # Filter results to find similar items
            similar_items = []
            for result in search_results:
                if result['name'].lower() != item_name.lower():
                    similar_items.append(result)
                    
            logging.debug(f"Found {len(similar_items)} similar items")
            return similar_items
        except Exception as e:
            logging.error(f"Failed to get similar items: {e}", exc_info=True)
            raise