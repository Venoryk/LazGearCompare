import logging
from logging.handlers import RotatingFileHandler
from config.settings import LOG_FILE, LOG_MAX_BYTES, LOG_BACKUP_COUNT, LOG_FORMAT
from utils.decorators import debug_log

@debug_log
def setup_logging(debug_mode=False):
    """Configure logging with rotation
    
    Args:
        debug_mode: If True, sets logging level to DEBUG, otherwise INFO
    """
    try:
        # Configure file handler with rotation
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT
        )
        
        # Set formatter
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        
        # Add handler and set level
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        logging.debug("Logging setup complete")
        
    except Exception as e:
        logging.error(f"Failed to setup logging: {e}")
        raise