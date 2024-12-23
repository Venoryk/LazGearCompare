# core/spell_parser.py
from utils.web import WebUtils
import logging
import re
from bs4 import BeautifulSoup
import lxml
import lxml.etree
from utils.decorators import debug_log

class SpellParser:
    def __init__(self):
        logging.debug("Initializing SpellParser")
        self.web_utils = WebUtils()
        self.debug_var = None
        logging.debug("SpellParser initialization complete")

    # Primary Spell Processing
    @debug_log
    def extract_spell_details(self, spell_name, spell_id=None):
        """Extract detailed spell information with caching"""
        
        try:
            if not spell_id:
                search_url = self.web_utils.format_spell_search_url(spell_name)
                response = self.web_utils.get_page_content(search_url)
                spell_id = self.extract_spell_id(response, spell_name)
                if not spell_id:
                    logging.warning(f"No spell ID found for: {spell_name}")
                    return None

            spell_url = self.web_utils.format_spell_details_url(spell_id)
            response = self.web_utils.get_page_content(spell_url)
            logging.debug(f"Retrieved spell page for ID: {spell_id}")
            
            try:
                soup = BeautifulSoup(response, 'lxml')
                logging.debug("Successfully parsed HTML with lxml")
            except lxml.etree.ParserError as e:
                logging.error(f"LXML parsing error: {e}", exc_info=True)
                soup = BeautifulSoup(response, 'html.parser')

            spell_details = {
                'name': spell_name,
                'id': spell_id,
                'url': spell_url,
                'effects': []
            }

            # Find the effects section header
            effects_header = soup.find('h2', class_='section_header', string='Effects')
            if effects_header:
                logging.debug("Found Effects header")
                # Find all tr elements that follow the Effects header
                current = effects_header
                while current:
                    current = current.find_next(['tr', 'table'])
                    if current and current.name == 'tr':
                        cells = current.find_all('td')
                        if len(cells) == 2:
                            first_cell = cells[0]
                            bold = first_cell.find('b')
                            if bold and 'Effect' in bold.get_text():
                                # Extract effect number
                                effect_num = re.search(r'Effect\s+(\d+)', bold.get_text())
                                effect_text = cells[1].get_text(strip=True)
                                if effect_num:
                                    # Format with effect number
                                    formatted_effect = f"{effect_num.group(1)}: {effect_text}"
                                    spell_details['effects'].append(formatted_effect)
                                    logging.debug(f"Found effect: {formatted_effect}")
                    elif current and current.name == 'table':
                        break

            # Look for charges
            charges_td = soup.find('td', string=lambda x: x and 'Charges:' in x)
            if charges_td:
                charges_text = charges_td.get_text(strip=True)
                charges_match = re.search(r'Charges:\s*(\w+)', charges_text)
                if charges_match:
                    spell_details['charges'] = charges_match.group(1)
                    logging.debug(f"Found charges: {charges_match.group(1)}")

            # Look for cast time
            cast_td = soup.find('td', string=lambda x: x and 'Cast Time:' in x)
            if cast_td:
                cast_text = cast_td.get_text(strip=True)
                cast_match = re.search(r'Cast Time:\s*([\d.]+\s*\w+)', cast_text)
                if cast_match:
                    spell_details['cast_time'] = cast_match.group(1)
                    logging.debug(f"Found cast time: {cast_match.group(1)}")

            return spell_details

        except Exception as e:
            logging.error(f"Error extracting spell details: {e}", exc_info=True)
            return None

    # HTML Parsing Methods
    @debug_log
    def extract_spell_id(self, html_content, spell_name):
        """Extract spell ID from the search results page"""
        try:
            logging.debug(f"Attempting to extract spell ID for: {spell_name}")
            try:
                soup = BeautifulSoup(html_content, 'lxml')
                logging.debug("Successfully parsed HTML with lxml")
            except lxml.etree.ParserError as e:
                logging.error(f"LXML parsing error in extract_spell_id: {e}", exc_info=True)
                logging.debug("Falling back to html.parser")
                soup = BeautifulSoup(html_content, 'html.parser')
            
            tables = soup.find_all('table')
            logging.debug(f"Found {len(tables)} tables")
            
            # Look for exact match first
            logging.debug("Searching for exact spell name match")
            for table in tables:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        cell_text = cells[1].get_text(strip=True)
                        link = cells[1].find('a')
                        if link and cell_text.lower() == spell_name.lower():
                            spell_id = re.search(r'id=(\d+)', link['href'])
                            if spell_id:
                                logging.debug(f"Found exact match spell ID: {spell_id.group(1)}")
                                return spell_id.group(1)
                
            # If no exact match, look for partial match
            logging.debug("No exact match found, searching for partial match")
            for table in tables:
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        cell_text = cells[1].get_text(strip=True)
                        link = cells[1].find('a')
                        if link and spell_name.lower() in cell_text.lower():
                            spell_id = re.search(r'id=(\d+)', link['href'])
                            if spell_id:
                                logging.debug(f"Found partial match spell ID: {spell_id.group(1)}")
                                return spell_id.group(1)
            
            logging.warning(f"No spell ID found for: {spell_name}")
            return None
            
        except Exception as e:
            logging.error(f"Error extracting spell ID: {e}", exc_info=True)
            return None

    @debug_log
    def extract_spell_basic_info(self, info_section):
        """Extract basic spell information from the info section"""
        try:
            logging.debug("Starting basic spell info extraction")
            basic_info = {}
            
            rows = info_section.find_all('tr')
            logging.debug(f"Found {len(rows)} rows in info section")
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 2:
                    key = cells[0].text.strip().rstrip(':')
                    value = cells[1].text.strip()
                    basic_info[key] = value
                    logging.debug(f"Extracted {key}: {value}")
                    
            logging.debug(f"Completed basic info extraction with {len(basic_info)} fields")
            return basic_info
            
        except Exception as e:
            logging.error(f"Error extracting basic spell info: {e}", exc_info=True)
            return {}
        
    # Effect Processing Methods
    @debug_log
    def process_spell_effects(self, soup):
        """Process spell effects from HTML soup"""
        try:
            effects = []
            effects_header = soup.find('h2', class_='section_header', string='Effects')
            
            if effects_header:
                logging.debug("Found Effects header")
                current = effects_header
                while current:
                    current = current.find_next(['tr', 'table'])
                    if current and current.name == 'tr':
                        cells = current.find_all('td')
                        if len(cells) == 2:
                            first_cell = cells[0]
                            bold = first_cell.find('b')
                            if bold and 'Effect' in bold.get_text():
                                effect_num = re.search(r'Effect\s+(\d+)', bold.get_text())
                                effect_text = cells[1].get_text(strip=True)
                                if effect_num:
                                    formatted_effect = f"{effect_num.group(1)}: {effect_text}"
                                    effects.append(formatted_effect)
                                    logging.debug(f"Found effect: {formatted_effect}")
                    elif current and current.name == 'table':
                        break
                        
            return effects
        except Exception as e:
            logging.error(f"Error processing spell effects: {e}", exc_info=True)
            return []

    # Display Formatting Methods
    @debug_log
    def format_effect_display(self, effect_details):
        """Format effect details for display
        
        Args:
            effect_details (dict): Dictionary containing effect information
                
        Returns:
            tuple: (display_name, additional_details)
        """
        try:
            if not effect_details:
                logging.debug("No effect details to format")
                return "", ""
                
            # Just the name for the hyperlink
            display_name = effect_details.get('name', 'Unknown Effect')
            additional_details = ""
            
            # Format cast time on same line, charges on next line
            if 'cast_time' in effect_details:
                additional_details += f" (Cast Time: {effect_details['cast_time']})"
                
            if 'charges' in effect_details:
                additional_details += f"\nCharges: {effect_details['charges']}"
                
            logging.debug(f"Formatted effect display for: {display_name}")
            return display_name, additional_details
                
        except Exception as e:
            logging.error(f"Error formatting effect display: {e}", exc_info=True)
            return "Error formatting effect", ""

    # Cache Management Methods
