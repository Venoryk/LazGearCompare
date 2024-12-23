# ui/widgets.py
import tkinter as tk
import customtkinter as ctk
import logging
from utils.decorators import debug_log
from tkinter.constants import SEL, SEL_FIRST, SEL_LAST, INSERT, END

class ContextMenu:
    def __init__(self, root, dark_mode_var):
        """Initialize context menu with root window and dark mode variable
        
        Args:
            root: Root window instance
            dark_mode_var: BooleanVar for dark mode state
        """
        self.root = root
        self.dark_mode_var = dark_mode_var
        self.debug_var = getattr(root, 'debug_var', None)
        self.setup_menu()

    # Setup Methods
    @debug_log
    def setup_menu(self):
        """Setup right-click context menu"""
        try:
            menu_config = {
                'tearoff': 0,
                'bg': '#2b2b2b' if self.dark_mode_var.get() else 'white',
                'fg': 'white' if self.dark_mode_var.get() else 'black',
                'activebackground': '#404040' if self.dark_mode_var.get() else '#e6e6e6',
                'activeforeground': 'white' if self.dark_mode_var.get() else 'black'
            }
            
            self.menu = tk.Menu(self.root, **menu_config)
            
            # Add menu items
            menu_items = [
                ("Copy", self.copy_text),
                ("Paste", self.paste_text),
                (None, None),  # Separator
                ("Select All", self.select_all_text)
            ]
            
            for label, command in menu_items:
                if label is None:
                    self.menu.add_separator()
                else:
                    self.menu.add_command(label=label, command=command)
            
            logging.debug("Context menu setup complete")
        except Exception as e:
            logging.error(f"Error setting up context menu: {e}")
            raise

    # Menu Display Methods  
    @debug_log
    def show_menu(self, event):
        """Show context menu at cursor position"""
        try:
            widget = event.widget
            if self.debug_var and self.debug_var.get():
                logging.debug(f"Showing menu at x={event.x_root}, y={event.y_root}")
                logging.debug(f"Target widget: {widget.__class__.__name__}")
            
            self.menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            logging.error(f"Error showing context menu: {e}")
            raise

    # Text Operation Methods
    @debug_log
    def copy_text(self):
        """Copy selected text"""
        try:
            widget = self.root.focus_get()
            if isinstance(widget, tk.Text):
                selected = widget.get(SEL_FIRST, SEL_LAST)
                if self.debug_var and self.debug_var.get():
                    logging.debug(f"Copying from Text widget, selection length: {len(selected)}")
            else:
                selected = widget.selection_get()
                if self.debug_var and self.debug_var.get():
                    logging.debug(f"Copying from {widget.__class__.__name__}, selection length: {len(selected)}")
            
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            logging.debug("Text copied to clipboard")
        except tk.TclError:
            logging.debug("No text selected for copy")
        except Exception as e:
            logging.error(f"Error copying text: {e}")
            raise

    @debug_log
    def paste_text(self):
        """Paste text at cursor position"""
        try:
            widget = self.root.focus_get()
            clipboard_content = self.root.clipboard_get()
            
            if self.debug_var and self.debug_var.get():
                logging.debug(f"Paste operation on widget type: {widget.__class__.__name__}")
                logging.debug(f"Clipboard content length: {len(clipboard_content)}")
            
            if isinstance(widget, tk.Text):
                widget.insert(INSERT, clipboard_content)
            else:
                widget.delete(0, END)
                widget.insert(0, clipboard_content)
            logging.debug("Text pasted from clipboard")
        except tk.TclError:
            logging.debug("No text available to paste")
        except Exception as e:
            logging.error(f"Error pasting text: {e}")
            raise

    @debug_log
    def select_all_text(self):
        """Select all text in the widget"""
        try:
            widget = self.root.focus_get()
            if isinstance(widget, tk.Text):
                widget.tag_add(SEL, "1.0", END)
                if self.debug_var and self.debug_var.get():
                    content_length = len(widget.get("1.0", END))
                    logging.debug(f"Selected all text in Text widget, length: {content_length}")
            else:
                widget.select_range(0, END)
                if self.debug_var and self.debug_var.get():
                    content_length = len(widget.get())
                    logging.debug(f"Selected all text in {widget.__class__.__name__}, length: {content_length}")
            logging.debug("All text selected")
        except tk.TclError:
            logging.debug("No text to select")
        except Exception as e:
            logging.error(f"Error selecting all text: {e}")
            raise