# core/data_manager.py
import logging
import json
import os
import csv
from datetime import datetime

from utils.decorators import debug_log
from utils.cache import CacheManager
from core.item_parser import ItemParser
from core.spell_parser import SpellParser

class DataManager:
    @debug_log
    def __init__(self):
        try:
            logging.debug("Initializing DataManager")
            self.cache_manager = CacheManager(
                cache_file='item_cache.json',
                cache_duration=24 * 60 * 60,
                is_item_cache=True,
                max_size_mb=10.0
            )
            self.spell_cache_manager = CacheManager(
                cache_file='spell_cache.json',
                cache_duration=24 * 60 * 60,
                is_item_cache=False
            )
            self.item_parser = ItemParser()
            self.spell_parser = SpellParser()
            logging.debug("DataManager initialization complete")
        except Exception as e:
            logging.error(f"Error initializing DataManager: {e}", exc_info=True)
            raise

    # Cache Management Methods
    @debug_log
    def get_cache_stats(self, cache_type='all'):
        """Get high-level statistics about cache contents"""
        try:
            if cache_type == 'all':
                logging.debug(f"Spell cache data: {self.spell_cache_manager.cache_data}")
                stats = {
                    'items': len(self.cache_manager.cache_data),
                    'spells': len(self.spell_cache_manager.cache_data),
                    'total': len(self.cache_manager.cache_data) + 
                            len(self.spell_cache_manager.cache_data)
                }
                logging.debug(f"Cache stats - Items: {stats['items']}, "
                                f"Spells: {stats['spells']}, Total: {stats['total']}")
                return stats
                
            # Individual cache stats
            current_time = datetime.now()
            cache = (self.cache_manager if cache_type == 'item' 
                    else self.spell_cache_manager)
            count = len(cache.cache_data)
            
            if count > 0:
                oldest = min(entry['timestamp'] for entry in cache.cache_data.values())
                age = (current_time - datetime.fromtimestamp(oldest)).total_seconds() / 3600
                logging.debug(f"{cache_type} cache: {count} entries, oldest: {age:.1f} hours")
                return count, age
            return count, 0
                        
        except Exception as e:
            logging.error(f"Error getting cache stats: {e}", exc_info=True)
            return {'items': 0, 'spells': 0, 'total': 0} if cache_type == 'all' else (0, 0)

    @debug_log
    def clear_spell_cache(self):
        """Clear spell cache and return success status and count"""
        try:
            cleared = self.spell_cache_manager.clear()
            logging.info(f"Cleared {cleared} spell cache entries")
            return True, cleared
        except Exception as e:
            logging.error(f"Error clearing spell cache: {e}", exc_info=True)
            return False, 0

    @debug_log
    def clear_item_cache(self):
        """Clear item cache and return success status and count"""
        try:
            cleared = self.cache_manager.clear()
            logging.info(f"Cleared {cleared} item cache entries")
            return True, cleared
        except Exception as e:
            logging.error(f"Error clearing item cache: {e}", exc_info=True)
            return False, 0

    @debug_log
    def clear_all_caches(self):
        """High-level operation to clear all caches"""
        try:
            items_cleared = self.cache_manager.clear()
            spells_cleared = self.spell_cache_manager.clear()
            
            results = {
                'items': items_cleared,
                'spells': spells_cleared,
                'total': items_cleared + spells_cleared
            }
            
            logging.info(f"Cleared {results['total']} total cache entries "
                        f"(Items: {results['items']}, Spells: {results['spells']})")
            
            return True, results
        except Exception as e:
            logging.error(f"Error clearing caches: {e}", exc_info=True)
            return False, {'items': 0, 'spells': 0, 'total': 0}

    # CSV File Operations
    @debug_log
    def check_duplicate_entry(self, filename, item_name):
        """Check if an item already exists in the CSV"""
        try:
            logging.debug(f"Checking for duplicate entry: {item_name} in {filename}")
            if os.path.exists(filename):
                logging.debug(f"CSV file found, searching for duplicate")
                with open(filename, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        if row.get('Name') == item_name:
                            logging.debug(f"Duplicate found for item: {item_name}")
                            return True
                logging.debug(f"No duplicate found for item: {item_name}")
            else:
                logging.debug(f"CSV file does not exist: {filename}")
            return False
        except Exception as e:
            logging.error(f"Error checking for duplicate entry: {e}", exc_info=True)
            return False

    @debug_log
    def save_item_to_csv(self, filename, item_data, slot, slot_order):
        """Save item data to CSV file"""
        try:
            logging.debug(f"Starting save operation for item: {item_data.get('Name', 'Unknown')} in slot: {slot}")
            
            # Read existing data and headers
            existing_data = []
            headers = set()
            if os.path.exists(filename):
                logging.debug(f"Reading existing CSV file: {filename}")
                with open(filename, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    headers = set(reader.fieldnames)
                    existing_data = list(reader)
                    logging.debug(f"Found {len(existing_data)} existing entries")

            # Update headers
            logging.debug("Updating headers with new item data")
            headers.add('Slot')
            headers.update(item_data.keys())
            ordered_headers = ['Slot'] + sorted(list(headers - {'Slot'}))
            logging.debug(f"Final header count: {len(ordered_headers)}")

            # Prepare new row
            logging.debug("Preparing new row data")
            new_row = {'Slot': slot}
            new_row.update(item_data)

            if 'URL' in new_row and 'ID' in new_row:
                new_row['URL'] = f"{new_row['URL']} "
                logging.debug("Added space after ID in URL")

            # Update data
            existing_data.append(new_row)
            logging.debug("Sorting data by slot order")
            existing_data.sort(key=lambda x: slot_order.get(x['Slot'], float('inf')))

            # Write to file
            logging.debug(f"Writing {len(existing_data)} entries to CSV")
            with open(filename, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=ordered_headers, quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                writer.writerows(existing_data)

            logging.info(f"Successfully saved data to {filename}")
            return True

        except Exception as e:
            logging.error(f"Failed to save to CSV: {e}", exc_info=True)
            return False