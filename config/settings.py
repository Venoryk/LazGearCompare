# config/settings.py

# Logging settings
LOG_FILE = 'eq_gear_debug.log'
LOG_MAX_BYTES = 1024 * 1024  # 1MB
LOG_BACKUP_COUNT = 5
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Cache settings
CACHE_DURATION = 24 * 60 * 60  # 24 hours in seconds
SPELL_CACHE_FILE = 'spell_cache.json'

# Web settings
BASE_URL = "https://www.lazaruseq.com/Alla/"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# UI Base Colors
DARK_MODE_COLORS = {
    # Base Theme Colors
    'bg': '#2b2b2b',             # Charcoal Gray
    'fg': 'white',               # Pure White
    'separator': 'gray50',       # Medium Gray
    
    # Button Colors
    'button_bg': '#404040',      # Gunmetal Gray
    'button_hover': '#606060',   # Slate Gray
    'button_text': 'white',      # Pure White
    
    # Input Field Colors
    'entry_bg': '#404040',       # Gunmetal Gray
    'text_bg': '#404040',        # Gunmetal Gray
    'text_fg': 'white',          # Pure White
    'text_select_bg': '#505050', # Dark Slate Gray
    'text_select_fg': 'white',   # Pure White
    'entry_border': '#505050',   # Dark Slate Gray
    
    # Menu and Dropdown Colors
    'menu_bg': '#2b2b2b',        # Charcoal Gray
    'menu_fg': 'white',          # Pure White
    'menu_active_bg': '#404040', # Gunmetal Gray
    'menu_active_fg': 'white',   # Pure White
    'dropdown_bg': '#404040',    # Gunmetal Gray
    'dropdown_fg': 'white',      # Pure White
    'dropdown_button': '#505050', # Dark Slate Gray
    'dropdown_hover': '#606060',  # Slate Gray
    
    # Special Elements
    'hyperlink': '#6ea6ff',      # Light Steel Blue
    'heroic': '#CD6600',         # Dark Orange
    'tooltip_bg': '#909090',     # Medium Gray
    'positive_value': '#00ff00', # Pure Green
    'negative_value': '#ff0000', # Pure Red
    
    # Scrollbar Colors
    'scrollbar_bg': '#404040',   # Gunmetal Gray
    'scrollbar_fg': '#606060',   # Slate Gray
    
    # CSV Viewer Colors
    'csv_top_header_bg': '#2b3b4b', # Dark Steel Blue
    'csv_category_bg': '#404850',   # Dark Slate Blue
    'csv_item_bg': '#505050'        # Dark Slate Gray
}

LIGHT_MODE_COLORS = {
    # Base Theme Colors
    'bg': 'SystemButtonFace',    # System Default Gray
    'fg': 'black',               # Pure Black
    'separator': 'gray70',       # Medium Light Gray
    
    # Button Colors
    'button_bg': '#1f538d',      # Steel Blue
    'button_hover': '#14375e',   # Dark Steel Blue
    'button_text': 'white',      # Pure White
    
    # Input Field Colors
    'entry_bg': 'white',         # Pure White
    'text_bg': 'white',          # Pure White
    'text_fg': 'black',          # Pure Black
    'text_select_bg': '#0078d7', # Windows Blue
    'text_select_fg': 'white',   # Pure White
    'entry_border': '#e6e6e6',   # Light Gray
    
    # Menu and Dropdown Colors
    'menu_bg': 'white',          # Pure White
    'menu_fg': 'black',          # Pure Black
    'menu_active_bg': '#e6e6e6', # Light Gray
    'menu_active_fg': 'black',   # Pure Black
    'dropdown_bg': 'white',      # Pure White
    'dropdown_fg': 'black',      # Pure Black
    'dropdown_button': '#e6e6e6', # Light Gray
    'dropdown_hover': '#d9d9d9',  # Lighter Gray
    
    # Special Elements
    'hyperlink': 'blue',         # Standard Blue
    'heroic': '#CD6600',         # Dark Orange
    'tooltip_bg': '#909090',     # Medium Gray
    'positive_value': 'green',   # System Green
    'negative_value': 'red',     # System Red
    
    # Scrollbar Colors
    'scrollbar_bg': '#d9d9d9',   # Light Gray
    'scrollbar_fg': '#b3b3b3',   # Medium Gray
    
    # CSV Viewer Colors
    'csv_top_header_bg': '#1f538d', # Steel Blue
    'csv_category_bg': '#e6e6e6',   # Light Gray
    'csv_item_bg': 'white'          # Pure White
}

