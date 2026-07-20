"""
Universal AI Web Scraper - Main GUI Coordinator
Assembles the Sidebar, Top Navigation, Workspace views, and bottom Status Bar.
Implements tab switching and appearance updates.
"""

import os
import logging
import customtkinter as ctk
from typing import Dict

# Component Imports
from components.sidebar import Sidebar
from components.status_bar import StatusBar

# View Imports
from views.dashboard_view import DashboardView
from views.scraper_view import ScraperView
from views.history_view import HistoryView
from views.database_view import DatabaseView
from views.settings_view import SettingsView
from views.about_view import AboutView

from database import DatabaseManager

logger = logging.getLogger(__name__)

class MainGUI(ctk.CTkFrame):
    """
    Core GUI frame that links the sidebar navigation with the view manager container.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._db = DatabaseManager.get_instance()

        # Grid system: 2 columns (sidebar + content), 3 rows (top nav + content + footer status)
        self.grid_columnconfigure(0, weight=0) # Sidebar column
        self.grid_columnconfigure(1, weight=1) # Main area column
        
        self.grid_rowconfigure(0, weight=0) # Top navigation bar
        self.grid_rowconfigure(1, weight=1) # Main workspace frame
        self.grid_rowconfigure(2, weight=0) # Bottom status bar footer

        # Initialize widgets
        self._build_sidebar()
        self._build_top_nav()
        self._build_workspace_container()
        self._build_status_bar()

        # Show default landing page
        self.show_view("Dashboard")
        self.update_status_metrics()

    # ----------------------------------------------------
    # Construction Methods
    # ----------------------------------------------------

    def _build_sidebar(self):
        """Initializes left navigation bar."""
        self.sidebar = Sidebar(self, select_callback=self.show_view, width=240, fg_color="#1A202C")
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")

    def _build_top_nav(self):
        """Initializes top navigation bar."""
        self.top_nav = ctk.CTkFrame(self, height=70, fg_color="#1A202C", corner_radius=0)
        self.top_nav.grid(row=0, column=1, sticky="ew")
        
        self.top_nav.grid_columnconfigure(0, weight=1)
        self.top_nav.grid_columnconfigure(1, weight=0)

        # Active view title label
        self.nav_title_lbl = ctk.CTkLabel(
            self.top_nav,
            text="DASHBOARD OVERVIEW",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#F7FAFC"
        )
        self.nav_title_lbl.grid(row=0, column=0, padx=30, pady=20, sticky="w")

        # Top Right Actions (Open Folder button)
        self.folder_btn = ctk.CTkButton(
            self.top_nav,
            text="📁 Output Directory",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#2D3748",
            hover_color="#3182CE",
            width=140,
            command=self.open_output_directory
        )
        self.folder_btn.grid(row=0, column=1, padx=30, pady=20, sticky="e")

    def _build_workspace_container(self):
        """Creates the container where child pages will render."""
        self.workspace_container = ctk.CTkFrame(self, fg_color="#171923", corner_radius=0)
        self.workspace_container.grid(row=1, column=1, sticky="nsew")
        
        # Grid settings to allow full expansion of nested frames
        self.workspace_container.grid_columnconfigure(0, weight=1)
        self.workspace_container.grid_rowconfigure(0, weight=1)

        # Instantiate all sub-views under a registry
        self.views: Dict[str, ctk.CTkFrame] = {
            "Dashboard": DashboardView(self.workspace_container),
            "Scraper": ScraperView(self.workspace_container, status_bar_callback=self.update_status_callback),
            "History": HistoryView(self.workspace_container, status_bar_callback=self.update_status_callback),
            "Database": DatabaseView(self.workspace_container, status_bar_callback=self.update_status_callback),
            "Settings": SettingsView(self.workspace_container, status_bar_callback=self.update_status_callback, theme_change_callback=self.change_appearance_mode),
            "About": AboutView(self.workspace_container)
        }

        # Hide all frames initially
        for view_frame in self.views.values():
            view_frame.grid_forget()

    def _build_status_bar(self):
        """Initializes bottom status footer."""
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")

    # ----------------------------------------------------
    # Control Actions & Navigation flow
    # ----------------------------------------------------

    def show_view(self, name: str):
        """Switches the view inside the workspace frame."""
        logger.info(f"Workspace loading view: {name}")

        # Update Top Title
        self.nav_title_lbl.configure(text=f"{name.upper()} WORKSPACE")

        # Hide current active frames
        for view_name, view_frame in self.views.items():
            if view_name == name:
                # Trigger internal load callbacks if the view supports them
                if hasattr(view_frame, "load_statistics"):
                    view_frame.load_statistics()
                elif hasattr(view_frame, "load_history"):
                    view_frame.load_history()
                elif hasattr(view_frame, "load_selected_table"):
                    view_frame.load_selected_table()
                elif hasattr(view_frame, "read_configurations"):
                    view_frame.read_configurations()

                view_frame.grid(row=0, column=0, sticky="nsew")
            else:
                view_frame.grid_forget()

        # Update sidebar active selector state
        self.sidebar.set_active_tab(name)
        self.update_status_metrics()

    def open_output_directory(self):
        """Retrieves default output folder settings and opens in windows Explorer."""
        folder = self._db.get_setting("output_folder", os.getcwd())
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        
        logger.info(f"Opening target exports directory: {folder}")
        try:
            os.startfile(folder)
            self.update_status_callback("Opened exports directory in system browser.", "SUCCESS")
        except Exception as e:
            logger.error(f"Failed to open exports directory: {e}")
            self.update_status_callback("Could not open exports directory.", "ERROR")

    def update_status_callback(self, message: str, state: str = "IDLE"):
        """Safe status update hook passed into views."""
        self.status_bar.set_status(message, state)
        self.update_status_metrics()

    def update_status_metrics(self):
        """Updates configurations displayed in the right slots of the status bar."""
        settings = self._db.get_all_settings()
        browser = settings.get("browser", "Chrome")
        headless = settings.get("headless", "True").lower() == "true"
        
        stats = self._db.get_dashboard_statistics()
        total_runs = stats.get("total_runs", 0)
        
        self.status_bar.update_meta_info(browser, headless, total_runs)

    def change_appearance_mode(self, mode: str):
        """Hook triggers system appearance theme edits (Light/Dark/System)."""
        logger.info(f"Updating application theme appearance: {mode}")
        ctk.set_appearance_mode(mode)
