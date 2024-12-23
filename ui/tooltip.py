# ui/tooltip.py
import tkinter as tk
import customtkinter as ctk
import logging
from utils.decorators import debug_log
from config.settings import DARK_MODE_COLORS, LIGHT_MODE_COLORS

class ToolTip:
    def __init__(self, widget, text):
        """Initialize tooltip for a widget
        
        Args:
            widget: The widget to attach tooltip to
            text: The tooltip text to display
        """
        logging.debug("Initializing ToolTip")
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.visible = False
        
        self._setup_bindings()
        logging.debug(f"ToolTip initialized for text: {text}")

    # Event Binding Methods
    @debug_log
    def _setup_bindings(self):
        """Setup event bindings for the tooltip"""
        try:
            logging.debug("Setting up tooltip bindings")
            # Basic bindings for all widgets
            self.widget.bind('<Enter>', self.show)
            self.widget.bind('<Leave>', self.hide)
            
            # Special handling for CTkOptionMenu
            if isinstance(self.widget, ctk.CTkOptionMenu):
                logging.debug("Setting up additional CTkOptionMenu bindings")
                self._setup_optionmenu_bindings()
                
            logging.debug("Tooltip bindings setup complete")
        except Exception as e:
            logging.error(f"Error setting up tooltip bindings: {e}", exc_info=True)

    @debug_log
    def _setup_optionmenu_bindings(self):
        """Setup additional bindings for CTkOptionMenu"""
        try:
            logging.debug("Setting up CTkOptionMenu specific bindings")
            # Bind to option menu events
            self.widget.bind('<<ComboboxSelected>>', lambda e: self.force_hide())
            self.widget.bind('<Button-1>', lambda e: self.force_hide())
            
            # Bind to root window events
            root = self.widget.winfo_toplevel()
            root.bind('<Button-1>', lambda e: self.force_hide(), '+')
            root.bind('<Configure>', lambda e: self.force_hide(), '+')
            logging.debug("CTkOptionMenu bindings setup complete")
        except Exception as e:
            logging.error(f"Error setting up optionmenu bindings: {e}", exc_info=True)

    # Display Methods
    @debug_log
    def show(self, event=None):
        """Show the tooltip"""
        if not self.visible:
            try:
                logging.debug("Calculating tooltip position")
                # Get widget position and dimensions
                x = self.widget.winfo_rootx()
                y = self.widget.winfo_rooty()
                height = self.widget.winfo_height()
                
                # Get screen dimensions
                screen_width = self.widget.winfo_screenwidth()
                screen_height = self.widget.winfo_screenheight()
                logging.debug(f"Screen dimensions: {screen_width}x{screen_height}")
                
                # Create tooltip window
                logging.debug("Creating tooltip window")
                self.tooltip = tk.Toplevel(self.widget)
                self.tooltip.wm_overrideredirect(True)
                
                # Get current theme colors
                appearance_mode = ctk.get_appearance_mode()
                colors = DARK_MODE_COLORS if appearance_mode == "Dark" else LIGHT_MODE_COLORS
                
                # Configure tooltip window
                self.tooltip.configure(
                    bg=colors["tooltip_bg"],
                    borderwidth=0,
                    highlightthickness=0
                )
                
                # Create tooltip label
                label = tk.Label(
                    self.tooltip, 
                    text=self.text,
                    bg=colors["tooltip_bg"],
                    fg=colors["fg"],
                    justify="left",
                    padx=5,
                    pady=2,
                    borderwidth=0,
                    highlightthickness=0
                )
                label.pack()
                
                # Calculate position
                logging.debug("Calculating final tooltip position")
                self.tooltip.update_idletasks()
                tooltip_width = self.tooltip.winfo_width()
                tooltip_height = self.tooltip.winfo_height()
                
                x_pos = x + 25
                y_pos = y + height + 5
                
                # Adjust if tooltip would go off screen
                if x_pos + tooltip_width > screen_width:
                    logging.debug("Adjusting x position to prevent off-screen")
                    x_pos = screen_width - tooltip_width - 10
                
                if y_pos + tooltip_height > screen_height:
                    logging.debug("Adjusting y position to prevent off-screen")
                    y_pos = y - tooltip_height - 5
                
                self.tooltip.wm_geometry(f"+{x_pos}+{y_pos}")
                self.visible = True
                logging.debug(f"Tooltip displayed at position: {x_pos},{y_pos}")
                
            except Exception as e:
                logging.error(f"Error showing tooltip: {e}", exc_info=True)

    @debug_log
    def hide(self, event=None):
        """Hide the tooltip"""
        if self.tooltip and self.visible:
            try:
                logging.debug("Hiding tooltip")
                self.tooltip.destroy()
                self.tooltip = None
                self.visible = False
                logging.debug("Tooltip hidden successfully")
            except Exception as e:
                logging.error(f"Error hiding tooltip: {e}", exc_info=True)

    @debug_log
    def force_hide(self):
        """Force hide the tooltip regardless of mouse position"""
        if self.tooltip:
            try:
                logging.debug("Force hiding tooltip")
                self.tooltip.destroy()
                self.tooltip = None
                self.visible = False
                logging.debug("Tooltip force hidden successfully")
            except Exception as e:
                logging.error(f"Error force hiding tooltip: {e}", exc_info=True)