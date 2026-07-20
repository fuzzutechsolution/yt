"""
Universal AI Web Scraper - Database Visualizer View
Allows raw inspections of Settings, Logs, and Projects tables.
Provides a console cleaner to optimize system DB storage.
"""

import customtkinter as ctk
import logging
from database import DatabaseManager

logger = logging.getLogger(__name__)

class DatabaseView(ctk.CTkFrame):
    """
    Visualization page representing raw SQLite storage contents.
    Provides controls to purge application log records.
    """
    def __init__(self, parent, status_bar_callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.status_bar_callback = status_bar_callback
        self._db = DatabaseManager.get_instance()

        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title header
        self.grid_rowconfigure(1, weight=0) # Table selector row
        self.grid_rowconfigure(2, weight=1) # Data visualizer scrollable frame

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="SQLITE DATABASE EXPLORER",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#F7FAFC"
        )
        self.title_lbl.grid(row=0, column=0, sticky="w")

        # 2. Selector row
        self.selector_frame = ctk.CTkFrame(self, fg_color="#1A202C", border_width=1, border_color="#2D3748")
        self.selector_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.selector_frame.grid_columnconfigure(2, weight=1)

        self.table_lbl = ctk.CTkLabel(
            self.selector_frame,
            text="Inspect Table:",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#CBD5E0"
        )
        self.table_lbl.grid(row=0, column=0, padx=(20, 10), pady=12, sticky="w")

        # Table Selection Menu
        self.tables = ["System Logs", "Application Settings", "Scrape Runs (Raw)"]
        self.table_menu = ctk.CTkOptionMenu(
            self.selector_frame,
            values=self.tables,
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#4A5568",
            button_color="#2D3748",
            button_hover_color="#1A365D",
            command=lambda v: self.load_selected_table()
        )
        self.table_menu.grid(row=0, column=1, padx=10, pady=12, sticky="w")
        self.table_menu.set(self.tables[0])

        # Delete Logs Action button
        self.clear_logs_btn = ctk.CTkButton(
            self.selector_frame,
            text="🧹 Clear Logs Table",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#2D3748",
            hover_color="#E53E3E",
            width=140,
            command=self.clear_logs
        )
        self.clear_logs_btn.grid(row=0, column=3, padx=(10, 20), pady=12, sticky="e")

        # 3. Dynamic Scrollable Visualizer
        self.visualizer_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A202C",
            border_width=1,
            border_color="#2D3748"
        )
        self.visualizer_frame.grid(row=2, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.visualizer_frame.grid_columnconfigure(0, weight=1)

        # Load initial table data
        self.load_selected_table()

    def clear_logs(self):
        """Purges system logging records to save storage space."""
        self._db.clear_logs()
        logger.info("Logs table cleared successfully.")
        if self.status_bar_callback:
            self.status_bar_callback("Database log cache cleared.", "SUCCESS")
        self.load_selected_table()

    def load_selected_table(self):
        """Loads and visualizes sqlite rows based on dropdown choice."""
        # Clear frame
        for child in self.visualizer_frame.winfo_children():
            child.destroy()

        selected = self.table_menu.get()

        if selected == "System Logs":
            self.clear_logs_btn.configure(state="normal")
            self._render_logs_table()
        elif selected == "Application Settings":
            self.clear_logs_btn.configure(state="disabled")
            self._render_settings_table()
        elif selected == "Scrape Runs (Raw)":
            self.clear_logs_btn.configure(state="disabled")
            self._render_raw_history_table()

    def _render_logs_table(self):
        """Renders standard UI list elements for application trace logs."""
        logs = self._db.get_logs(limit=250)
        if not logs:
            lbl = ctk.CTkLabel(
                self.visualizer_frame,
                text="System logs are currently empty.",
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#718096"
            )
            lbl.pack(pady=40)
            return

        # Header titles
        header = ctk.CTkFrame(self.visualizer_frame, fg_color="#2D3748", corner_radius=4)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.grid_columnconfigure(0, weight=2) # Date
        header.grid_columnconfigure(1, weight=1) # Level
        header.grid_columnconfigure(2, weight=6) # Message
        
        lbl_font = ctk.CTkFont(family="Inter", size=11, weight="bold")
        ctk.CTkLabel(header, text="TIMESTAMP", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header, text="LEVEL", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header, text="TRACE MESSAGE", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=2, padx=10, pady=5, sticky="w")

        # Rows
        for idx, item in enumerate(logs):
            row = ctk.CTkFrame(
                self.visualizer_frame, 
                fg_color="#1D2330" if idx % 2 == 0 else "#141721",
                corner_radius=4
            )
            row.pack(fill="x", padx=10, pady=2)
            row.grid_columnconfigure(0, weight=2)
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=6)

            # Style level text
            level = item["level"]
            lvl_color = "#E53E3E" if level == "ERROR" else ("#DD6B20" if level == "WARNING" else "#A0AEC0")

            ctk.CTkLabel(row, text=item["timestamp"], font=ctk.CTkFont(family="Inter", size=11), text_color="#718096").grid(row=0, column=0, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(row, text=level, font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color=lvl_color).grid(row=0, column=1, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(row, text=item["message"], font=ctk.CTkFont(family="Inter", size=11), text_color="#E2E8F0", anchor="w", justify="left").grid(row=0, column=2, padx=10, pady=4, sticky="w")

    def _render_settings_table(self):
        """Displays key-value settings parameters."""
        settings = self._db.get_all_settings()
        
        # Header titles
        header = ctk.CTkFrame(self.visualizer_frame, fg_color="#2D3748", corner_radius=4)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)
        
        lbl_font = ctk.CTkFont(family="Inter", size=11, weight="bold")
        ctk.CTkLabel(header, text="SETTINGS OPTION KEY", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=0, padx=15, pady=5, sticky="w")
        ctk.CTkLabel(header, text="CURRENT CONFIGURATION", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=1, padx=15, pady=5, sticky="w")

        for idx, (k, v) in enumerate(settings.items()):
            row = ctk.CTkFrame(
                self.visualizer_frame, 
                fg_color="#1D2330" if idx % 2 == 0 else "#141721",
                corner_radius=4
            )
            row.pack(fill="x", padx=10, pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=k.upper(), font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color="#A0AEC0").grid(row=0, column=0, padx=15, pady=6, sticky="w")
            ctk.CTkLabel(row, text=v, font=ctk.CTkFont(family="Inter", size=12), text_color="#63B3ED").grid(row=0, column=1, padx=15, pady=6, sticky="w")

    def _render_raw_history_table(self):
        """Lists raw metadata for runs."""
        records = self._db.get_history(limit=50)
        if not records:
            lbl = ctk.CTkLabel(
                self.visualizer_frame,
                text="No records logged.",
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#718096"
            )
            lbl.pack(pady=40)
            return

        header = ctk.CTkFrame(self.visualizer_frame, fg_color="#2D3748", corner_radius=4)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=3)
        header.grid_columnconfigure(2, weight=1)
        header.grid_columnconfigure(3, weight=1)

        lbl_font = ctk.CTkFont(family="Inter", size=11, weight="bold")
        ctk.CTkLabel(header, text="ID", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header, text="URL / ENDPOINT", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header, text="ITEMS", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(header, text="STATUS CODE", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=3, padx=10, pady=5, sticky="w")

        for idx, item in enumerate(records):
            row = ctk.CTkFrame(
                self.visualizer_frame, 
                fg_color="#1D2330" if idx % 2 == 0 else "#141721",
                corner_radius=4
            )
            row.pack(fill="x", padx=10, pady=2)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=3)
            row.grid_columnconfigure(2, weight=1)
            row.grid_columnconfigure(3, weight=1)

            ctk.CTkLabel(row, text=str(item["id"]), font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#718096").grid(row=0, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(row, text=item["url"][:80], font=ctk.CTkFont(family="Inter", size=11), text_color="#E2E8F0", anchor="w", justify="left").grid(row=0, column=1, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(row, text=str(item["results_count"]), font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#63B3ED").grid(row=0, column=2, padx=10, pady=6, sticky="w")
            
            status = item["status"]
            s_color = "#48BB78" if status == "COMPLETED" else "#E53E3E"
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color=s_color).grid(row=0, column=3, padx=10, pady=6, sticky="w")
