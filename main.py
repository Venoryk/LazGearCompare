import tkinter as tk
import customtkinter as ctk
import logging
import argparse

from CTkMessagebox import CTkMessagebox
from ui.main_window import MainWindow
from utils.logging_config import setup_logging
from utils.decorators import debug_log


@debug_log
def main():
    """Initialize and start the application"""
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser()
        parser.add_argument('--debug', action='store_true', help='Enable debug mode')
        args = parser.parse_args()

        # Initialize logging
        setup_logging(debug_mode=args.debug)
        logging.debug("Logging system initialized")
        
        # Create root window with detailed logging
        logging.debug("Starting root window creation")
        root = ctk.CTk()
        logging.debug("Root window created successfully")
        
        # Initialize main application with detailed logging
        logging.debug("Starting MainWindow initialization")
        app = MainWindow(root)
        app.debug_var.set(args.debug)
        logging.debug("MainWindow initialization complete")
        
        # Set up window closing handler
        logging.debug("Setting up window closing handler")
        def on_closing():
            try:
                logging.debug("Application closing initiated")
                if hasattr(app, 'dropdown_checker'):
                    logging.debug("Canceling pending callbacks")
                    root.after_cancel(app.dropdown_checker)
                logging.debug("Destroying root window")
                root.destroy()
            except Exception as e:
                logging.error(f"Error during window closing: {e}", exc_info=True)
                
        root.protocol("WM_DELETE_WINDOW", on_closing)
        logging.debug("Window closing handler setup complete")
        
        # Start main loop
        logging.debug("Starting main application loop")
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Application startup failed: {e}", exc_info=True)
        CTkMessagebox(
            title="Error",
            message="Application failed to start. Check logs for details.",
            icon="cancel"
        )
        raise

if __name__ == "__main__":
    main()