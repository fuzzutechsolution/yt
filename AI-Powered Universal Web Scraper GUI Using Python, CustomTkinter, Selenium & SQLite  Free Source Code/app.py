"""
Universal AI Web Scraper - Main Application Entry Point
Initializes SQLite schemas, setups root logger streams, and runs the CustomTkinter UI.
"""

import sys
import os
import logging
import customtkinter as ctk

# Ensure workspace packages are discoverable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger import setup_logging
from database import DatabaseManager
from gui import MainGUI

def main():
    # 1. Initialize Loggers
    log_file = "scraper.log"
    setup_logging(log_file=log_file, log_level=logging.INFO)
    logger = logging.getLogger("app_main")
    logger.info("Initializing Application Bootstrap Lifecycle...")

    # 2. Initialize Database Manager (Creates schema if empty)
    try:
        db = DatabaseManager.get_instance()
        logger.info("Local SQLite database initialized successfully.")
    except Exception as e:
        logger.critical(f"Database Initialization Failure: {e}", exc_info=True)
        sys.exit(f"Database Initialization Failure: {e}")

    # 3. Read settings for visual style theme selection
    saved_theme = db.get_setting("theme", "Dark")
    logger.info(f"Loaded appearance configuration: Theme={saved_theme}")

    # Set CustomTkinter globally configured theme styling
    ctk.set_appearance_mode(saved_theme)
    # Slate Blue neon accent theme
    ctk.set_default_color_theme("blue")

    # 4. Initialize Window Shell
    logger.info("Assembling Main Application GUI Shell...")
    app = ctk.CTk()
    app.title("Universal AI Web Scraper - Premium Enterprise Edition")
    
    # Target Resolution 1400x900 (Centred if possible)
    window_width = 1400
    window_height = 900
    
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    
    pos_x = int((screen_width / 2) - (window_width / 2))
    pos_y = int((screen_height / 2) - (window_height / 2))
    
    app.geometry(f"{window_width}x{window_height}+{pos_x}+{pos_y}")
    app.minsize(1200, 800) # Allow reasonable responsiveness down to smaller window sizes

    # 5. Pack MainGUI Frame Wrapper
    gui_main = MainGUI(app)
    gui_main.pack(fill="both", expand=True)

    # Clean shutdown handling
    def on_closing():
        logger.info("Application shutdown requested. Closing active subprocesses...")
        try:
            # Quit active background scraper sessions if running
            if hasattr(gui_main.views["Scraper"], "scraper_engine"):
                gui_main.views["Scraper"].scraper_engine.stop_active_scrape()
        except Exception:
            pass
        app.destroy()
        logger.info("Application terminated. Exiting.")

    app.protocol("WM_DELETE_WINDOW", on_closing)

    # 6. Boot event loop
    logger.info("Main GUI loop executing.")
    app.mainloop()

if __name__ == "__main__":
    main()
