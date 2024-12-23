# core/item_parser.py
import logging
import re
from bs4 import BeautifulSoup
import lxml
import lxml.etree

from config.constraints import STAT_CATEGORIES, STAT_REPLACEMENTS
from utils.decorators import debug_log
from core.spell_parser import SpellParser
from utils.web import WebUtils

class ItemParser:
    def __init__(self):
        logging.debug("Initializing ItemParser")
        self.stat_categories = STAT_CATEGORIES
        self.spell_parser = SpellParser()
        self.web_utils = WebUtils()
        logging.debug("ItemParser initialization complete")

    # Item Processing Methods
    @debug_log
    def process_similar_items(self, html_content):
        """Process similar items from search results"""
        try:
            logging.debug("Processing similar items from search results")
            similar_items = []
            
            soup = self.web_utils.parse_html(html_content)
            tables = soup.find_all('table')
            
            if len(tables) >= 2:
                logging.debug(f"Found {len(tables)} tables in search results")
                for row in tables[1].find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        name_cell = cells[2]
                        item_link = name_cell.find('a')
                        if item_link:
                            item_name = item_link.text.strip()
                            similar_items.append(item_name)
                            logging.debug(f"Found similar item: {item_name}")
                
                logging.info(f"Found {len(similar_items)} similar items")
                return similar_items
            else:
                logging.warning("No similar items found in search results")
                return []
                
        except Exception as e:
            logging.error(f"Error processing similar items: {e}", exc_info=True)
            return []

    # Item ID Extraction
    @debug_log
    def extract_item_id(self, html_content, search_name):
        """Extract item ID from search results with exact name matching"""
        try:
            logging.debug(f"Attempting to parse HTML for item: {search_name}")
            try:
                soup = BeautifulSoup(html_content, 'lxml')
                logging.debug("Successfully parsed HTML with lxml")
            except lxml.etree.ParserError as e:
                logging.error(f"LXML parsing error in extract_item_id: {e}", exc_info=True)
                logging.debug("Falling back to html.parser")
                soup = BeautifulSoup(html_content, 'html.parser')
            
            tables = soup.find_all('table')
            logging.debug(f"Found {len(tables)} tables in search results")
            
            if len(tables) >= 2:
                result_rows = tables[1].find_all('tr')
                logging.debug(f"Processing {len(result_rows)} rows in results table")
                
                for row in result_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        item_id = cells[0].text.strip()
                        name_cell = cells[2]
                        item_link = name_cell.find('a')
                        if item_link:
                            item_name = item_link.text.strip()
                            logging.debug(f"Comparing '{item_name.lower()}' with '{search_name.lower()}'")
                            if item_name.lower() == search_name.lower():
                                logging.info(f"Found exact match! ID: {item_id} for item: {item_name}")
                                return item_id
                
                logging.warning(f"No exact name match found for: {search_name}")
            else:
                logging.warning("Could not find results table in HTML content")
            
        except Exception as e:
            logging.error(f"Error extracting item ID: {e}", exc_info=True)
        
        return None
    
    # Item Stats Extraction
    @debug_log
    def extract_item_stats(self, html_content):
        """Extract all item stats from the HTML content"""
        try:
            logging.debug("Starting item stats extraction")
            try:
                soup = BeautifulSoup(html_content, 'lxml')
                logging.debug("Successfully parsed HTML with lxml")
            except lxml.etree.ParserError as e:
                logging.error(f"LXML parsing error in extract_item_stats: {e}", exc_info=True)
                logging.debug("Falling back to html.parser")
                soup = BeautifulSoup(html_content, 'html.parser')

            stats = {}
            
            # Extract item name
            logging.debug("Extracting item name")
            item_name = None
            for heading in soup.find_all(['h2', 'h1', 'strong']):
                text = heading.text.strip()
                if text and not any(ignore in text.lower() for ignore in ['search', 'result', 'menu', 'navigation']):
                    item_name = text
                    logging.debug(f"Found item name: {item_name}")
                    break

            stats['Name'] = item_name or "Unknown Item"
            logging.debug(f"Set item name in stats: {stats['Name']}")

            # Get all text from item details
            logging.debug("Extracting item details text")
            item_details = soup.get_text()
            item_details = re.sub(r'Value:\s*[-+]?\d+', '', item_details)
            
            # Process basic patterns
            logging.debug("Processing basic stat patterns")
            self._process_basic_stats(item_details, stats)
            
            # Process remaining stats
            logging.debug("Processing remaining stats")
            self._process_remaining_stats(item_details, stats)

            # Process augmentation slots
            logging.debug("Processing augmentation slots")
            self._process_augmentation_slots(item_details, stats)
            
            # Process effects
            logging.debug("Processing item effects")
            self._process_effects(soup, stats)

            logging.info(f"Successfully extracted {len(stats)} stats for item: {stats.get('Name', 'Unknown')}")
            return stats

        except Exception as e:
            logging.error(f"Error in extract_item_stats: {e}", exc_info=True)
            return {}

    # Stat Processing Methods
    @debug_log
    def _process_basic_stats(self, item_details, stats):
        """Process basic item stats"""
        try:
            basic_patterns = [
                r'Type:\s*(\w+)',
                r'Armor Class:\s*([-]?\d+)',
                r'Health:\s*([-]?\d+)',
                r'Mana:\s*([-]?\d+)',
                r'Endurance:\s*([-]?\d+)',
                r'Slot\s+(\d+):\s*Type\s+(\d+)',
            ]

            for pattern in basic_patterns:
                match = re.search(pattern, item_details, re.IGNORECASE)
                if match:
                    if 'Type:' in pattern:
                        type_match = re.search(r'Type:\s*([a-zA-Z0-9\s]+?(?=\s*[A-Z]$|Armor))', 
                                             item_details, re.IGNORECASE)
                        if type_match:
                            stats['Type'] = type_match.group(1)
                            logging.debug(f"Found item type: {stats['Type']}")
                    else:
                        stat_name = pattern.split(r':\s*')[0].replace(r'\s*', '')
                        stat_name = self.normalize_stat_name(stat_name)
                        stats[stat_name] = self.clean_stat_value(match.group(1))
                        logging.debug(f"Found basic stat: {stat_name}={stats[stat_name]}")

        except Exception as e:
            logging.error(f"Error processing basic stats: {e}", exc_info=True)

    @debug_log
    def _process_remaining_stats(self, item_details, stats):
        """Process remaining stats like attributes, resists, etc."""
        try:
            # Process damage stats
            logging.debug("Processing damage stats")
            damage_match = re.search(r'(Bash|Kick|Flying Kick|Backstab|Dragon Punch|Eagle Strike|Round Kick|Tiger Claw|Frenzy) Damage:\s*(\d+)', 
                                   item_details, re.IGNORECASE)
            if damage_match:
                damage_type = damage_match.group(1).upper()
                damage_amount = damage_match.group(2)
                stats[f"{damage_type} DAMAGE"] = damage_amount
                logging.debug(f"Found damage stat: {damage_type} = {damage_amount}")

            # Process skill modifiers
            logging.debug("Processing skill modifiers")
            skill_mod_pattern = (
                r'Skill Modifier:\s*'
                r'(Backstab|Dragon Punch|Eagle Strike|Flying Kick|Kick|Round Kick|'
                r'Tiger Claw|Frenzy|Safe Fall|Pick Lock|Begging|Sneak|Intimidation|'
                r'Forage|Tracking)\s*\((\d+)%\)'
            )
            for match in re.finditer(skill_mod_pattern, item_details, re.IGNORECASE):
                skill_name = match.group(1).upper()
                if skill_name == "BACKSTAB":
                    skill_name = "BACKSTAB_MOD"
                skill_value = f"{match.group(2)}%"
                stats[skill_name] = skill_value
                logging.debug(f"Found skill modifier: {skill_name} = {skill_value}")

            # Process bard skills
            logging.debug("Processing bard skills")
            bard_skill_pattern = (
                r'Bard Skill:\s*'
                r'(Brass Instruments|Strings Instruments|Percussion Instruments|'
                r'Wind Instruments|Unknown \(50\)|All Instruments)\s*\((\d+)%\)'
            )
            for match in re.finditer(bard_skill_pattern, item_details, re.IGNORECASE):
                skill_name = match.group(1).upper()
                skill_name = skill_name.replace("UNKNOWN (50)", "SINGING RESONANCE")
                skill_value = f"{match.group(2)}%"
                stats[f"BARD_{skill_name}"] = skill_value
                logging.debug(f"Found bard skill: {skill_name} = {skill_value}")

            # Process attributes and resists
            logging.debug("Processing attributes and resists")
            attribute_resist_patterns = [
                r'(Strength|Stamina|Agility|Dexterity|Wisdom|Intelligence|Charisma):\s*([-]?\d+)(?:\s*\+(\d+))?',
                r'(Poison|Magic|Disease|Fire|Cold|Corrupt(?:ion)?):\s*([-]?\d+)(?:\s*\+(\d+))?'
            ]

            for pattern in attribute_resist_patterns:
                for match in re.finditer(pattern, item_details, re.IGNORECASE):
                    stat_name = self.normalize_stat_name(match.group(1))
                    base_value = match.group(2)
                    heroic_value = match.group(3)
                    
                    if heroic_value:
                        stats[stat_name] = f"{base_value} +{heroic_value}"
                    else:
                        stats[stat_name] = base_value
                    logging.debug(f"Found attribute/resist: {stat_name} = {stats[stat_name]}")

            # Process additional stats
            logging.debug("Processing additional stats")
            additional_patterns = [
                # Handle shield stats first
                r'(Damage\s+Shield(?:\s+Mitig)?)\s*:\s*([-+]?\d+)',
                # Handle standalone Damage with exclusions
                r'(?<!\w\s)(Damage)(?!\s+\w):\s*([-+]?\d+)',
                # Other weapon stats
                r'(Backstab|Delay|Bonus|Range):\s*([-+]?\d+)',
                # Offensive stats
                r'(Attack|Haste|Accuracy|Strikethrough):\s*([-+]?\d+)',
                # Magic stats
                r'(Spell Damage|Combat Effects):\s*([-+]?\d+)',
                # Defensive stats
                r'(Avoidance|Shielding|Spell Shielding|DoT Shielding|Damage Shield Mitig|Defense|Stun Resist):\s*([-+]?\d+)',
                # Regeneration
                r'(HP Regen|Mana Regen|Endurance Regen|Meditate):\s*([-+]?\d+)',
                # Combat abilities
                r'(Dodge|Parry|Riposte|Triple Attack|Double Attack):\s*([-+]?\d+)',
                # Weapon types/skills
                r'(Hand to Hand|1H Blunt|1H Slashing|2H Blunt|2H Slashing|1H Piercing|2H Piercing|Throwing):\s*([-+]?\d+)',
            ]

            for pattern in additional_patterns:
                for match in re.finditer(pattern, item_details, re.IGNORECASE):
                    stat_name = self.normalize_stat_name(match.group(1))
                    value = match.group(2)
                    
                    # Remove duplicate 'EFFECT' words if present
                    stat_name = re.sub(r'EFFECT\s+EFFECT', 'EFFECT', stat_name)
                    
                    # Store the stat without adding 'EFFECT'
                    stats[stat_name] = self.clean_stat_value(value)
                    logging.debug(f"Found additional stat: {stat_name} = {stats[stat_name]}")

            logging.debug("Completed processing remaining stats")

            # Process magic skills
            logging.debug("Processing magic skills")
            magic_skill_pattern = r'(Channeling|Abjuration|Conjuration|Divination|Evocation|Alteration):\s*(\d+)'
            for match in re.finditer(magic_skill_pattern, item_details, re.IGNORECASE):
                skill_name = match.group(1).upper()
                skill_value = match.group(2)
                stats[skill_name] = skill_value
                logging.debug(f"Found magic skill: {skill_name} = {skill_value}")

            # Process spell specializations
            logging.debug("Processing spell specializations")
            spec_pattern = r'(Specialize (?:Alteration|Conjuration|Abjuration|Evocation|Divination)):\s*(\d+)'
            for match in re.finditer(spec_pattern, item_details, re.IGNORECASE):
                skill_name = match.group(1).upper()
                skill_value = match.group(2)
                stats[skill_name] = skill_value
                logging.debug(f"Found specialization: {skill_name} = {skill_value}")

            # Process tradeskills
            tradeskill_pattern = r'(Alchemy|Baking|Blacksmithing|Brewing|Fishing|Fletching|Jewelry Making|Make Poison|Pottery|Research|Tailoring|Tinkering):\s*(\d+)'
            for match in re.finditer(tradeskill_pattern, item_details, re.IGNORECASE):
                skill_name = match.group(1).upper()
                skill_value = match.group(2)
                stats[skill_name] = skill_value
                logging.debug(f"Found tradeskill: {skill_name} = {skill_value}")

        except Exception as e:
            logging.error(f"Error processing remaining stats: {e}", exc_info=True)

    @debug_log
    def _process_effects(self, soup, stats):
        """Process item effects (Focus, Worn, Proc, Click)"""
        try:
            logging.debug("Starting effects processing")
            effect_labels = ['Focus Effect', 'Worn Effect', 'Proc Effect', 'Click Effect']
            
            for label in effect_labels:
                logging.debug(f"Processing {label}")
                td_elements = soup.find_all('td', {'colspan': '2'})
                
                for td in td_elements:
                    effect_b = td.find('b', string=re.compile(f"^{label}:"))
                    if effect_b:
                        logging.debug(f"Found {label} element")
                        effect_link = td.find('a')
                        if effect_link:
                            spell_name = effect_link.text.strip()
                            spell_url = effect_link.get('href', '')
                            logging.debug(f"Found effect: {label} - {spell_name}")
                            
                            # Extract cast time from the same td element
                            cast_time_match = re.search(r'\(Cast Time:\s*([\d.]+\s*\w+)\)', td.get_text())
                            cast_time = cast_time_match.group(1) if cast_time_match else None
                            
                            # Extract charges from the same td element
                            charges_match = re.search(r'Charges:\s*(\w+)', td.get_text())
                            charges = charges_match.group(1) if charges_match else None
                            
                            spell_id_match = re.search(r'id=(\d+)', spell_url)
                            if spell_id_match:
                                spell_id = spell_id_match.group(1)
                                logging.debug(f"Found spell ID: {spell_id}")
                                
                                spell_details = self.spell_parser.extract_spell_details(spell_name, spell_id)
                                if spell_details:
                                    # Add cast time and charges from item page
                                    if cast_time:
                                        spell_details['cast_time'] = cast_time
                                        logging.debug(f"Added cast time: {cast_time}")
                                    if charges:
                                        spell_details['charges'] = charges
                                        logging.debug(f"Added charges: {charges}")
                                        
                                    stats[f"{label.upper()}_DETAILS"] = spell_details
                                    logging.debug(f"Added spell details for {label}")
            
            logging.debug("Completed effects processing")
            
        except Exception as e:
            logging.error(f"Error processing effects: {e}", exc_info=True)

    @debug_log
    def _process_augmentation_slots(self, item_details, stats):
        """Process augmentation slots and their types"""
        try:
            logging.debug("Processing augmentation slots")
            aug_pattern = r'Slot\s+(\d+):\s*Type\s+(\d+)'
            
            for match in re.finditer(aug_pattern, item_details, re.IGNORECASE):
                slot_num = match.group(1)
                slot_type = match.group(2)
                stats[f'SLOT {slot_num}'] = f'Type {slot_type}'
                logging.debug(f"Found augmentation slot: Slot {slot_num} = Type {slot_type}")
                
        except Exception as e:
            logging.error(f"Error processing augmentation slots: {e}", exc_info=True)

    # Utility Methods
    @debug_log
    def normalize_stat_name(self, stat_name):
        """Normalize stat names to standard format"""
        try:
            logging.debug(f"Normalizing stat name: {stat_name}")
            # Remove special characters and convert to uppercase
            stat_name = re.sub(r'[^a-zA-Z0-9\s]', '', stat_name).strip().upper()
            normalized = STAT_REPLACEMENTS.get(stat_name, stat_name)
            logging.debug(f"Normalized '{stat_name}' to '{normalized}'")
            return normalized
        except Exception as e:
            logging.error(f"Error normalizing stat name: {e}", exc_info=True)
            return stat_name

    @debug_log
    def clean_stat_value(self, value):
        """Clean up stat values by removing unwanted characters and formatting"""
        try:
            logging.debug(f"Cleaning stat value: {value}")
            # Remove asterisks and extra spaces
            value = re.sub(r'\*+', '', str(value)).strip()
            
            # If the value already ends with %, return it as is
            if value.endswith('%'):
                logging.debug(f"Percentage value found: {value}")
                return value
                
            # Extract numeric values if present
            numeric_match = re.search(r'[-+]?\d+', value)
            if numeric_match:
                cleaned = numeric_match.group()
                logging.debug(f"Extracted numeric value: {cleaned}")
                return cleaned
                
            logging.debug(f"Returning cleaned value: {value}")
            return value
        except Exception as e:
            logging.error(f"Error cleaning stat value: {e}", exc_info=True)
            return value
        
    # Display Formatting Methods
    @debug_log
    def format_stat_with_heroic(self, value):
        """Format stat value with heroic bonus if present"""
        try:
            if isinstance(value, str) and '+' in value:
                base, heroic = value.split('+')
                return f"{base.strip()} (+{heroic.strip()})"
            return value
        except Exception as e:
            logging.error(f"Error formatting stat with heroic: {e}", exc_info=True)
            return value