"""
Universal AI Web Scraper - History View
Displays previously executed scrapes. Allows users to view results, export data, and delete entries.
"""

import os
import logging
import customtkinter as ctk
from database import DatabaseManager
from exporter import DataExporter

logger = logging.getLogger(__name__)

class HistoryView(ctk.CTkFrame):
    """
    Historical log viewer that lists all past scrape records.
    Provides options to re-export data from database cache.
    """
    def __init__(self, parent, status_bar_callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.status_bar_callback = status_bar_callback
        self._db = DatabaseManager.get_instance()
        self.selected_item = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header Frame
        self.grid_rowconfigure(1, weight=0) # Filter Frame
        self.grid_rowconfigure(2, weight=1) # History List Container

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="EXECUTION HISTORY LOGS",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#F7FAFC"
        )
        self.title_lbl.grid(row=0, column=0, sticky="w")

        # 2. Filter / Options Frame
        self.filter_frame = ctk.CTkFrame(self, fg_color="#1A202C", border_width=1, border_color="#2D3748")
        self.filter_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.filter_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            self.filter_frame,
            placeholder_text="🔍 Filter history by URL or Prompt key terms...",
            font=ctk.CTkFont(family="Inter", size=13),
            height=35,
            border_color="#4A5568",
            fg_color="#2D3748"
        )
        self.search_entry.grid(row=0, column=0, padx=(20, 10), pady=12, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_history())

        self.refresh_btn = ctk.CTkButton(
            self.filter_frame,
            text="🔄 Refresh",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#2D3748",
            hover_color="#4A5568",
            width=100,
            height=35,
            command=self.load_history
        )
        self.refresh_btn.grid(row=0, column=1, padx=(10, 20), pady=12)

        # 3. History Rows Scroll Frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1A202C",
            border_width=1,
            border_color="#2D3748"
        )
        self.scroll_frame.grid(row=2, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # Cache variables
        self.history_records = []
        self.selected_row_frame = None

        # Load history
        self.load_history()

    def load_history(self):
        """Fetches items and parses query filters."""
        # Reset selection
        self.selected_item = None
        self.selected_row_frame = None
        
        # Clear child elements
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        search_query = self.search_entry.get().strip().lower()
        records = self._db.get_history(limit=150)
        
        # Filter if search query exists
        if search_query:
            records = [
                r for r in records 
                if search_query in r["url"].lower() or search_query in r["prompt"].lower()
            ]

        self.history_records = records

        if not records:
            empty_lbl = ctk.CTkLabel(
                self.scroll_frame,
                text="No records found matching criteria.",
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#718096"
            )
            empty_lbl.pack(pady=50)
            return

        # Build list columns headers
        headers_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#2D3748", height=30, corner_radius=4)
        headers_frame.pack(fill="x", padx=10, pady=(10, 4))
        headers_frame.grid_columnconfigure(0, weight=4) # URL/Prompt
        headers_frame.grid_columnconfigure(1, weight=2) # Date
        headers_frame.grid_columnconfigure(2, weight=1) # Count
        headers_frame.grid_columnconfigure(3, weight=1) # Status
        headers_frame.grid_columnconfigure(4, weight=2) # Actions

        lbl_font = ctk.CTkFont(family="Inter", size=11, weight="bold")
        ctk.CTkLabel(headers_frame, text="TARGET SITE / PROMPT", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=0, padx=15, pady=6, sticky="w")
        ctk.CTkLabel(headers_frame, text="TIMESTAMP", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=1, padx=10, pady=6)
        ctk.CTkLabel(headers_frame, text="ITEMS", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=2, padx=10, pady=6)
        ctk.CTkLabel(headers_frame, text="STATUS", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=3, padx=10, pady=6)
        ctk.CTkLabel(headers_frame, text="CONTROLS", font=lbl_font, text_color="#E2E8F0").grid(row=0, column=4, padx=10, pady=6)

        # Add data entries
        for idx, item in enumerate(records):
            row_frame = ctk.CTkFrame(
                self.scroll_frame,
                fg_color="#1D2330" if idx % 2 == 0 else "#141721",
                corner_radius=4
            )
            row_frame.pack(fill="x", padx=10, pady=3)
            row_frame.grid_columnconfigure(0, weight=4)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=1)
            row_frame.grid_columnconfigure(3, weight=1)
            row_frame.grid_columnconfigure(4, weight=2)

            # Details
            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, padx=15, pady=8, sticky="w")
            
            url_lbl = ctk.CTkLabel(
                info_frame,
                text=item["url"][:60] + ("..." if len(item["url"]) > 60 else ""),
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#F7FAFC",
                anchor="w",
                justify="left"
            )
            url_lbl.pack(anchor="w")

            prompt_lbl = ctk.CTkLabel(
                info_frame,
                text=f"Prompt: {item['prompt']}",
                font=ctk.CTkFont(family="Inter", size=10),
                text_color="#A0AEC0",
                anchor="w",
                justify="left"
            )
            prompt_lbl.pack(anchor="w")

            # Timestamp
            ctk.CTkLabel(
                row_frame,
                text=item["timestamp"],
                font=ctk.CTkFont(family="Inter", size=11),
                text_color="#A0AEC0"
            ).grid(row=0, column=1, padx=10, pady=8)

            # Results count
            ctk.CTkLabel(
                row_frame,
                text=f"{item['results_count']}",
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#63B3ED"
            ).grid(row=0, column=2, padx=10, pady=8)

            # Status Badge
            status = item["status"]
            badge_color = "#48BB78" if status == "COMPLETED" else ("#E53E3E" if status == "FAILED" else "#ED8936")
            ctk.CTkLabel(
                row_frame,
                text=status,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color=badge_color
            ).grid(row=0, column=3, padx=10, pady=8)

            # Buttons Column (Export & Delete)
            btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=4, padx=10, pady=8)

            # Quick Export PDF/XLSX
            export_btn = ctk.CTkButton(
                btn_frame,
                text="📥 Export",
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                width=65,
                height=26,
                fg_color="#3182CE",
                hover_color="#2B6CB0",
                command=lambda val=item: self._export_history_entry(val)
            )
            export_btn.pack(side="left", padx=3)
            
            # If status failed, disable export
            if status == "FAILED" or item["results_count"] == 0:
                export_btn.configure(state="disabled", fg_color="#4A5568")

            # Delete button
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="❌",
                font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                width=30,
                height=26,
                fg_color="#4A5568",
                hover_color="#E53E3E",
                command=lambda val=item["id"]: self._delete_history_entry(val)
            )
            delete_btn.pack(side="left", padx=3)

    def _delete_history_entry(self, entry_id: int):
        """Clears record from DB."""
        self._db.delete_history_entry(entry_id)
        if self.status_bar_callback:
            self.status_bar_callback("History record removed.", "IDLE")
        self.load_history()

    def _export_history_entry(self, item: Dict[str, Any]):
        """Runs the Exporter flow for the selected database record."""
        results = self._db.get_results_for_history(item["id"])
        if not results:
            if self.status_bar_callback:
                self.status_bar_callback("Export failed: Cache results empty.", "ERROR")
            return

        # Show dialogue or use the configured settings output folder
        output_folder = self._db.get_setting("output_folder", os.getcwd())
        
        # We can ask the exporter to output a default package, e.g. Excel + PDF
        timestamp_clean = item["timestamp"].replace(":", "-").replace(" ", "_")
        filename_base = f"scrape_history_{item['id']}_{timestamp_clean}"

        meta_info = {
            "url": item["url"],
            "prompt": item["prompt"],
            "timestamp": item["timestamp"]
        }

        # By default export to XLSX and PDF in parallel to satisfy formats!
        try:
            xlsx_path = DataExporter.export_data(
                data=results,
                format_type="xlsx",
                base_filename=filename_base,
                output_dir=output_folder,
                meta_info=meta_info
            )
            pdf_path = DataExporter.export_data(
                data=results,
                format_type="pdf",
                base_filename=filename_base,
                output_dir=output_folder,
                meta_info=meta_info
            )
            
            # Show success message
            success_msg = f"Exported XLSX & PDF to: {output_folder}"
            logger.info(success_msg)
            if self.status_bar_callback:
                self.status_bar_callback(f"Export successful! Files generated in settings output folder.", "SUCCESS")
            
            # Open output folder path in windows file explorer
            import subprocess
            try:
                os.startfile(output_folder)
            except Exception:
                pass
        except Exception as e:
            err = f"Failed to export historical run: {e}"
            logger.error(err)
            if self.status_bar_callback:
                self.status_bar_callback(err, "ERROR")