# Colorize CSV Viewer Colors
DARK_CSV_CATEGORY_COLORS = {
    'slot': {
        'header': '#353540',      # Midnight Blue Gray
        'category': '#353540',    # Midnight Blue Gray
        'cell': '#353540'         # Midnight Blue Gray
    },
    'basic_info': {
        'header': '#1a2d3d',      # Deep Steel Blue
        'category': '#2a3d4d',    # Dark Steel Blue
        'cell': '#3a4d5d'         # Rich Steel Blue
    },
    'weapon_stats': {
        'header': '#2d0d0d',      # Deep Crimson
        'category': '#3d1d1d',    # Dark Crimson
        'cell': '#4d2d2d'         # Rich Crimson
    },
    'primary_stats': {
        'header': '#0d2d0d',      # Deep Forest
        'category': '#1d3d1d',    # Dark Forest
        'cell': '#2d4d2d'         # Rich Forest
    },
    'attributes': {
        'header': '#2d0d2d',      # Deep Purple
        'category': '#3d1d3d',    # Dark Purple
        'cell': '#4d2d4d'         # Rich Purple
    },
    'resists': {
        'header': '#2d2d0d',      # Deep Gold
        'category': '#3d3d1d',    # Dark Gold
        'cell': '#4d4d2d'         # Rich Gold
    },
    'secondary_stats': {
        'header': '#0d0d2d',      # Deep Navy
        'category': {
            'offensive_stats': '#1d1d3d',     # Dark Navy
            'defensive_stats': '#1d1d45',     # Dark Navy Blue (darkened)
            'regeneration': '#1d3d5d'         # Dark Azure
        },
        'cell': {
            'offensive_stats': '#2d2d4d',     # Rich Navy
            'defensive_stats': '#2d2d55',     # Rich Navy Blue (darkened)
            'regeneration': '#2d4d6d'         # Rich Azure
        }
    },
    'skill_modifiers': {
        'header': '#0d1a1a',      # Deep Teal
        'category': {
            'weapon_skills': '#1d2a2a',       # Dark Teal
            'combat_abilities': '#1d3a3a',    # Dark Sea
            'magic_skills': '#1d4a4a',        # Dark Ocean
            'spell_specializations': '#1d5a5a', # Dark Marine
            'bard_skills': '#1d3d3d',         # Dark Deep Teal (adjusted to be darker)
            'utility_skills': '#1d7a7a',      # Dark Cyan
            'tradeskills': '#1d8a8a'          # Dark Azure
        },
        'cell': {
            'weapon_skills': '#2d3a3a',       # Rich Teal
            'combat_abilities': '#2d4a4a',    # Rich Sea
            'magic_skills': '#2d5a5a',        # Rich Ocean
            'spell_specializations': '#2d6a6a', # Rich Marine
            'bard_skills': '#2d4d4d',         # Rich Deep Teal (adjusted to be darker)
            'utility_skills': '#2d8a8a',      # Rich Cyan
            'tradeskills': '#2d9a9a'          # Rich Azure
        }
    },
    'effects': {
        'header': '#2d1a1a',      # Deep Burgundy
        'category': '#3d2a2a',    # Dark Burgundy
        'cell': '#4d3a3a'         # Rich Burgundy
    }
}

LIGHT_CSV_CATEGORY_COLORS = {
    'slot': {
        'header': '#e6e6f0',      # Pearl White
        'category': '#e6e6f0',    # Pearl White
        'cell': '#e6e6f0'         # Pearl White
    },
    'basic_info': {
        'header': '#4d77bb',      # Light Steel Blue
        'category': '#6699dd',    # Pale Steel Blue
        'cell': '#88bbee'         # Pastel Steel Blue
    },
    'weapon_stats': {
        'header': '#bb4d4d',      # Light Crimson
        'category': '#dd6666',    # Pale Crimson
        'cell': '#ee8888'         # Pastel Crimson
    },
    'primary_stats': {
        'header': '#4dbb4d',      # Light Forest
        'category': '#66dd66',    # Pale Forest
        'cell': '#88ee88'         # Pastel Forest
    },
    'attributes': {
        'header': '#bb4dbb',      # Light Purple
        'category': '#dd66dd',    # Pale Purple
        'cell': '#ee88ee'         # Pastel Purple
    },
    'resists': {
        'header': '#bbbb4d',      # Light Gold
        'category': '#dddd66',    # Pale Gold
        'cell': '#eeee88'         # Pastel Gold
    },
    'secondary_stats': {
        'header': '#4d4dbb',      # Light Navy
        'category': {
            'offensive_stats': '#6666dd',     # Pale Navy
            'defensive_stats': '#7777ee',     # Pale Ocean
            'regeneration': '#8888ff'         # Pale Azure
        },
        'cell': {
            'offensive_stats': '#8888ee',     # Pastel Navy
            'defensive_stats': '#9999ff',     # Pastel Ocean
            'regeneration': '#aaaaff'         # Pastel Azure
        }
    },
    'skill_modifiers': {
        'header': '#4d9999',      # Light Teal
        'category': {
            'weapon_skills': '#66bbbb',       # Pale Teal
            'combat_abilities': '#77cccc',    # Pale Sea
            'magic_skills': '#88dddd',        # Pale Ocean
            'spell_specializations': '#99eeee', # Pale Marine
            'bard_skills': '#88cccc',         # Pale Sea Teal (different from combat_abilities)
            'utility_skills': '#bbffff',      # Pale Cyan
            'tradeskills': '#ccffff'          # Pale Azure
        },
        'cell': {
            'weapon_skills': '#88cccc',       # Pastel Teal
            'combat_abilities': '#99dddd',    # Pastel Sea
            'magic_skills': '#aaaaee',        # Pastel Ocean
            'spell_specializations': '#bbbbff', # Pastel Marine
            'bard_skills': '#aadddd',         # Pastel Sea Teal (different from combat_abilities)
            'utility_skills': '#ddddff',      # Pastel Cyan
            'tradeskills': '#eeeeff'          # Pastel Azure
        }
    },
    'effects': {
        'header': '#994d4d',      # Light Burgundy
        'category': '#bb6666',    # Pale Burgundy
        'cell': '#dd8888'         # Pastel Burgundy
    }
}