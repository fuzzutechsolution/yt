"""
Universal AI Web Scraper - Dashboard View
Displays scraper analytics cards and a quick-view table of the latest execution logs.
"""

import customtkinter as ctk
from components.cards import StatCard
from database import DatabaseManager

class DashboardView(ctk.CTkFrame):
    """
    Main overview landing page of the application workspace.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._db = DatabaseManager.get_instance()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title Banner
        self.grid_rowconfigure(1, weight=0) # Card Row
        self.grid_rowconfigure(2, weight=0) # Table Title Row
        self.grid_rowconfigure(3, weight=1) # Recent Table Frame

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(25, 15), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="SYSTEM DASHBOARD",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#F7FAFC"
        )
        self.title_lbl.grid(row=0, column=0, sticky="w")

        # Refresh stats button
        self.refresh_btn = ctk.CTkButton(
            self.header_frame,
            text="🔄 Refresh Stats",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#2D3748",
            hover_color="#1A365D",
            width=120,
            command=self.load_statistics
        )
        self.refresh_btn.grid(row=0, column=1, sticky="e")

        # 2. Stats Grid Row
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        
        # Configure columns for card alignment
        self.cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")

        # Create Stat Cards
        self.card_runs = StatCard(self.cards_frame, "Total Run Executions", "0", "Runs logged in db", "#63B3ED")
        self.card_runs.grid(row=0, column=0, padx=8, pady=5, sticky="ew")

        self.card_success = StatCard(self.cards_frame, "Successful Scrapes", "0", "Completed status", "#48BB78")
        self.card_success.grid(row=0, column=1, padx=8, pady=5, sticky="ew")

        self.card_failed = StatCard(self.cards_frame, "Failure Events", "0", "Failed status code", "#F56565")
        self.card_failed.grid(row=0, column=2, padx=8, pady=5, sticky="ew")

        self.card_items = StatCard(self.cards_frame, "Total Items Extracted", "0", "Structured rows saved", "#ED64A6")
        self.card_items.grid(row=0, column=3, padx=8, pady=5, sticky="ew")

        # 3. Section Title: Recent Executions
        self.sect_title_lbl = ctk.CTkLabel(
            self,
            text="RECENT ACTIVITY HISTORY",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#A0AEC0",
            anchor="w"
        )
        self.sect_title_lbl.grid(row=2, column=0, padx=30, pady=(25, 5), sticky="w")

        # 4. Scrollable Container for recent logs
        self.history_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A202C",
            border_width=1,
            border_color="#2D3748"
        )
        self.history_frame.grid(row=3, column=0, padx=30, pady=(0, 30), sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)

        # Initial stats loading
        self.load_statistics()

    def load_statistics(self):
        """Fetches SQLite metrics and populates the cards and the activity lists."""
        stats = self._db.get_dashboard_statistics()
        
        self.card_runs.update_value(str(stats["total_runs"]))
        self.card_success.update_value(str(stats["successful_runs"]))
        self.card_failed.update_value(str(stats["failed_runs"]))
        self.card_items.update_value(f"{stats['total_items_scraped']:,}")

        # Clear previous rows from scroll frame
        for child in self.history_frame.winfo_children():
            child.destroy()

        history_items = self._db.get_history(limit=8)
        
        if not history_items:
            empty_lbl = ctk.CTkLabel(
                self.history_frame,
                text="No recent scrapers logged. Navigate to the 'Scraper' tab to begin.",
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#718096"
            )
            empty_lbl.pack(pady=40)
            return

        # Render rows dynamically
        for idx, item in enumerate(history_items):
            row_frame = ctk.CTkFrame(
                self.history_frame,
                fg_color="#2D3748" if idx % 2 == 0 else "#1A202C",
                corner_radius=6
            )
            row_frame.pack(fill="x", padx=10, pady=4)
            row_frame.grid_columnconfigure(0, weight=1) # URL / Prompt info
            row_frame.grid_columnconfigure(1, weight=0) # Timestamp
            row_frame.grid_columnconfigure(2, weight=0) # Items count
            row_frame.grid_columnconfigure(3, weight=0) # Status Indicator badge

            # Detail container (Url + prompt description)
            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, padx=15, pady=8, sticky="w")
            
            url_lbl = ctk.CTkLabel(
                info_frame,
                text=item["url"],
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                text_color="#E2E8F0",
                anchor="w",
                justify="left"
            )
            url_lbl.pack(anchor="w")

            prompt_lbl = ctk.CTkLabel(
                info_frame,
                text=f"Prompt: {item['prompt']}",
                font=ctk.CTkFont(family="Inter", size=11),
                text_color="#A0AEC0",
                anchor="w",
                justify="left"
            )
            prompt_lbl.pack(anchor="w")

            # Timestamp Column
            time_lbl = ctk.CTkLabel(
                row_frame,
                text=item["timestamp"],
                font=ctk.CTkFont(family="Inter", size=12),
                text_color="#A0AEC0",
                width=160
            )
            time_lbl.grid(row=0, column=1, padx=15, pady=8)

            # Extracted count
            count_lbl = ctk.CTkLabel(
                row_frame,
                text=f"{item['results_count']} items",
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#63B3ED",
                width=100
            )
            count_lbl.grid(row=0, column=2, padx=15, pady=8)

            # Status Badge
            status = item["status"]
            badge_color = "#48BB78" if status == "COMPLETED" else ("#E53E3E" if status == "FAILED" else "#ED8936")
            
            badge_lbl = ctk.CTkLabel(
                row_frame,
                text=status,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color=badge_color,
                width=100
            )
            badge_lbl.grid(row=0, column=3, padx=15, pady=8)
