# utils/csv_viewer.py

# Imports section
import pandas as pd
import logging
import webbrowser
import ast
import customtkinter as ctk
import os
from datetime import datetime

from config.settings import DARK_MODE_COLORS, LIGHT_MODE_COLORS, DARK_CSV_CATEGORY_COLORS, LIGHT_CSV_CATEGORY_COLORS
from config.constraints import STAT_CATEGORIES, DISPLAY_ORGANIZATION
from utils.decorators import debug_log
from ui.tooltip import ToolTip
from ui.CTkXYFrame.CTkXYFrame import CTkXYFrame

class CSVViewer:
    """Class for handling CSV viewing functionality"""

    # Initialization and Core Methods
    # -----------------------------
    # __init__, set_colorize, load_csv
    @debug_log
    def __init__(self):
        self.stat_categories = STAT_CATEGORIES
        self.category_headers = []
        self.column_headers = []
        self.slot_headers = []
        self.data_rows = []
        self.tooltips = {}
        self._effect_details_cols = []
        self.viewer = None
        self.df = None
        self.colorize = False
        self.current_file = None
        self.last_modified = None
        self.has_bard_skills = False
        logging.debug("Initializing CSV viewer")

    @debug_log
    def set_colorize(self, value):
        """Set the colorize state"""
        self.colorize = value
        logging.debug(f"CSV colorize set to: {value}")

    @debug_log
    def load_csv(self, class_name):
        try:
            # Format class name to use underscore instead of space
            formatted_class = class_name.lower().replace(' ', '_')
            filename = f"{formatted_class}_gear_comparison.csv"
            self.current_file = filename
            # Only load columns we need
            needed_cols = ['Slot']  # Add Slot column
            for category in self.stat_categories.values():
                needed_cols.extend(category)
                
            # Add bard skill columns explicitly
            if class_name.lower() == 'bard':
                for skill in self.stat_categories['bard_skills']:
                    needed_cols.append(f"BARD_{skill}")
            
            df = pd.read_csv(filename, 
                            usecols=lambda x: x in needed_cols or 
                                            x.endswith('_DETAILS') or 
                                            x.startswith('BARD_'),
                            na_filter=False,
                            memory_map=True,
                            low_memory=False,
                            engine='c')
            
            logging.debug(f"Successfully loaded CSV for {class_name}")
            logging.debug(f"Loaded columns: {df.columns.tolist()}")

            # Store initial file state for change detection
            self.last_modified = os.path.getmtime(filename)
            return df
        except Exception as e:
            logging.error(f"Failed to load CSV: {e}")
            return None
        
    @debug_log
    def start_file_monitor(self, viewer):
        """Start monitoring CSV file for changes"""
        if self.current_file and self.viewer:
            self._check_file_changes()
            # Schedule next check in 1 second
            viewer.after(1000, lambda: self.start_file_monitor(viewer))

    @debug_log
    def _check_file_changes(self):
        """Check if CSV file has been modified"""
        try:
            if not self.current_file or not os.path.exists(self.current_file):
                return
                
            current_mtime = os.path.getmtime(self.current_file)
            
            if self.last_modified is None:
                self.last_modified = current_mtime
                return
                
            if current_mtime > self.last_modified:
                logging.debug(f"CSV file changed: {self.current_file}")
                self.last_modified = current_mtime
                self._refresh_display()
                
        except Exception as e:
            logging.error(f"Error checking file changes: {e}", exc_info=True)

    @debug_log
    def _refresh_display(self):
        """Refresh the CSV display"""
        try:
            if self.viewer and self.current_file:
                # Reload the data
                class_name = os.path.basename(self.current_file).split('_')[0]
                new_df = self.load_csv(class_name)
                
                if new_df is not None:
                    self.df = new_df
                    # Update the display
                    self.display_csv_data(
                        self.viewer,
                        self.df,
                        dark_mode=ctk.get_appearance_mode() == "Dark",
                        colorize=self.colorize
                    )
                    logging.debug("CSV display refreshed successfully")
                    
        except Exception as e:
            logging.error(f"Error refreshing display: {e}", exc_info=True)        

    # Display Setup Methods
    # -------------------
    # Methods for setting up the display environment and frame structure
    @debug_log
    def _setup_display_environment(self, viewer, dark_mode):
        """Setup initial display environment"""
        viewer.update_idletasks()
        for widget in viewer.winfo_children():
            widget.destroy()
        ctk.set_appearance_mode("Dark" if dark_mode else "Light")

    @debug_log
    def _create_frame_structure(self, viewer, colors):
        """Create and return main frame and scroll frame"""
        # Create main frame
        main_frame = ctk.CTkFrame(viewer, fg_color=colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure main frame grid
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Create scrollable frame
        scroll_frame = CTkXYFrame(
            main_frame,
            fg_color=colors['bg'],
            width=1280,
            height=800
        )
        scroll_frame.pack(fill='both', expand=True)
        
        return main_frame, scroll_frame

    @debug_log
    def _init_widget_storage(self):
        """Initialize storage for widgets"""
        self.category_headers = []
        self.column_headers = []
        self.slot_headers = []
        self.data_rows = []
        self.tooltips = {}

    # Header Processing Methods
    # -----------------------
    # format_header_text, format_effect_text, and other header-related methods
    @debug_log
    def format_header_text(self, text):
        """Format header text to split double words and ensure uppercase"""
        text = text.upper()
        
        if text.startswith('BARD_'):
            skill_name = text.replace('BARD_', '')
            skill_name = skill_name.split(' ')[0]
            return skill_name
        elif '_' in text:
            words = text.split('_')
            return '\n'.join(words)
        elif ' ' in text:
            words = text.split(' ')
            return '\n'.join(words)
        elif text == 'ENDURANCE':
            return 'END'
        return text

    @debug_log
    def _format_aug_slots(self, row_data):
        """Format augmentation slot data with tooltip"""
        aug_slots = []
        tooltip_text = []
        
        for slot_num in range(1, 6):  # For slots 1-5
            slot_col = f"SLOT {slot_num}"
            if slot_col in row_data and row_data[slot_col].strip():
                aug_slots.append(str(slot_num))
                # Remove redundant "Type" text but keep "TYPE" prefix
                type_value = row_data[slot_col].upper().replace('TYPE ', '').strip()
                tooltip_text.append(f"SLOT {slot_num} : TYPE {type_value}")
        
        return ','.join(aug_slots), '\n'.join(tooltip_text)

    @debug_log
    def format_effect_text(self, text):
        """Format effect text to split on parentheses"""
        if '(' in text and ')' in text:
            main_text, paren_text = text.split('(', 1)
            return f"{main_text.strip()}\n({paren_text}"
        return text
    
    # Category Processing Methods
    # -------------------------
    # Methods for processing different categories (basic, bard, effects, etc)
    @debug_log
    def _create_category_headers(self, scroll_frame, category_name, cols_present, current_col, colors, subcategories=None):
        """Create main section, subcategory, and column headers"""
        # Row 0 - Main section header
        header_text = self.format_header_text(category_name)
        section_header = ctk.CTkLabel(
            scroll_frame,
            text=header_text,
            font=('Arial', 14, 'bold'),
            fg_color=colors['header'],
            text_color=DARK_MODE_COLORS['fg'] if ctk.get_appearance_mode() == "Dark" else LIGHT_MODE_COLORS['fg'],
            padx=10,
            pady=0,
            corner_radius=0,
            width=0,
            anchor="center",
            justify="center"
        )
        section_header.grid(row=0, column=current_col, columnspan=len(cols_present),
                        sticky='nsew', padx=1, pady=1, ipadx=4)
        self.category_headers.append(section_header)
        
        # Row 1 - Subcategory headers or empty row
        if subcategories:
            # Calculate columns per subcategory
            cols_per_subcategory = {}
            current_subcol = current_col
            for subcat in subcategories:
                if subcat == 'bard_skills':
                    # For bard skills, check for BARD_ prefix
                    subcols = [col for col in cols_present if col.startswith('BARD_')]
                else:
                    # For other categories, check against stat_categories
                    subcols = [col for col in cols_present if col in self.stat_categories[subcat]]
                
                if subcols:
                    cols_per_subcategory[subcat] = {
                        'cols': subcols,
                        'start': current_subcol,
                        'span': len(subcols)
                    }
                    current_subcol += len(subcols)
            
            # Create subcategory headers
            for subcat, info in cols_per_subcategory.items():
                if subcat == 'bard_skills' and self.has_bard_skills:
                    subcat_text = 'INSTRUMENT\nMODS'
                else:
                    subcat_text = self.format_header_text(subcat.upper().replace('_', ' '))
                
                # Get subcategory-specific color
                if isinstance(colors['category'], dict):
                    subcat_color = colors['category'][subcat]  # Direct access since we know the key exists
                else:
                    subcat_color = colors['category']

                subcat_header = ctk.CTkLabel(
                    scroll_frame,
                    text=subcat_text,
                    font=('Arial', 12, 'bold'),
                    fg_color=subcat_color,
                    text_color=DARK_MODE_COLORS['fg'] if ctk.get_appearance_mode() == "Dark" else LIGHT_MODE_COLORS['fg'],
                    padx=10,
                    pady=0,
                    corner_radius=0,
                    width=0,
                    anchor="center",
                    justify="center"
                )
                subcat_header.grid(row=1, column=info['start'], columnspan=info['span'],
                            sticky='nsew', padx=1, pady=1, ipadx=4)
                self.category_headers.append(subcat_header)
        else:
            # Empty middle row for single categories
            empty_header = ctk.CTkLabel(
                scroll_frame,
                text="",
                font=('Arial', 12, 'bold'),
                fg_color=colors['category'],
                text_color=DARK_MODE_COLORS['fg'] if ctk.get_appearance_mode() == "Dark" else LIGHT_MODE_COLORS['fg'],
                padx=10,
                pady=0,
                corner_radius=0,
                width=0,
                anchor="center",
                justify="center"
            )
            empty_header.grid(row=1, column=current_col, columnspan=len(cols_present),
                        sticky='nsew', padx=1, pady=1, ipadx=4)
            self.category_headers.append(empty_header)
        
        # Row 2 - Column headers
        for col_idx, col in enumerate(cols_present):
            col_text = self.format_header_text(col)
            
            # Get appropriate cell color based on category type
            if isinstance(colors['cell'], dict):
                # Find which subcategory this column belongs to
                for subcat in subcategories:
                    if col in self.stat_categories.get(subcat, []) or \
                    (subcat == 'bard_skills' and col.startswith('BARD_')):
                        cell_color = colors['cell'][subcat]
                        break
                else:
                    cell_color = colors['cell']  # Fallback
            else:
                cell_color = colors['cell']

            col_header = ctk.CTkLabel(
                scroll_frame,
                text=col_text,
                font=('Arial', 10, 'bold'),
                fg_color=cell_color,
                text_color=DARK_MODE_COLORS['fg'] if ctk.get_appearance_mode() == "Dark" else LIGHT_MODE_COLORS['fg'],
                padx=10,
                pady=0,
                corner_radius=0,
                width=0,
                anchor="center",
                justify="center"
            )
            col_header.grid(row=2, column=current_col + col_idx,
                        sticky='nsew', padx=1, pady=1, ipadx=4)
            self.column_headers.append(col_header)
    
    @debug_log
    def _get_category_columns(self, category, cols, df):
        """Get columns present in the dataframe for a given category"""
        cols_present = []
        
        # Special handling for effects
        if category == 'effects':
            for col in cols:
                details_col = f"{col}_DETAILS"
                if details_col in df.columns:
                    # Store the details column for later use
                    self._effect_details_cols.append(details_col)
                    # Create virtual effect column from details
                    cols_present.append(col)
                    # Add the effect name from the details column to the DataFrame
                    effect_data = df[details_col].apply(lambda x: 
                        ast.literal_eval(x)['name'] if x and not pd.isna(x) else '')
                    df[col] = effect_data
        else:
            # Normal column handling
            for col in cols:
                if col in df.columns:
                    cols_present.append(col)
                    
            # Special handling for augmentation slots
            if category == 'basic_info':
                slot_cols = [f"SLOT {i}" for i in range(1, 6)]
                if all(slot in cols_present for slot in slot_cols):
                    cols_present = [col for col in cols_present if col not in slot_cols]
                    cols_present.append('AUG SLOTS')
                    
        return cols_present

    @debug_log
    def _get_bard_skill_columns(self, df):
        """Get bard skill columns"""
        cols_present = []
        bard_cols = [col for col in df.columns if col.startswith('BARD_')]
        
        for col in bard_cols:
            if 'UNKNOWN (50)' in col:
                cols_present.append('BARD_ALL INSTRUMENTS')
            else:
                cols_present.append(col)
                
        # Sort according to STAT_CATEGORIES order
        ordered_cols = []
        for stat_col in self.stat_categories['bard_skills']:
            full_col = f"BARD_{stat_col}"
            if full_col in cols_present:
                ordered_cols.append(full_col)
        return ordered_cols

    @debug_log
    def _get_effect_columns(self, cols, df):
        """Get effect columns"""
        cols_present = []
        for col in cols:
            if col in df.columns:
                cols_present.append(col)
                # Add details column to internal tracking but don't display it
                details_col = f"{col}_DETAILS"
                if details_col in df.columns:
                    self._effect_details_cols.append(details_col)
        return cols_present

    @debug_log
    def _get_category_colors(self, category_name, dark_mode, colorize):
        """Get colors for a category"""
        base_colors = DARK_MODE_COLORS if dark_mode else LIGHT_MODE_COLORS
        
        if not colorize:
            return {
                'header': base_colors['csv_top_header_bg'],
                'category': base_colors['csv_category_bg'],
                'cell': base_colors['csv_item_bg']
            }
                
        colors_set = DARK_CSV_CATEGORY_COLORS if dark_mode else LIGHT_CSV_CATEGORY_COLORS
        
        # Handle slot category directly
        if category_name == 'slot':
            return colors_set['slot']
        
        # Find the parent section for subcategories
        for section, config in DISPLAY_ORGANIZATION.items():
            if category_name in config['categories']:
                if section not in colors_set:
                    continue
                    
                category_colors = colors_set[section]
                
                # For multi-category sections (secondary_stats, skill_modifiers)
                if isinstance(category_colors['category'], dict):
                    # Return the entire color structure for the section
                    return category_colors
                # For single category sections
                else:
                    return category_colors
                        
        # If category_name is a main section
        if category_name in colors_set:
            return colors_set[category_name]
                    
        # Fallback to base colors if not found
        return {
            'header': base_colors['csv_top_header_bg'],
            'category': base_colors['csv_category_bg'],
            'cell': base_colors['csv_item_bg']
        }

    # Cell Creation Methods
    # -------------------
    # Methods for creating different types of cells (standard, URL, effects)
    @debug_log
    def _create_cell(self, scroll_frame, value, cell_color, colors, row, col):
        """Create standard cell widget"""
        cell = ctk.CTkLabel(
            scroll_frame,
            text=value if value.strip() else ' ',
            font=('Arial', 10),
            fg_color=cell_color,
            text_color=colors['fg'],
            padx=2,
            pady=0,
            corner_radius=0,
            width=0,
            anchor="center",
            justify="center"
        )
        cell.grid(row=row, column=col, sticky='nsew', padx=1, pady=1, ipadx=4)
        self.data_rows.append(cell)
        return cell

    @debug_log
    def _create_url_cell(self, scroll_frame, url, row, col, colors):
        """Create URL button cell"""
        link = ctk.CTkButton(
            scroll_frame,
            text="LINK",
            command=lambda url=url: webbrowser.open(url),
            width=50,
            height=24,
            fg_color=colors['button_bg'],
            text_color=colors['fg']
        )
        link.grid(row=row, column=col, sticky='nsew', padx=1, pady=1)
        self.data_rows.append(link)
        return link
    
    @debug_log
    def _create_effect_cell(self, scroll_frame, col, row_data, current_row, current_col, colors):
        """Create effect cell with tooltip"""
        try:
            base_colors = DARK_MODE_COLORS if ctk.get_appearance_mode() == "Dark" else LIGHT_MODE_COLORS
            
            details_value = row_data.get(f"{col}_DETAILS")
            if pd.isna(details_value) or details_value == '':
                cell = self._create_cell(
                    scroll_frame,
                    ' ',
                    colors['cell'],
                    base_colors,
                    current_row,
                    current_col
                )
                return cell

            effect_dict = ast.literal_eval(details_value)
            display_text = effect_dict.get('name', ' ')
            effects_list = effect_dict.get('effects', [])
            
            cell = self._create_cell(
                scroll_frame,
                display_text,
                colors['cell'],
                base_colors,
                current_row,
                current_col
            )

            if effects_list:
                # Clean up the effects list text
                tooltip_text = '\n'.join(effect.strip("'[]") for effect in effects_list)
                
                # Create tooltip
                tooltip = ToolTip(cell, tooltip_text)
                
                # Store tooltip reference
                self.tooltips[cell] = tooltip
                    
            return cell

        except Exception as e:
            logging.error(f"Error creating effect cell: {e}")
            base_colors = DARK_MODE_COLORS if ctk.get_appearance_mode() == "Dark" else LIGHT_MODE_COLORS
            return self._create_cell(
                scroll_frame,
                ' ',
                colors['cell'],
                base_colors,
                current_row,
                current_col
            )
    
    @debug_log
    def _create_slot_label(self, scroll_frame, slot_name, slot_group, current_row, colors_set, colors, colorize):
        """Create slot label"""
        slot_label = ctk.CTkLabel(
            scroll_frame,
            text=slot_name,
            font=('Arial', 10, 'bold'),
            fg_color=colors_set['slot']['cell'] if colorize else colors['csv_category_bg'],
            text_color=colors['fg'],
            padx=10
        )
        slot_label.grid(row=current_row, 
                    column=0,
                    rowspan=len(slot_group),
                    sticky='nsew', 
                    padx=1, pady=1)
        self.slot_headers.append(slot_label)

    # Value Formatting Methods
    # ----------------------
    # Methods for formatting different types of values
    @debug_log
    def _format_value(self, value, is_bard_skill=False):
        """Format cell value based on type"""
        if not value.strip():
            return ' '
        
        if is_bard_skill:
            return self._format_bard_skill_value(value)
        
        return self._format_numeric_value(value)

    @debug_log
    def _format_bard_skill_value(self, value):
        """Format bard skill value with percentage"""
        if not value.endswith('%') and value.strip():
            return f"{value}%"
        return value

    @debug_log
    def _format_numeric_value(self, value):
        """Format numeric value removing unnecessary decimals"""
        try:
            if '.' in value:
                numeric_value = float(value)
                if numeric_value.is_integer():
                    return str(int(numeric_value))
        except ValueError:
            pass
        return value

    @debug_log
    def _process_effect_details(self, details_value):
        """Process effect details from JSON-like string"""
        try:
            if pd.isna(details_value) or details_value == '':
                return ' ', None
                
            effect_dict = ast.literal_eval(details_value)
            display_text = effect_dict.get('name', ' ')
            tooltip_text = '\n'.join(effect_dict.get('effects', []))
            
            return display_text, tooltip_text if tooltip_text else None
        except:
            logging.error(f"Error parsing effect details: {details_value}")
            return ' ', None

    # Layout Configuration Methods
    # --------------------------
    # Methods for configuring grid weights and frame layouts
    @debug_log
    def _configure_grid_weights(self, scroll_frame, main_frame):
        """Configure grid weights for all frames"""
        # Configure scroll frame grid weights
        scroll_frame.grid_columnconfigure(0, weight=1)  # Slot column
        for i in range(scroll_frame.grid_size()[0]):
            scroll_frame.grid_columnconfigure(i, weight=1)
            scroll_frame.grid_rowconfigure(i, weight=1)

        # Configure main frame grid weights
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Configure parent frame grid weights (specific to CTkXYFrame)
        scroll_frame.parent_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.parent_frame.grid_columnconfigure(0, weight=1)

    @debug_log
    def _configure_frame_expansion(self, scroll_frame, main_frame):
        """Configure frame expansion settings"""
        scroll_frame.pack(fill='both', expand=True)
        main_frame.pack(fill='both', expand=True)

    # Main Display Method
    # -----------------
    # display_csv_data
    @debug_log
    def display_csv_data(self, viewer, df, dark_mode=False, colorize=False):
        """Display CSV data in the viewer window"""
        logging.debug(f"Displaying CSV with colorize={colorize}")

        if df is None:
            logging.error("No dataframe provided to display_csv_data")
            return

        self.viewer = viewer
        self.df = df

        try:
            # Setup display environment
            self._setup_display_environment(viewer, dark_mode)
            
            # Get colors for current mode
            colors = DARK_MODE_COLORS if dark_mode else LIGHT_MODE_COLORS
            
            # Create frame structure
            main_frame, scroll_frame = self._create_frame_structure(viewer, colors)
            
            # Initialize widget storage
            self._init_widget_storage()
            
            # Process categories and create headers
            category_positions = self._process_categories(scroll_frame, df, dark_mode, colorize)
            
            # Display data rows
            self._display_data_rows(scroll_frame, df, category_positions, dark_mode, colorize)
            
            # Configure final layout
            self._configure_grid_weights(scroll_frame, main_frame)

            # Initialize automatic refresh monitoring
            self.start_file_monitor(viewer)
            
        except Exception as e:
            logging.error(f"Error displaying CSV data: {e}")
            raise

    @debug_log
    def _process_categories(self, scroll_frame, df, dark_mode, colorize):
        """Process categories and create headers"""
        category_positions = {}
        current_col = 1  # Start at 1 to leave room for slot column

        # Process categories according to DISPLAY_ORGANIZATION
        for section, config in DISPLAY_ORGANIZATION.items():
            display_name = config['display_name']
            categories = config['categories']
            
            # Check for bard skills when processing skill modifiers section
            if section == 'skill_modifiers':
                self.has_bard_skills = any(col.startswith('BARD_') for col in df.columns)
                logging.debug(f"Has bard skills: {self.has_bard_skills}")
            
            # Get all columns present for this section's categories
            section_cols = []
            for category in categories:
                cols = self.stat_categories[category]
                
                # Special handling for bard skills
                if category == 'bard_skills' and self.has_bard_skills:
                    cols_present = [col for col in df.columns if col.startswith('BARD_')]
                else:
                    cols_present = self._get_category_columns(category, cols, df)
                    
                    # Special handling for augmentation slots
                    if category == 'basic_info':
                        slot_cols = [f"SLOT {i}" for i in range(1, 6)]
                        if all(slot in cols_present for slot in slot_cols):
                            cols_present = [col for col in cols_present if col not in slot_cols]
                            cols_present.append('AUG SLOTS')
                
                if cols_present:
                    section_cols.extend(cols_present)
            
            if section_cols:
                # Store position information
                category_positions[section] = {
                    'start_col': current_col,
                    'cols': section_cols,
                    'categories': categories
                }
                
                # Get colors for the section
                colors = self._get_category_colors(categories[0], dark_mode, colorize)
                
                # Create headers with section name and appropriate subcategories
                self._create_category_headers(
                    scroll_frame=scroll_frame,
                    category_name=display_name,
                    cols_present=section_cols,
                    current_col=current_col,
                    colors=colors,
                    subcategories=categories if len(categories) > 1 else None
                )
                
                current_col += len(section_cols)

        return category_positions

    @debug_log
    def _display_data_rows(self, scroll_frame, df, category_positions, dark_mode, colorize):
        """Display data rows for each slot group"""
        colors = DARK_MODE_COLORS if dark_mode else LIGHT_MODE_COLORS
        colors_set = DARK_CSV_CATEGORY_COLORS if dark_mode else LIGHT_CSV_CATEGORY_COLORS
        current_row = 3  # Start after headers

        for slot_name, slot_group in df.groupby('Slot'):
            # Create slot label
            self._create_slot_label(scroll_frame, slot_name, slot_group, current_row, 
                                colors_set, colors, colorize)
            
            # Process each row in the slot group
            for idx, (_, row) in enumerate(slot_group.iterrows()):
                row_num = current_row + idx
                self._process_row(scroll_frame, row, category_positions, row_num, 
                                dark_mode, colorize)
            
            current_row += len(slot_group)

    @debug_log
    def _process_row(self, scroll_frame, row, category_positions, current_row, dark_mode, colorize):
        """Process a single row of data"""
        base_colors = DARK_MODE_COLORS if dark_mode else LIGHT_MODE_COLORS
        
        for category_name, position_info in category_positions.items():
            start_col = position_info['start_col']
            cols_present = position_info['cols']
            categories = position_info['categories']
            category_colors = self._get_category_colors(category_name, dark_mode, colorize)
            
            for col_idx, col in enumerate(cols_present):
                current_col = start_col + col_idx
                
                # Special handling for augmentation slots
                if col == 'AUG SLOTS':
                    slot_cols = [f"SLOT {i}" for i in range(1, 6)]
                    if any(slot in row.index for slot in slot_cols):
                        value, tooltip_text = self._format_aug_slots(row)
                        cell = self._create_cell(scroll_frame, value, category_colors['cell'],
                                            base_colors, current_row, current_col)
                        if tooltip_text:
                            tooltip = ToolTip(cell, tooltip_text)
                            self.tooltips[cell] = tooltip
                    continue
                
                # Determine cell color based on category type
                cell_color = category_colors['cell']
                if isinstance(cell_color, dict):
                    # Find which subcategory this column belongs to
                    for cat in categories:
                        if cat == 'bard_skills':
                            if col.startswith('BARD_'):
                                cell_color = cell_color[cat]
                                break
                        elif col in self.stat_categories.get(cat, []):
                            cell_color = cell_color[cat]
                            break
                
                # Process the cell based on its type
                value = str(row[col])
                if col == 'URL':
                    self._create_url_cell(scroll_frame, value, current_row, current_col, base_colors)
                elif 'EFFECT' in col and not col.endswith('_DETAILS'):
                    self._create_effect_cell(scroll_frame, col, row, current_row, current_col, 
                                        {'cell': cell_color})
                else:
                    formatted_value = self._format_value(value, col.startswith('BARD_'))
                    cell = self._create_cell(scroll_frame, formatted_value, cell_color,
                                        base_colors, current_row, current_col)