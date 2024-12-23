# utils/cache.py
import json
import os
import logging
import time
from typing import Dict, Any, Optional, Tuple
from utils.decorators import debug_log
from CTkMessagebox import CTkMessagebox

class CacheManager:
    """Manages caching operations with size limits and duration controls"""
    
    def __init__(self, cache_file: str, cache_duration: int = 24 * 60 * 60,
                is_item_cache: bool = False, max_size_mb: float = 100.0):
        logging.debug(f"Initializing CacheManager for {cache_file}")
        self.cache_file = cache_file
        self.cache_duration = cache_duration
        self.cache_data: Dict[str, Any] = {}
        self.is_item_cache = is_item_cache
        if is_item_cache:
            self.max_size_bytes = max_size_mb * 1024 * 1024
            logging.debug(f"Item cache initialized with {max_size_mb}MB limit")
        
        # Ensure cache file exists
        if not os.path.exists(self.cache_file):
            logging.debug(f"Creating new cache file: {self.cache_file}")
            self.save_cache()  # This will create the file with empty cache
        else:
            self.load_cache()
        
        logging.debug("CacheManager initialization complete")

    # Cache Size Management
    @debug_log
    def get_item_cache_size(self) -> Optional[Tuple[float, bool]]:
        """Get current cache size and check if it exceeds limit"""
        if not self.is_item_cache:
            logging.debug("Size check skipped - not an item cache")
            return None
            
        try:
            if os.path.exists(self.cache_file):
                size_bytes = os.path.getsize(self.cache_file)
                size_mb = size_bytes / (1024 * 1024)
                is_exceeded = size_bytes > self.max_size_bytes
                logging.debug(f"Cache size: {size_mb:.2f}MB, Limit exceeded: {is_exceeded}")
                return size_mb, is_exceeded
            logging.debug("Cache file does not exist")
            return 0.0, False
        except Exception as e:
            logging.error(f"Error getting cache size: {e}", exc_info=True)
            return 0.0, False

    @debug_log
    def check_item_cache_size(self) -> bool:
        """Check cache size and show warning if exceeded"""
        if not self.is_item_cache:
            return False
            
        size_info = self.get_item_cache_size()
        if size_info and size_info[1]:
            logging.warning(f"Cache size ({size_info[0]:.2f}MB) exceeds limit ({self.max_size_bytes/1024/1024:.2f}MB)")
            msg = (f"Item cache size ({size_info[0]:.2f}MB) exceeds "
                  f"recommended limit ({self.max_size_bytes/1024/1024:.2f}MB).")
            response = CTkMessagebox(
                title="Cache Size Warning",
                message=f"{msg}\nWould you like to clear it?",
                icon="warning",
                option_1="Yes",
                option_2="No"
            ).get()
            logging.debug(f"User response to cache clear prompt: {response}")
            return response == "Yes"
        return False

    # Cache Operations
    @debug_log
    def get(self, key: str) -> Any:
        """Get item from cache with expiration check"""
        key = key.lower()
        if key in self.cache_data:
            cached_item = self.cache_data[key]
            current_time = time.time()
            age = current_time - cached_item['timestamp']
            
            if age < self.cache_duration:
                logging.debug(f"Cache hit for: {key} (age: {age:.1f}s)")
                return cached_item['data']
            else:
                logging.debug(f"Cache expired for: {key} (age: {age:.1f}s)")
                del self.cache_data[key]
        else:
            logging.debug(f"Cache miss for: {key}")
        return None

    @debug_log
    def set(self, key: str, value: Any) -> None:
        """Set cache value and check size limits"""
        key = key.lower()
        logging.debug(f"Caching item: {key}")
        self.cache_data[key] = {
            'data': value,
            'timestamp': time.time()
        }
        self.save_cache()
        
        if self.is_item_cache:
            if self.check_item_cache_size():
                logging.info("Cache size limit exceeded, clearing cache")
                self.clear()

    # Cache File Operations
    @debug_log
    def clear(self) -> int:
        """Clear cache and remove cache file"""
        cache_size = len(self.cache_data)
        logging.info(f"Clearing cache containing {cache_size} items")
        
        try:
            # Clear the cache data
            self.cache_data.clear()
            
            # Create empty cache file
            self.save_cache()
            logging.info("Cache cleared and empty file created")
                
            return cache_size
            
        except Exception as e:
            logging.error(f"Error clearing cache: {e}", exc_info=True)
            return 0

    @debug_log
    def load_cache(self) -> None:
        """Load cache from file"""
        try:
            if os.path.exists(self.cache_file):
                logging.debug(f"Loading cache from: {self.cache_file}")
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
                logging.info(f"Successfully loaded {len(self.cache_data)} cached items")
            else:
                logging.debug("No cache file found, initializing empty cache")
                self.cache_data = {}
        except Exception as e:
            logging.error(f"Error loading cache: {e}", exc_info=True)
            self.cache_data = {}

    def save_cache(self) -> None:
        """Save cache to file"""
        try:
            logging.debug(f"Saving {len(self.cache_data)} items to cache file")
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f)
            logging.info(f"Successfully saved {len(self.cache_data)} items to cache")
        except Exception as e:
            logging.error(f"Error saving cache: {e}", exc_info=True)