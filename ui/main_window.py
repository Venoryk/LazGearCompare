#ui/main_window.py

# Imports section
import tkinter as tk
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import webbrowser
import logging
import os
import sys
import re
from datetime import datetime
from ctypes import windll, byref, sizeof, c_int

from config.constraints import STAT_CATEGORIES, CLASSES, SLOTS
from config.settings import DARK_MODE_COLORS, LIGHT_MODE_COLORS
from ui.tooltip import ToolTip
from ui.widgets import ContextMenu
from core.data_manager import DataManager
from core.item_parser import ItemParser
from core.spell_parser import SpellParser
from utils.web import WebUtils
from utils.cache import CacheManager
from utils.decorators import debug_log
from utils.csv_viewer import CSVViewer
from config.constraints import (
    STAT_CATEGORIES, CLASSES, SLOTS, 
    DISPLAY_ORGANIZATION
)

class MainWindow:
    """Main application window class"""

    # Initialization Methods
    @debug_log
    def __init__(self, root):
        """Initialize the main window"""
        logging.debug("Starting MainWindow initialization")
        try:
            self._init_window(root)
            logging.debug("Window initialization complete")
            
            self._init_utilities()
            logging.debug("Utilities initialization complete")
            
            self._init_variables()
            logging.debug("Variables initialization complete")
            
            self._init_ui()
            logging.debug("UI initialization complete")
            
            self._start_dropdown_checker()
            logging.debug("Dropdown checker started")
            
            logging.info("MainWindow initialization completed successfully")
        except Exception as e:
            logging.error(f"Failed to initialize MainWindow: {e}", exc_info=True)
            raise

    @debug_log
    def _init_window(self, root):
        """Initialize window properties and appearance"""
        try:
            self.root = root
            self.root.title("EverQuest Gear Comparer - LazarusEQ")
            
            # Set window icon
            try:
                icon_path = os.path.join('assets', 'LazGearCompare.ico')

                # If running as exe, check PyInstaller path
                if getattr(sys, 'frozen', False):
                    icon_path = os.path.join(sys._MEIPASS, 'assets', 'LazGearCompare.ico')

                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    if os.name == 'nt':  # Windows specific
                        self.root.wm_iconbitmap(default=icon_path)
                    logging.debug(f"Icon loaded successfully from: {icon_path}")
            except Exception as e:
                logging.error(f"Could not load window icon: {e}", exc_info=True)
                
        except Exception as e:
            logging.error(f"Error in window initialization: {e}", exc_info=True)
        
        # Set initial appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root.configure(bg='SystemButtonFace')

        # Windows specific configuration
        if os.name == 'nt':
            self.root.wm_attributes('-alpha', 0.99)
            try:
                HWND = windll.user32.GetParent(self.root.winfo_id())
                windll.dwmapi.DwmSetWindowAttribute(HWND, 20, byref(c_int(2)), sizeof(c_int))
            except:
                pass
        
        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    @debug_log
    def _init_utilities(self):
        """Initialize utility classes"""
        try:
            logging.debug("Initializing WebUtils")
            self.web_utils = WebUtils()
            
            logging.debug("Initializing DataManager")
            self.data_manager = DataManager()
            self.item_cache = self.data_manager.cache_manager
            self.spell_cache = self.data_manager.spell_cache_manager
            
            logging.debug("Initializing ItemParser")
            self.item_parser = ItemParser()
            
            logging.debug("Initializing CSVViewer")
            self.csv_viewer = CSVViewer()
            
            logging.debug("Initializing SpellParser")
            self.spell_parser = SpellParser()
            logging.debug(f"SpellParser methods: {dir(self.spell_parser)}")
            
            logging.debug("All utilities initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize utilities: {e}", exc_info=True)
            raise

    @debug_log
    def _init_variables(self):
        """Initialize instance variables"""
        # UI state variables
        self.dark_mode_var = tk.BooleanVar(value=False)
        self.debug_var = tk.BooleanVar(value=False)
        self.class_var = tk.StringVar()
        self.slot_var = tk.StringVar()
        self.item_name = tk.StringVar()
        self.colorize_var = tk.BooleanVar(value=False)
        self.csv_colorize_var = tk.BooleanVar(value=False)
        self.auto_save_var = tk.BooleanVar(value=False)
        
        # Internal state tracking
        self.needs_dropdown_check = False
        self.needs_menu_check = False
        self.current_url = ""
        self.current_item_data = {}
        self.hyperlink_urls = {}

        # Stat Categories
        self.stat_categories = STAT_CATEGORIES

    @debug_log
    def _init_ui(self):
        """Initialize UI components"""
        self.setup_ui()
        self.setup_context_menu()
        self.setup_bindings()

        # Force initial UI color update
        colors = LIGHT_MODE_COLORS
        self._update_ui_colors(colors)
        self.root.update_idletasks()

    # UI Setup Methods
    @debug_log
    def setup_ui(self):
        """Setup the main UI components"""
        # Create menu frame
        self.menu_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.menu_frame.grid(row=0, column=0, sticky='ew')

        # Add separator
        self.separator = ctk.CTkFrame(
            self.root,
            height=2,
            fg_color=DARK_MODE_COLORS['entry_bg'] if self.dark_mode_var.get() else LIGHT_MODE_COLORS['entry_bg']
        )
        self.separator.grid(row=1, column=0, sticky='ew', pady=(0, 5))

        # Create Options button
        self.options_button = ctk.CTkButton(
            self.menu_frame,
            text="Options",
            command=self.show_options_menu,
            corner_radius=0,
            fg_color="transparent",
            hover_color=DARK_MODE_COLORS['button_hover'] if self.dark_mode_var.get() 
                    else LIGHT_MODE_COLORS['button_hover'],
            text_color=DARK_MODE_COLORS['fg'] if self.dark_mode_var.get() 
                    else LIGHT_MODE_COLORS['fg'],
            height=28,
            width=70
        )
        self.options_button.grid(row=0, column=0, padx=2, sticky='w')

        # Bind menu closing
        self.root.bind('<Button-1>', self._close_menu, '+')

        # Add separator
        self.separator = ctk.CTkFrame(
            self.root,
            height=2,
            fg_color="gray70"
        )
        self.separator.grid(row=1, column=0, sticky='ew', pady=(0, 5))

        # Create the main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

        # Create button frame to hold search/clear buttons
        self.button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # Create second button frame for CSV buttons
        self.csv_button_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.csv_button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        # Setup UI components
        self.setup_class_selection()
        self.setup_slot_selection()
        self.setup_item_entry()
        self.setup_buttons()
        self.setup_results_area()

        # Configure grid weights
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    @debug_log
    def setup_class_selection(self):
        """Setup the class selection dropdown"""
        class_label = ctk.CTkLabel(self.main_frame, text="Class:")
        class_label.grid(row=0, column=0, sticky='w')

        self.class_combo = ctk.CTkOptionMenu(
            self.main_frame,
            variable=self.class_var,
            values=CLASSES,
            **self.get_dropdown_colors()
        )
        self.class_combo.grid(row=0, column=1, sticky='e', padx=5, pady=5)

        ToolTip(class_label, "Required for Saving to CSV only")
        ToolTip(self.class_combo, "Required for Saving to CSV only")

    @debug_log
    def setup_slot_selection(self):
        """Setup the slot selection dropdown"""
        slot_label = ctk.CTkLabel(self.main_frame, text="Slot:")
        slot_label.grid(row=1, column=0, sticky='w')

        self.slot_combo = ctk.CTkOptionMenu(
            self.main_frame,
            variable=self.slot_var,
            values=SLOTS,
            **self.get_dropdown_colors()
        )
        self.slot_combo.grid(row=1, column=1, sticky='e', padx=5, pady=5)

        ToolTip(slot_label, "Required for Saving to CSV only")
        ToolTip(self.slot_combo, "Required for Saving to CSV only")

    @debug_log
    def setup_item_entry(self):
        """Setup the item name entry field"""
        item_label = ctk.CTkLabel(self.main_frame, text="Item Name:")
        item_label.grid(row=2, column=0, sticky='w')

        self.item_entry = ctk.CTkEntry(
            self.main_frame,
            textvariable=self.item_name,
            **self.get_entry_colors()
        )
        self.item_entry.grid(row=2, column=1, sticky='e', padx=5, pady=5)

    @debug_log
    def setup_buttons(self):
        """Setup the action buttons"""
        button_colors = self.get_button_colors()

        # Create Clear Results button
        self.clear_button = ctk.CTkButton(
            self.button_frame,
            text="Clear Results",
            command=self.clear_results,
            **button_colors
        )
        self.clear_button.grid(row=0, column=0, padx=(25, 25))

        # Create Search Item button
        self.search_button = ctk.CTkButton(
            self.button_frame,
            text="Search Item",
            command=self.search_item,
            **button_colors
        )
        self.search_button.grid(row=0, column=1, padx=(25, 25))

        # Create Save to CSV button
        self.save_button = ctk.CTkButton(
            self.csv_button_frame,
            text="Save to CSV",
            command=self.save_to_csv,
            **button_colors
        )
        self.save_button.grid(row=0, column=1, padx=(25, 25))

        # Create Open Class CSV button
        self.open_csv_button = ctk.CTkButton(
            self.csv_button_frame,
            text="Open Class CSV",
            command=self.open_csv_viewer,
            **button_colors
        )
        self.open_csv_button.grid(row=0, column=0, padx=(25, 25))

        # Configure grid weights for both button frames
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.csv_button_frame.grid_columnconfigure(0, weight=1)
        self.csv_button_frame.grid_columnconfigure(1, weight=1)

    @debug_log
    def setup_results_area(self):
        """Setup the results text area"""
        self.results_text = tk.Text(
            self.main_frame,
            height=30,
            width=50,
            wrap=tk.WORD,
            maxundo=0,
            **self.get_text_colors()
        )
        self.results_text.grid(row=4, column=0, columnspan=2, pady=10, sticky='nsew')

        # Allow Ctrl+A and Ctrl+C but prevent other keyboard input
        self.results_text.bind("<Control-a>", lambda e: None)  # Allow system default select all
        self.results_text.bind("<Control-c>", lambda e: None)  # Allow system default copy
        self.results_text.bind("<Key>", lambda e: "break")     # Prevent other keyboard input

        # Configure text widget tags
        self.results_text.tag_configure("bold", font=("TkFixedFont", 10, "bold"), underline=1)
        self.results_text.tag_configure("hyperlink", 
            foreground=DARK_MODE_COLORS['hyperlink'] if self.dark_mode_var.get() 
            else LIGHT_MODE_COLORS['hyperlink']
        )
        self.results_text.tag_configure("heroic", 
            foreground=DARK_MODE_COLORS['heroic'] if self.dark_mode_var.get() 
            else LIGHT_MODE_COLORS['heroic']
        )

        # Configure Colorize Stats
        colors = DARK_MODE_COLORS if self.dark_mode_var.get() else LIGHT_MODE_COLORS
        self.results_text.tag_configure("positive", foreground=colors['positive_value'])
        self.results_text.tag_configure("negative", foreground=colors['negative_value'])

    @debug_log
    def setup_context_menu(self):
        """Setup the right-click context menu"""
        self.context_menu = ContextMenu(self.root, self.dark_mode_var)
        self.results_text.bind("<Button-3>", self.context_menu.show_menu)
        self.item_entry.bind("<Button-3>", self.context_menu.show_menu)

    @debug_log
    def setup_bindings(self):
        """Setup event bindings"""
        # Search bindings
        self.root.bind('<Return>', lambda e: self.search_item())
        self.item_entry.bind('<Return>', lambda e: self.search_item())
        
        # Hyperlink event bindings
        self.results_text.tag_bind("hyperlink", "<Enter>", self._on_enter)
        self.results_text.tag_bind("hyperlink", "<Leave>", self._on_leave)
        self.results_text.tag_bind("hyperlink", "<Button-1>", self._on_click)
        
        # Dropdown event bindings
        self.class_combo.bind('<Button-1>', 
            lambda e: self.toggle_dropdown(e, self.class_combo))
        self.slot_combo.bind('<Button-1>', 
            lambda e: self.toggle_dropdown(e, self.slot_combo))

        # Add bindings for auto save checks
        self.class_combo.bind('<<ComboboxSelected>>', lambda e: self._check_search_button_state())
        self.slot_combo.bind('<<ComboboxSelected>>', lambda e: self._check_search_button_state())
        self.item_entry.bind('<KeyRelease>', lambda e: self._check_search_button_state())


    # Core Functionality Methods
    @debug_log
    def search_item(self):
        """Search for an item and display results"""
        if self.auto_save_var.get() and not self._check_search_button_state():
            logging.warning("Search attempted without required class/slot selections when auto-save enabled")
            CTkMessagebox(
                master=None,
                title="Warning",
                message="Please select both class and slot before searching with auto-save enabled",
                icon="warning"
            )
            return
            
        item_name = self.item_name.get()
        
        if not item_name:
            logging.warning("Search attempted with empty item name")
            CTkMessagebox(
                master=None,
                title="Warning",
                message="Please enter an item name",
                icon="warning"
            )
            return
                
        logging.info(f"Starting search for item: {item_name}")
        
        try:
            self.show_loading_indicator()
            logging.debug("Loading indicator displayed")
            
            # Check cache first with case-insensitive key
            cache_key = item_name.lower()
            logging.debug(f"Checking cache for key: {cache_key}")
            
            cached_item = self.item_cache.get(cache_key)
            if cached_item:
                logging.debug(f"Cache hit for item: {item_name}")
                self.results_text.config(state='normal')
                self.results_text.delete(1.0, tk.END)
                self.display_results(cached_item.get('ID'), 
                                cached_item, 
                                cached_item.get('URL'))
                logging.debug(f"Displayed cached results for: {item_name}")
                
                # Auto save if enabled and exact match found
                if self.auto_save_var.get():
                    self.save_to_csv()
                    
                self.hide_loading_indicator()
                return

            # If not in cache, fetch from web
            logging.debug(f"Cache miss for item: {item_name}, fetching from web")
            search_url = self.web_utils.format_search_url(item_name)
            logging.debug(f"Formatted search URL: {search_url}")
            
            html_content = self.web_utils.get_page_content(search_url)
            logging.debug("Retrieved search page content")
            
            item_id = self.item_parser.extract_item_id(html_content, item_name)
            if not item_id:
                logging.warning(f"No exact item match found for: {item_name}")
                self._handle_similar_items(html_content)
                # Don't auto-save when showing similar items
                return

            logging.debug(f"Found item ID: {item_id}")
            item_url = self.web_utils.format_item_url(item_id)
            logging.debug(f"Formatted item URL: {item_url}")
            
            html_content = self.web_utils.get_page_content(item_url)
            logging.debug("Retrieved item page content")
            
            stats = self.item_parser.extract_item_stats(html_content)
            if not stats:
                logging.error("Failed to extract item stats")
                self.results_text.insert(tk.END, "Failed to extract item stats. Check debug log for details.\n")
                self.hide_loading_indicator()
                return
            
            logging.debug(f"Successfully extracted stats for item: {item_name}")
            
            # Add ID and URL to stats before caching
            stats['ID'] = item_id
            stats['URL'] = item_url
            
            # Cache the item data
            self.item_cache.set(item_name, stats)
            logging.debug(f"Cached item data for: {item_name}")

            # Cache any spell effects found
            for effect_type in self.stat_categories['effects']:
                details_key = f"{effect_type}_DETAILS"
                if details_key in stats:
                    effect_details = stats[details_key]
                    spell_cache_key = f"{effect_details['name']}_{effect_details['id']}"
                    self.spell_cache.set(spell_cache_key, effect_details)
                    logging.debug(f"Cached spell data for: {effect_details['name']}")
            
            self.display_results(item_id, stats, item_url)
            logging.info(f"Successfully completed search for: {item_name}")
            
            # Auto save if enabled and exact match found
            if self.auto_save_var.get():
                self.save_to_csv()
                
        except Exception as e:
            error_msg = self.item_parser._handle_search_error(e)
            CTkMessagebox(
                master=None,
                title="Error",
                message=error_msg,
                icon="cancel"
            )
        finally:
            self.hide_loading_indicator()
            logging.debug("Loading indicator hidden")

    @debug_log
    def save_to_csv(self):
        """Save current item data to CSV file"""
        logging.info("Starting save to CSV operation")
        
        if not self._validate_save_requirements():
            logging.warning("Save requirements not met - operation cancelled")
            return

        # Format class name to use underscore instead of space
        formatted_class = self.class_var.get().lower().replace(' ', '_')
        filename = f"{formatted_class}_gear_comparison.csv"
        logging.debug(f"Target CSV file: {filename}")
        
        try:
            # Check for duplicate entry
            item_name = self.current_item_data.get('Name')
            if self.data_manager.check_duplicate_entry(filename, item_name):
                logging.warning(f"Duplicate item found: {item_name}")
                if self.auto_save_var.get():
                    # Show "Entry Already Exists" in search button temporarily
                    self.root.after(500, lambda: self.search_button.configure(text="Entry Already Exists"))
                    # Reset button text after 5 seconds
                    self.root.after(5250, lambda: self.search_button.configure(text="Search Item"))
                else:
                    CTkMessagebox(
                        master=None,
                        title="Warning",
                        message=f"{item_name} already exists in {filename}",
                        icon="warning"
                    )
                return
                
            logging.debug(f"Attempting to save item data for slot: {self.slot_var.get()}")
            logging.debug(f"Current item data: {self.current_item_data.get('Name', 'Unknown')}")
            
            # Create slot mapping for ordering
            slot_mapping = {slot: i for i, slot in enumerate(SLOTS)}
            logging.debug("Created slot mapping for CSV ordering")
            
            success = self.data_manager.save_item_to_csv(
                filename, 
                self.current_item_data,
                self.slot_var.get(),
                slot_mapping
            )
            
            if success:
                logging.info(f"Successfully saved item data to {filename}")
                if self.auto_save_var.get():
                    # Show "Saved!" in search button temporarily
                    self.root.after(500, lambda: self.search_button.configure(text="Saved!"))
                    # Reset button text after 3 seconds
                    self.root.after(3000, lambda: self.search_button.configure(text="Search Item"))
                else:
                    CTkMessagebox(
                        master=None,
                        title="Success",
                        message=f"Saved to {filename}",
                        icon="check"
                    )
            else:
                logging.error("Data manager reported save failure")
                raise Exception("Failed to save data")
                
        except Exception as e:
            logging.error(f"Error during save operation: {e}", exc_info=True)
            self._handle_save_error(e)

    @debug_log
    def open_csv_viewer(self):
        """Open CSV viewer window"""
        try:
            if not self.class_var.get():
                logging.warning("Attempted to open CSV viewer without class selection")
                CTkMessagebox(
                    master=None,
                    title="Warning",
                    message="Please select a class first",
                    icon="warning"
                )
                return

            logging.info(f"Opening CSV viewer for class: {self.class_var.get()}")
            
            viewer = ctk.CTkToplevel(self.root)
            viewer.title(f"{self.class_var.get()} Gear Comparison")
            viewer.geometry("1280x800")
            viewer.minsize(1280, 800)
            logging.debug("Created viewer window")
            
            # Set icon path based on environment
            try:
                # If running as exe, check PyInstaller path
                if getattr(sys, 'frozen', False):
                    icon_path = os.path.join(sys._MEIPASS, 'assets', 'LazGearCompare.ico')
                else:
                    icon_path = os.path.join('assets', 'LazGearCompare.ico')
                    
                if os.path.exists(icon_path):
                    viewer.after(250, lambda: viewer.iconbitmap(icon_path))
                    if os.name == 'nt':  # Windows specific
                        viewer.after(250, lambda: viewer.wm_iconbitmap(default=icon_path))
                    logging.debug(f"Icon scheduled for loading from: {icon_path}")
            except Exception as e:
                logging.error(f"Could not load window icon: {e}", exc_info=True)
            
            # Force window to front using iconify/deiconify
            viewer.iconify()
            viewer.after(250, lambda: viewer.deiconify())
            logging.debug("Scheduled window focus handling")
            
            # Create CSV viewer instance and display data
            self.csv_viewer = CSVViewer()
            self.csv_viewer.set_colorize(self.csv_colorize_var.get())
            
            logging.debug(f"Loading CSV data for class: {self.class_var.get()}")
            df = self.csv_viewer.load_csv(self.class_var.get())
            
            if df is not None:
                self.csv_viewer.display_csv_data(
                    viewer, 
                    df, 
                    dark_mode=ctk.get_appearance_mode() == "Dark",
                    colorize=self.csv_colorize_var.get()
                )
            else:
                logging.warning("No CSV data loaded")
                CTkMessagebox(
                    master=None,
                    title="Warning",
                    message=f"No data found for {self.class_var.get()}",
                    icon="warning"
                )
                
        except Exception as e:
            logging.error(f"Failed to open CSV viewer: {e}", exc_info=True)
            CTkMessagebox(
                master=None,
                title="Error",
                message="Failed to open CSV viewer. Check logs for details.",
                icon="cancel"
            )
            raise

    @debug_log
    def clear_results(self):
        """Clear search results and reset fields"""
        try:
            logging.debug("Clearing all results and resetting fields")
            self.results_text.delete(1.0, tk.END)
            self.item_name.set("")
            self.current_item_data.clear()
            self.current_url = ""
            self.hyperlink_urls.clear()
            logging.debug("Successfully cleared all results and reset fields")
        except Exception as e:
            logging.error(f"Error clearing results: {e}", exc_info=True)

    # Display Methods
    @debug_log
    def display_results(self, item_id, stats, url):
        """Format and display the results"""
        try:
            logging.debug(f"Starting to display results for item ID: {item_id}")
            
            self.results_text.config(state='normal')
            self.results_text.delete(1.0, tk.END)
            logging.debug("Cleared previous results")
            
            # Display sections
            self._display_sections(stats)
            logging.debug("Completed displaying all sections")
            
            self.current_url = url
            self.current_item_data = stats.copy()
            logging.debug(f"Updated current item data for: {stats.get('Name', 'Unknown')}")
            
        except Exception as e:
            logging.error(f"Error displaying results: {e}", exc_info=True)
            raise

    @debug_log
    def _display_sections(self, stats):
        """Display all sections of item information"""
        try:
            # Handle all non-effect sections first
            for section, config in DISPLAY_ORGANIZATION.items():
                if section != 'effects':  # Skip effects for now
                    display_name = config['display_name']
                    categories = config['categories']
                    
                    # Check if any stats from these categories exist
                    has_stats = any(any(stat in stats for stat in self.stat_categories[cat]) 
                                for cat in categories)
                    
                    if has_stats:
                        # Add newline before section header (except for first section)
                        if section != 'basic_info':
                            self.results_text.insert(tk.END, "\n")
                        
                        # Insert section header with bold formatting
                        self.results_text.insert(tk.END, f"{display_name}:\n", "bold")
                        
                        # Display stats for each category
                        for category in categories:
                            self._display_category_stats(stats, category)
            
            # Handle effects section last
            if any(f"{effect}_DETAILS" in stats for effect in self.stat_categories['effects']):
                self.results_text.insert(tk.END, "\n")
                self.results_text.insert(tk.END, f"{DISPLAY_ORGANIZATION['effects']['display_name']}:\n", "bold")
                self.display_effects(stats)
                        
        except Exception as e:
            logging.error(f"Error in _display_sections: {e}", exc_info=True)

    @debug_log
    def _display_category_stats(self, stats, category):
        """Display stats for a specific category"""
        try:
            stats_present = False
            
            # Filter out effect-related entries
            effect_related = [key for key in stats.keys() 
                            if any(x in key for x in ['_CHARGES', '_DETAILS', '_EFFECT'])]
            
            # Handle basic info specially to include aug slots
            if category == 'basic_info':
                basic_fields = ['NAME', 'ID', 'URL', 'TYPE']
                for field in basic_fields:
                    # Check for field in stats using case-insensitive comparison
                    field_key = next((k for k in stats.keys() 
                                    if k.upper() == field), None)
                    if field_key:
                        if not stats_present:
                            stats_present = True
                        self.results_text.insert(tk.END, f"ITEM {field}: ")
                        if field == 'URL':
                            self.insert_hyperlink(stats[field_key], stats[field_key])
                            self.results_text.insert(tk.END, "\n")
                        else:
                            self.results_text.insert(tk.END, f"{stats[field_key]}\n")
                
                # Handle aug slots on one line
                aug_slots = sorted(key for key in stats if key.startswith('SLOT '))
                if aug_slots:
                    self.results_text.insert(tk.END, "AUG SLOTS: ")
                    slots_text = ", ".join(f"{slot.replace('SLOT ', '')}: {stats[slot]}" 
                                        for slot in aug_slots)
                    self.results_text.insert(tk.END, f"{slots_text}\n")
            
            # Handle bard skills only in their designated category
            elif category == 'bard_skills':
                bard_skills = [key for key in stats.keys() if key.startswith('BARD_')]
                if bard_skills:
                    if not stats_present:
                        stats_present = True
                        self.results_text.insert(tk.END, "\nBARD MODIFIERS:\n", "bold")
                    for key in sorted(bard_skills):
                        display_name = key.replace('BARD_', '')
                        self.results_text.insert(tk.END, f"{display_name}: ")
                        stat_value = str(stats[key])
                        if self.colorize_var.get():
                            try:
                                if stat_value.endswith('%'):
                                    num_value = int(stat_value.rstrip('%'))
                                    tag = "positive" if num_value > 0 else "negative" if num_value < 0 else None
                                    self.results_text.insert(tk.END, stat_value, tag)
                                else:
                                    num_value = int(stat_value)
                                    tag = "positive" if num_value > 0 else "negative" if num_value < 0 else None
                                    self.results_text.insert(tk.END, stat_value, tag)
                            except ValueError:
                                self.results_text.insert(tk.END, stat_value)
                        else:
                            self.results_text.insert(tk.END, stat_value)
                        self.results_text.insert(tk.END, "\n")
            
            # Handle regular stats
            else:
                for stat in self.stat_categories[category]:
                    if stat in stats and stat not in effect_related and not stat.startswith('BARD_'):
                        if not stats_present:
                            stats_present = True
                        
                        # Special handling for BACKSTAB_MOD
                        if stat == 'BACKSTAB_MOD':
                            self.results_text.insert(tk.END, "BACKSTAB: ")
                        else:
                            self.results_text.insert(tk.END, f"{stat}: ")
                        
                        stat_value = str(stats[stat])
                        
                        # Handle heroic values
                        if '+' in stat_value:
                            base_value, heroic_value = stat_value.split('+')
                            if self.colorize_var.get():
                                try:
                                    base_num = int(base_value.strip())
                                    tag = "positive" if base_num > 0 else "negative" if base_num < 0 else None
                                    self.results_text.insert(tk.END, base_value.strip(), tag)
                                except ValueError:
                                    self.results_text.insert(tk.END, base_value.strip())
                            else:
                                self.results_text.insert(tk.END, base_value.strip())
                            
                            self.results_text.insert(tk.END, " (+")
                            self.results_text.insert(tk.END, heroic_value.strip(), "heroic")
                            self.results_text.insert(tk.END, ")")
                        
                        # Handle percentage values
                        elif isinstance(stat_value, str) and stat_value.endswith('%'):
                            if self.colorize_var.get():
                                try:
                                    num_value = int(stat_value.rstrip('%'))
                                    tag = "positive" if num_value > 0 else "negative" if num_value < 0 else None
                                    self.results_text.insert(tk.END, stat_value, tag)
                                except ValueError:
                                    self.results_text.insert(tk.END, stat_value)
                            else:
                                self.results_text.insert(tk.END, stat_value)
                        
                        # Handle regular numeric values
                        else:
                            if self.colorize_var.get():
                                try:
                                    num_value = int(stat_value)
                                    tag = "positive" if num_value > 0 else "negative" if num_value < 0 else None
                                    self.results_text.insert(tk.END, stat_value, tag)
                                except ValueError:
                                    self.results_text.insert(tk.END, stat_value)
                            else:
                                self.results_text.insert(tk.END, stat_value)
                        
                        # Add newline after each stat
                        self.results_text.insert(tk.END, "\n")
                        
        except Exception as e:
            logging.error(f"Error displaying category stats: {e}", exc_info=True)

    @debug_log
    def display_effects(self, stats):
        """Display item effects"""
        try:
            for effect_type in self.stat_categories['effects']:
                details_key = f"{effect_type}_DETAILS"
                if details_key in stats:
                    effect_details = stats[details_key]
                    display_name, additional_details = self.spell_parser.format_effect_display(effect_details)
                    
                    # Display effect type and name with cast time on same line
                    self.results_text.insert(tk.END, f"{effect_type}: ")
                    self.insert_hyperlink(display_name, effect_details['url'])
                    
                    # Add cast time on same line as name
                    if additional_details:
                        cast_time, *rest = additional_details.split('\n')
                        self.results_text.insert(tk.END, cast_time)  # Cast time without newline
                        self.results_text.insert(tk.END, "\n")  # Then add newline
                        
                        # Charges on next line
                        if rest:
                            self.results_text.insert(tk.END, f"{rest[0]}")
                    
                    # Display effects on separate lines
                    if effect_details.get('effects'):
                        self.results_text.insert(tk.END, "\n")  # Add blank line before effects
                        for effect in effect_details['effects']:
                            self.results_text.insert(tk.END, f"  {effect}\n")
                        
                    self.results_text.insert(tk.END, "\n")
                    
        except Exception as e:
            logging.error(f"Error displaying effects: {e}", exc_info=True)

    @debug_log
    def display_similar_items(self, similar_items):
        """Display similar items in results text"""
        try:
            self.results_text.delete(1.0, tk.END)
            error_msg = "Exact item match not found.\n\nSimilar items found:\n"
            self.results_text.insert(tk.END, error_msg)
            for item in similar_items:
                self.insert_similar_item_hyperlink(item)
        except Exception as e:
            logging.error(f"Error displaying similar items: {e}", exc_info=True)
        finally:
            self.hide_loading_indicator()

    # UI State Management Methods
    @debug_log
    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        is_dark = self.dark_mode_var.get()
        
        # Update appearance mode
        ctk.set_appearance_mode("dark" if is_dark else "light")
        
        # Update root window background
        self.root.configure(bg='#2b2b2b' if is_dark else 'SystemButtonFace')
        
        # Update colors based on settings
        colors = DARK_MODE_COLORS if is_dark else LIGHT_MODE_COLORS
        
        # Update UI elements with new colors
        self._update_ui_colors(colors)
        
        # Update options menu colors and label
        if hasattr(self, 'options_menu'):
            self.options_menu.configure(
                bg=colors['menu_bg'],
                fg=colors['menu_fg'],
                activebackground=colors['menu_active_bg'],
                activeforeground=colors['menu_active_fg']
            )
            # Update the label text for the Dark Mode menu item (index 1)
            self.options_menu.entryconfig(1, 
                label="Light Mode" if is_dark else "Dark Mode"
            )

        # Update CSV viewer if it's open
        if hasattr(self, 'csv_viewer') and self.csv_viewer and hasattr(self.csv_viewer, 'df'):
            for window in self.root.winfo_children():
                if isinstance(window, ctk.CTkToplevel):
                    # Store current state
                    temp_df = self.csv_viewer.df
                    
                    # Set appearance mode first
                    ctk.set_appearance_mode("Dark" if is_dark else "Light")
                    
                    # Destroy old window
                    window.destroy()
                    
                    # Call open_csv_viewer to create new window
                    self.open_csv_viewer()
                    
                    # Find new window and display data
                    for new_window in self.root.winfo_children():
                        if isinstance(new_window, ctk.CTkToplevel):
                            self.csv_viewer.display_csv_data(
                                new_window, 
                                temp_df, 
                                is_dark,
                                self.csv_colorize_var.get()
                            )
                            break

        # Force window redraw
        self.root.update_idletasks()

    @debug_log
    def toggle_csv_colorize(self):
        """Toggle CSV viewer colorization"""
        try:
            # Find the CSV viewer window if it exists
            for window in self.root.winfo_children():
                if isinstance(window, ctk.CTkToplevel):
                    if hasattr(self, 'csv_viewer') and hasattr(self.csv_viewer, 'df'):
                        self.csv_viewer.display_csv_data(
                            window,
                            self.csv_viewer.df,
                            self.dark_mode_var.get(),
                            self.csv_colorize_var.get()
                        )
                        logging.debug("CSV viewer colorization toggled")
                        break
        except Exception as e:
            logging.error(f"Error toggling CSV colorization: {e}", exc_info=True)

    @debug_log
    def toggle_debug_mode(self):
        """Toggle debug logging based on checkbox state"""
        if self.debug_var.get():
            logging.getLogger().setLevel(logging.DEBUG)
            logging.debug("Debug mode enabled")
        else:
            logging.getLogger().setLevel(logging.INFO)
            logging.info("Debug mode disabled")

    @debug_log
    def toggle_dropdown(self, event, optionmenu):
        """Toggle dropdown state between normal and disabled"""
        try:
            current_state = optionmenu.cget('state')
            new_state = 'disabled' if current_state == 'normal' else 'normal'
            logging.debug(f"Toggling dropdown state from {current_state} to {new_state}")
            optionmenu.configure(state=new_state)
            self.needs_dropdown_check = True
        except Exception as e:
            logging.error(f"Error toggling dropdown: {e}", exc_info=True)

    @debug_log
    def toggle_colorize(self):
        """Toggle stat colorization and refresh display"""
        if self.current_item_data:
            self.display_results(
                self.current_item_data.get('ID'),
                self.current_item_data,
                self.current_item_data.get('URL')
            )

    @debug_log
    def dropdown_checker(self):
        """Periodically check and re-enable dropdowns and menus"""
        try:
            if self.needs_dropdown_check:
                logging.debug("Re-enabling dropdowns")
                self.class_combo.configure(state='normal')
                self.slot_combo.configure(state='normal')
                self.needs_dropdown_check = False
                logging.debug("Dropdowns re-enabled")
            
            if hasattr(self, 'needs_menu_check') and self.needs_menu_check:
                if hasattr(self, '_menu_visible') and self._menu_visible:
                    logging.debug("Hiding visible menu")
                    self.options_menu.unpost()
                    self._menu_visible = False
                self.needs_menu_check = False
                logging.debug("Menu check completed")
            
            # Schedule next check without logging
            self.root.after(500, self.dropdown_checker)
            
        except Exception as e:
            logging.error(f"Error in dropdown checker: {e}", exc_info=True)

    # UI Helper Methods
    @debug_log
    def _start_dropdown_checker(self):
        """Start the periodic dropdown checker"""
        try:
            logging.debug("Starting dropdown checker")
            self.needs_dropdown_check = False
            self.dropdown_checker()
        except Exception as e:
            logging.error(f"Error starting dropdown checker: {e}", exc_info=True)

    @debug_log
    def _update_ui_colors(self, colors):
        """Update UI element colors based on current theme"""
        try:
            logging.debug("Updating UI colors")
            
            # Update separator colors
            self.separator.configure(fg_color=colors['entry_bg'])
            
            # Update options button colors
            self.options_button.configure(
                text_color=colors['fg'],
                hover_color=colors['button_hover']
            )
            
            # Update dropdown colors
            self.class_combo.configure(**self.get_dropdown_colors())
            self.slot_combo.configure(**self.get_dropdown_colors())
            
            # Update entry colors
            self.item_entry.configure(**self.get_entry_colors())
            
            # Update button colors
            button_colors = self.get_button_colors()
            self.search_button.configure(**button_colors)
            self.clear_button.configure(**button_colors)
            self.save_button.configure(**button_colors)
            self.open_csv_button.configure(**button_colors)
            
            # Update text widget colors
            text_colors = self.get_text_colors()
            for key, value in text_colors.items():
                self.results_text[key] = value
                
            # Update text widget tags
            self.results_text.tag_configure("hyperlink", foreground=colors['hyperlink'])
            self.results_text.tag_configure("heroic", foreground=colors['heroic'])
            self.results_text.tag_configure("positive", foreground=colors['positive_value'])
            self.results_text.tag_configure("negative", foreground=colors['negative_value'])
            
            logging.debug("UI colors updated successfully")
        except Exception as e:
            logging.error(f"Error updating UI colors: {e}", exc_info=True)

    @debug_log
    def show_loading_indicator(self):
        """Show loading indicator"""
        try:
            logging.debug("Showing loading indicator")
            self.search_button.configure(text="Searching...", state="disabled")
            self.root.config(cursor="wait")
            self.root.update_idletasks()
        except Exception as e:
            logging.error(f"Error showing loading indicator: {e}", exc_info=True)

    @debug_log
    def hide_loading_indicator(self):
        """Hide loading indicator"""
        try:
            logging.debug("Scheduling loading indicator hide")
            # Only update button text if not showing "Saved!" message
            if not self.auto_save_var.get() or self.search_button.cget("text") != "Saved!":
                self.root.after(0, self._complete_hide_indicator)
        except Exception as e:
            logging.error(f"Error hiding loading indicator: {e}", exc_info=True)

    @debug_log
    def _complete_hide_indicator(self):
        """Complete the hiding of the loading indicator"""
        try:
            logging.debug("Completing loading indicator hide")
            self.search_button.configure(text="Search Item", state="normal")
            self.root.config(cursor="")
            self.root.update_idletasks()
            logging.debug("Loading indicator hidden")
        except Exception as e:
            logging.error(f"Error completing hide indicator: {e}", exc_info=True)

    @debug_log
    def _check_search_button_state(self):
        """Enable/disable search button based on auto save requirements"""
        if self.auto_save_var.get():
            if not self.class_var.get() or not self.slot_var.get():
                logging.debug("Disabling search button - missing class/slot selection")
                self.search_button.configure(state="disabled")
                return False
        
        # Only enable if there's text in the item name field
        if self.item_name.get().strip():
            logging.debug("Enabling search button - requirements met")
            self.search_button.configure(state="normal")
            return True
        else:
            logging.debug("Disabling search button - no item name")
            self.search_button.configure(state="disabled")
            return False

    @debug_log
    def show_options_menu(self, event=None):
        """Show or hide the options menu below the Options button"""
        try:
            # Check if menu is already posted
            if hasattr(self, '_menu_visible') and self._menu_visible:
                self.options_menu.unpost()
                self._menu_visible = False
                return
                
            # Recreate the menu with current states
            self.options_menu = tk.Menu(
                self.root,
                tearoff=0,
                bg=DARK_MODE_COLORS['menu_bg'] if self.dark_mode_var.get() else LIGHT_MODE_COLORS['menu_bg'],
                fg=DARK_MODE_COLORS['menu_fg'] if self.dark_mode_var.get() else LIGHT_MODE_COLORS['menu_fg'],
                activebackground=DARK_MODE_COLORS['menu_active_bg'] if self.dark_mode_var.get() else LIGHT_MODE_COLORS['menu_active_bg'],
                activeforeground=DARK_MODE_COLORS['menu_active_fg'] if self.dark_mode_var.get() else LIGHT_MODE_COLORS['menu_active_fg']
            )

            # Add Debug Mode checkbutton
            self.options_menu.add_checkbutton(
                label="Debug Mode",
                variable=self.debug_var,
                command=self.toggle_debug_mode,
                onvalue=True,
                offvalue=False,
                selectcolor='white' if self.dark_mode_var.get() else 'black'
            )

            # Add Dark Mode command
            self.options_menu.add_command(
                label="Light Mode" if self.dark_mode_var.get() else "Dark Mode",
                command=lambda: [
                    self.dark_mode_var.set(not self.dark_mode_var.get()), 
                    self.toggle_dark_mode()
                ]
            )

            # Add separator
            self.options_menu.add_separator()

            # Add Auto Save checkbutton
            self.options_menu.add_checkbutton(
                label="Auto Save to CSV",
                variable=self.auto_save_var,
                command=self._check_search_button_state,
                onvalue=True,
                offvalue=False,
                selectcolor='white' if self.dark_mode_var.get() else 'black'
            )

            # Add separator
            self.options_menu.add_separator()

            # Add Colorize Stats checkbutton
            self.options_menu.add_checkbutton(
                label="Colorize Stats",
                variable=self.colorize_var,
                command=self.toggle_colorize,
                onvalue=True,
                offvalue=False,
                selectcolor='white' if self.dark_mode_var.get() else 'black'
            )

            # Add CSV Colorize checkbutton
            self.options_menu.add_checkbutton(
                label="Colorize CSV Viewer",
                variable=self.csv_colorize_var,
                command=self.toggle_csv_colorize,
                onvalue=True,
                offvalue=False,
                selectcolor='white' if self.dark_mode_var.get() else 'black'
            )

            # Add separator
            self.options_menu.add_separator()

            # Add Clear Spell Cache command
            self.options_menu.add_command(
                label="Clear Spell Cache",
                command=lambda: self._handle_cache_clear('spell')
            )

            # Add Clear Item Cache command 
            self.options_menu.add_command(
                label="Clear Item Cache",
                command=lambda: self._handle_cache_clear('item')
            )

            # Add Clear All Cache command
            self.options_menu.add_command(
                label="Clear All Cache", 
                command=lambda: self._handle_cache_clear('all')
            )

            # Position and display the menu
            x = self.options_button.winfo_rootx()
            y = self.options_button.winfo_rooty() + self.options_button.winfo_height()
            self.options_menu.post(x, y)
            self._menu_visible = True
            self.needs_menu_check = True
            
        except Exception as e:
            logging.error(f"Error showing options menu: {e}", exc_info=True)

    def _close_menu(self, event=None):
        """Close the options menu when clicking outside"""
        if hasattr(self, '_menu_visible') and self._menu_visible:
            # Check if click was on the options button
            if event and event.widget == self.options_button:
                return
            self.options_menu.unpost()
            self._menu_visible = False
            self.root.unbind('<Button-1>')

    # Color Configuration Methods
    def get_dropdown_colors(self):
        """Get color configuration for dropdown menus"""
        colors = DARK_MODE_COLORS if self.dark_mode_var.get() else LIGHT_MODE_COLORS
        return {
            'fg_color': colors['dropdown_bg'],
            'button_color': colors['dropdown_button'],
            'button_hover_color': colors['dropdown_hover'],
            'dropdown_fg_color': colors['dropdown_bg'],
            'dropdown_hover_color': colors['dropdown_hover'],
            'text_color': colors['fg'],
            'corner_radius': 0,
            'height': 25,
            'width': 200,
            'dropdown_text_color': colors['fg']
        }

    def get_entry_colors(self):
        """Get color configuration for entry fields"""
        colors = DARK_MODE_COLORS if self.dark_mode_var.get() else LIGHT_MODE_COLORS
        return {
            'fg_color': colors['entry_bg'],
            'text_color': colors['fg'],
            'border_color': colors['entry_border'],
            'border_width': 0,
            'corner_radius': 0,
            'height': 25,
            'width': 200
        }

    def get_button_colors(self):
        """Get color configuration for buttons"""
        colors = DARK_MODE_COLORS if self.dark_mode_var.get() else LIGHT_MODE_COLORS
        return {
            'corner_radius': 10,
            'fg_color': colors['button_bg'],
            'hover_color': colors['button_hover'],
            'text_color': colors['button_text'],
            'border_width': 0
        }

    def get_text_colors(self):
        """Get color configuration for text widgets"""
        colors = DARK_MODE_COLORS if self.dark_mode_var.get() else LIGHT_MODE_COLORS
        return {
            'bg': colors['text_bg'],
            'fg': colors['fg'],
            'insertbackground': colors['fg'],
            'selectbackground': colors['text_select_bg'],
            'selectforeground': colors['text_select_fg']
        }

    # Event Handler Methods
    @debug_log
    def _on_enter(self, event):
        """Handle mouse enter event for hyperlinks"""
        try:
            logging.debug("Mouse entered hyperlink area")
            self.results_text.config(cursor="hand2")
        except Exception as e:
            logging.error(f"Error handling mouse enter: {e}", exc_info=True)

    @debug_log
    def _on_leave(self, event):
        """Handle mouse leave event for hyperlinks"""
        try:
            logging.debug("Mouse left hyperlink area")
            self.results_text.config(cursor="")
        except Exception as e:
            logging.error(f"Error handling mouse leave: {e}", exc_info=True)

    @debug_log
    def _on_click(self, event):
        """Handle click event for hyperlinks"""
        try:
            index = self.results_text.index(f"@{event.x},{event.y}")
            tags = self.results_text.tag_names(index)
            logging.debug(f"Click event at index {index} with tags: {tags}")
            for tag in tags:
                if tag.startswith("link-"):
                    url = self.hyperlink_urls.get(tag)
                    if url:
                        logging.debug(f"Opening URL: {url}")
                        webbrowser.open_new(url)
                        break
        except Exception as e:
            logging.error(f"Error handling hyperlink click: {e}", exc_info=True)

    # Text and Hyperlink Handling Methods
    @debug_log
    def insert_hyperlink(self, text, url):
        """Insert a hyperlink into the text widget"""
        try:
            tag_name = f"link-{len(self.hyperlink_urls)}"
            logging.debug(f"Inserting hyperlink for: {text}")
            logging.debug(f"URL: {url}")
            self.results_text.insert(tk.END, text, ("hyperlink", tag_name))
            self.hyperlink_urls[tag_name] = url
        except Exception as e:
            logging.error(f"Error inserting hyperlink: {e}", exc_info=True)

    @debug_log
    def insert_similar_item_hyperlink(self, item_name):
        """Insert a hyperlink for a similar item"""
        try:
            tag_name = f"similar-link-{len(self.hyperlink_urls)}"
            logging.debug(f"Inserting similar item hyperlink: {item_name}")
            self.results_text.insert(tk.END, item_name + "\n", ("hyperlink", tag_name))
            self.hyperlink_urls[tag_name] = item_name
            self.results_text.tag_bind(tag_name, "<Button-1>", 
                                    lambda e, name=item_name: self.search_similar_item(name))
        except Exception as e:
            logging.error(f"Error inserting similar item hyperlink: {e}", exc_info=True)

    @debug_log
    def search_similar_item(self, item_name):
        """Update the item name entry and trigger a search"""
        try:
            logging.debug(f"Searching for similar item: {item_name}")
            self.item_name.set(item_name)
            self.search_item()
        except Exception as e:
            logging.error(f"Error searching similar item: {e}", exc_info=True)

    # UI Feedback and Validation Methods
    @debug_log
    def _handle_cache_clear(self, cache_type):
        """Handle cache clearing through DataManager"""
        try:
            # Get cache statistics
            if cache_type == 'all':
                stats = self.data_manager.get_cache_stats('all')
                confirm_message = (
                    f"Are you sure you want to clear all caches?\n\n"
                    f"Items in cache: {stats['items']}\n"
                    f"Spells in cache: {stats['spells']}\n"
                    f"Total entries: {stats['total']}"
                )
            else:
                count, age = self.data_manager.get_cache_stats(cache_type)
                confirm_message = (
                    f"Are you sure you want to clear the {cache_type} cache?\n\n"
                    f"Entries in cache: {count}\n"
                    f"Oldest entry: {age:.1f} hours old"
                )
            
            logging.debug(f"Starting cache clear operation for: {cache_type}")
            logging.debug(f"DataManager instance: {self.data_manager}")
            logging.debug(f"DataManager cache managers - Item: {self.data_manager.cache_manager}, Spell: {self.data_manager.spell_cache_manager}")
            
            # Get current theme colors
            colors = DARK_MODE_COLORS if self.dark_mode_var.get() else LIGHT_MODE_COLORS
            button_colors = self.get_button_colors()
            logging.debug(f"Using theme colors: {colors['button_bg']}")
            
            # Ask for confirmation before clearing
            logging.debug("Showing confirmation dialog")
            confirm = CTkMessagebox(
                master=None,
                title="Confirm Cache Clear",
                message=confirm_message,
                icon="question",
                option_1="Yes",
                option_2="No",
                button_color=button_colors["fg_color"],
                button_hover_color=button_colors["hover_color"],
                button_text_color=button_colors["text_color"],
                button_width=60
            )
            
            response = confirm.get()
            logging.debug(f"User response: {response}")
            
            if response == "Yes":
                logging.debug(f"Processing cache clear for type: {cache_type}")
                if cache_type == 'spell':
                    logging.debug("Clearing spell cache")
                    success, cleared = self.data_manager.clear_spell_cache()
                    logging.debug(f"Spell cache clear result - Success: {success}, Cleared: {cleared}")
                    if success:
                        if cleared > 0:
                            CTkMessagebox(
                                master=None,
                                title="Success", 
                                message=f"Cleared {cleared} spell cache entries",
                                button_color=button_colors["fg_color"],
                                button_hover_color=button_colors["hover_color"],
                                button_text_color=button_colors["text_color"]
                            )
                        else:
                            CTkMessagebox(
                                master=None,
                                title="Info", 
                                message="Spell cache already empty",
                                button_color=button_colors["fg_color"],
                                button_hover_color=button_colors["hover_color"],
                                button_text_color=button_colors["text_color"]
                            )
                elif cache_type == 'item':
                    logging.debug("Clearing item cache")
                    success, cleared = self.data_manager.clear_item_cache()
                    logging.debug(f"Item cache clear result - Success: {success}, Cleared: {cleared}")
                    if success:
                        if cleared > 0:
                            CTkMessagebox(
                                title="Success", 
                                message=f"Cleared {cleared} item cache entries",
                                button_color=button_colors["fg_color"],
                                button_hover_color=button_colors["hover_color"],
                                button_text_color=button_colors["text_color"]
                            )
                        else:
                            CTkMessagebox(
                                master=None,
                                title="Info", 
                                message="Item cache already empty",
                                button_color=button_colors["fg_color"],
                                button_hover_color=button_colors["hover_color"],
                                button_text_color=button_colors["text_color"]
                            )
                else:  # all
                    logging.debug("Clearing all caches")
                    success, counts = self.data_manager.clear_all_caches()
                    logging.debug(f"All cache clear result - Success: {success}, Counts: {counts}")
                    if success:
                        if counts['total'] > 0:
                            CTkMessagebox(
                                master=None,
                                title="Success",
                                message=(f"Cleared {counts['total']} total cache entries\n"
                                        f"Items: {counts['items']}\n"
                                        f"Spells: {counts['spells']}"),
                                button_color=button_colors["fg_color"],
                                button_hover_color=button_colors["hover_color"],
                                button_text_color=button_colors["text_color"]
                            )
                        else:
                            CTkMessagebox(
                                master=None,
                                title="Info", 
                                message="All caches already empty",
                                button_color=button_colors["fg_color"],
                                button_hover_color=button_colors["hover_color"],
                                button_text_color=button_colors["text_color"]
                            )
                
                if not success:
                    logging.error(f"Cache clear operation failed for type: {cache_type}")
                    CTkMessagebox(
                        master=None,
                        title="Error", 
                        message=f"Failed to clear {cache_type} cache", 
                        icon="cancel",
                        button_color=button_colors["fg_color"],
                        button_hover_color=button_colors["hover_color"],
                        button_text_color=button_colors["text_color"]
                    )
                    
        except Exception as e:
            logging.error(f"Error clearing {cache_type} cache: {e}", exc_info=True)
            CTkMessagebox(
                master=None,
                title="Error", 
                message=f"Failed to clear {cache_type} cache", 
                icon="cancel",
                button_color=button_colors["fg_color"],
                button_hover_color=button_colors["hover_color"],
                button_text_color=button_colors["text_color"]
            )

    @debug_log
    def _handle_similar_items(self, html_content):
        """Handle case when no exact item match is found"""
        try:
            similar_items = self.item_parser.process_similar_items(html_content)
            if similar_items and len(similar_items) > 0:
                self.display_similar_items(similar_items)
            else:
                CTkMessagebox(
                    master=None,
                    title="Warning",
                    message="No similar items found",
                    icon="warning"
                )
                self.hide_loading_indicator()
        except Exception as e:
            logging.error(f"Error handling similar items: {e}", exc_info=True)
            self.hide_loading_indicator()

    @debug_log
    def _validate_save_requirements(self):
        """Validate requirements before saving to CSV"""
        try:
            logging.debug("Validating save requirements")
            
            if not self.current_item_data:
                logging.warning("Save attempted without item data")
                CTkMessagebox(
                    master=None,
                    title="Warning", 
                    message="Please search for an item first",
                    icon="warning"
                )
                return False
                    
            if not self.class_var.get() or not self.slot_var.get():
                logging.warning(f"Save attempted with missing selections - Class: {self.class_var.get()}, Slot: {self.slot_var.get()}")
                CTkMessagebox(
                    master=None,
                    title="Warning",
                    message="Please select both class and slot before saving",
                    icon="warning"
                )
                return False
                
            logging.debug("Save requirements validated successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error validating save requirements: {e}", exc_info=True)
            return False

    @debug_log
    def _show_save_success(self, filename):
        """Show success message after saving"""
        try:
            logging.debug(f"Showing save success message for: {filename}")
            
            # If auto-save is enabled, update the search button text
            if self.auto_save_var.get():
                self.root.after(250, lambda: self.search_button.configure(text="Saved!"))
                # Reset button text after 3 seconds
                self.root.after(3000, lambda: self.search_button.configure(text="Search Item"))
            else:
                # Show regular popup for manual saves
                CTkMessagebox(
                    master=None,
                    title="Success",
                    message=f"Saved to {filename}",
                    icon="check"
                )
            logging.info(f"Successfully saved data to {filename}")
        except Exception as e:
            logging.error(f"Error showing save success message: {e}", exc_info=True)

    # Error Handling Methods
    @debug_log
    def _handle_save_error(self, error):
        """Handle save-related errors"""
        try:
            error_msg = f"Failed to save: {str(error)}"
            logging.error(error_msg, exc_info=True)
            CTkMessagebox(
                master=None,
                title="Error",
                message=error_msg,
                icon="cancel"
            )
            logging.debug("Displayed save error message to user")
        except Exception as e:
            logging.error(f"Error handling save error: {e}", exc_info=True)