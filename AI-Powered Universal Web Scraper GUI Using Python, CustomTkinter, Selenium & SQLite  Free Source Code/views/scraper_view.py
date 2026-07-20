"""
Universal AI Web Scraper - Scraper Workspace View
Provides URL pasting, natural language instructions box with templates,
control execution (start, stop, clear), active stats, and a dynamic results preview grid.
"""

import time
import logging
import threading
import customtkinter as ctk
from typing import List, Dict, Any

from components.console_panel import ConsolePanel
from database import DatabaseManager
from scraping_engine import ScrapingEngine

logger = logging.getLogger(__name__)

class ScraperView(ctk.CTkFrame):
    """
    Main work area containing inputs, prompt selectors, state controls,
    progress tracking, and data results table.
    """
    def __init__(self, parent, status_bar_callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.status_bar_callback = status_bar_callback
        
        self._db = DatabaseManager.get_instance()
        self.scraper_engine = ScrapingEngine()
        self.extracted_results: List[Dict[str, Any]] = []
        self.active_explanation: str = ""
        self.start_time = 0.0
        self.timer_running = False

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Inputs Frame
        self.grid_rowconfigure(1, weight=0) # Progress / Actions Frame
        self.grid_rowconfigure(2, weight=1) # Results / Console Frame

        # ----------------------------------------------------
        # 1. Inputs Frame (URL + Prompt Box + Templates)
        # ----------------------------------------------------
        self.inputs_frame = ctk.CTkFrame(self, fg_color="#1A202C", border_width=1, border_color="#2D3748")
        self.inputs_frame.grid(row=0, column=0, padx=30, pady=(20, 10), sticky="ew")
        self.inputs_frame.grid_columnconfigure(1, weight=1)

        # URL Label & Entry
        self.url_lbl = ctk.CTkLabel(
            self.inputs_frame,
            text="WEBSITE TARGET URL",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#A0AEC0"
        )
        self.url_lbl.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.url_entry = ctk.CTkEntry(
            self.inputs_frame,
            placeholder_text="https://example.com/products-catalog",
            font=ctk.CTkFont(family="Inter", size=13),
            height=35,
            border_color="#4A5568",
            fg_color="#2D3748"
        )
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=(10, 20), pady=(15, 5), sticky="ew")

        # Prompt Label & Combo Templates
        self.prompt_lbl = ctk.CTkLabel(
            self.inputs_frame,
            text="EXTRACTION PROMPT INSTRUCTION",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#A0AEC0"
        )
        self.prompt_lbl.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")

        # Preset prompts drop-down template
        self.templates = [
            "--- Choose a Template Instruction ---",
            "Extract product names and prices",
            "Extract article titles and publish dates",
            "Extract all visible headings",
            "Extract table data",
            "Extract image URLs",
            "Extract links",
            "Extract contact information that is publicly displayed",
            "Extract FAQ sections",
            "Extract blog titles",
            "Extract category names"
        ]
        
        self.template_combobox = ctk.CTkComboBox(
            self.inputs_frame,
            values=self.templates,
            font=ctk.CTkFont(family="Inter", size=12),
            height=30,
            border_color="#4A5568",
            fg_color="#2D3748",
            command=self._on_template_selected
        )
        self.template_combobox.grid(row=1, column=1, padx=(10, 20), pady=(10, 5), sticky="ew")

        # Custom Prompt Input Box
        self.prompt_textbox = ctk.CTkTextbox(
            self.inputs_frame,
            height=60,
            font=ctk.CTkFont(family="Inter", size=13),
            border_width=1,
            border_color="#4A5568",
            fg_color="#2D3748"
        )
        self.prompt_textbox.grid(row=2, column=1, columnspan=2, padx=(10, 20), pady=(5, 15), sticky="ew")
        self.prompt_textbox.insert("1.0", "Extract product names and prices") # Default placeholder text

        # ----------------------------------------------------
        # 2. Controls & Progress Frame
        # ----------------------------------------------------
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(3, weight=1)

        # Action Buttons
        self.start_btn = ctk.CTkButton(
            self.controls_frame,
            text="▶ Start Scrape",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#3182CE", # Primary Accent blue
            hover_color="#2B6CB0",
            height=35,
            width=120,
            command=self.start_scraping
        )
        self.start_btn.grid(row=0, column=0, padx=(0, 10), pady=5)

        self.stop_btn = ctk.CTkButton(
            self.controls_frame,
            text="⏹ Stop",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#E53E3E", # Red alert
            hover_color="#C53030",
            height=35,
            width=100,
            state="disabled",
            command=self.stop_scraping
        )
        self.stop_btn.grid(row=0, column=1, padx=10, pady=5)

        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="🧹 Clear",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#4A5568",
            hover_color="#2D3748",
            height=35,
            width=100,
            command=self.clear_inputs
        )
        self.clear_btn.grid(row=0, column=2, padx=10, pady=5)

        # Scraper Metrics Labels
        self.stats_frame = ctk.CTkFrame(self.controls_frame, fg_color="#1A202C", height=35)
        self.stats_frame.grid(row=0, column=3, padx=(20, 0), pady=5, sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.time_lbl = ctk.CTkLabel(
            self.stats_frame,
            text="Timer: 0.0s",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#CBD5E0"
        )
        self.time_lbl.grid(row=0, column=0, pady=5)

        self.status_lbl = ctk.CTkLabel(
            self.stats_frame,
            text="Engine: IDLE",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#48BB78"
        )
        self.status_lbl.grid(row=0, column=1, pady=5)

        self.count_lbl = ctk.CTkLabel(
            self.stats_frame,
            text="Items Found: 0",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#63B3ED"
        )
        self.count_lbl.grid(row=0, column=2, pady=5)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self, height=6, progress_color="#3182CE")
        self.progress_bar.grid(row=1, column=0, padx=30, pady=(45, 0), sticky="ew")
        self.progress_bar.set(0)

        # ----------------------------------------------------
        # 3. Double-Panel (Left: Results Table, Right: Live Logs)
        # ----------------------------------------------------
        self.workspace_panels = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_panels.grid(row=2, column=0, padx=30, pady=(15, 25), sticky="nsew")
        self.workspace_panels.grid_columnconfigure(0, weight=7, uniform="panels") # 70% width
        self.workspace_panels.grid_columnconfigure(1, weight=3, uniform="panels") # 30% width
        self.workspace_panels.grid_rowconfigure(0, weight=1)

        # Left panel: Results Grid frame
        self.results_card = ctk.CTkFrame(self.workspace_panels, fg_color="#1A202C", border_width=1, border_color="#2D3748")
        self.results_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.results_card.grid_columnconfigure(0, weight=1)
        self.results_card.grid_rowconfigure(0, weight=0) # Title header
        self.results_card.grid_rowconfigure(1, weight=1) # Scroll frame for rows

        self.table_header_lbl = ctk.CTkLabel(
            self.results_card,
            text="📊 EXTRACTED DATA RESULTS PREVIEW",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#A0AEC0",
            anchor="w"
        )
        self.table_header_lbl.grid(row=0, column=0, padx=15, pady=10, sticky="ew")

        # Scrollable table container
        self.table_scroll_container = ctk.CTkScrollableFrame(self.results_card, fg_color="#171923")
        self.table_scroll_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Right panel: Console Live Log view
        self.console_panel = ConsolePanel(self.workspace_panels, fg_color="#1A202C", border_width=1, border_color="#2D3748")
        self.console_panel.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

    def _on_template_selected(self, val: str):
        if val != self.templates[0]:
            self.prompt_textbox.delete("1.0", "end")
            self.prompt_textbox.insert("1.0", val)

    def clear_inputs(self):
        """Resets the scraper forms to blank."""
        self.url_entry.delete(0, "end")
        self.prompt_textbox.delete("1.0", "end")
        self.template_combobox.set(self.templates[0])
        self.clear_results_table()
        self.extracted_results = []
        self.count_lbl.configure(text="Items Found: 0")

    def clear_results_table(self):
        for child in self.table_scroll_container.winfo_children():
            child.destroy()
        # Add a default placeholder
        placeholder = ctk.CTkLabel(
            self.table_scroll_container,
            text="No active results. Provide details above and start scraper.",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#4A5568"
        )
        placeholder.pack(pady=50)

    def start_scraping(self):
        """Fetches forms and boots up the scraping execution task."""
        url = self.url_entry.get().strip()
        prompt = self.prompt_textbox.get("1.0", "end-1c").strip()

        if not url:
            logger.error("Scrape failed: Target URL is blank.")
            self.console_panel.append_log("[ERROR] Target URL cannot be empty.")
            return

        if not prompt:
            logger.error("Scrape failed: Instruction is blank.")
            self.console_panel.append_log("[ERROR] Extraction prompt instruction cannot be empty.")
            return

        # Prepare GUI state
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.clear_btn.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.template_combobox.configure(state="disabled")
        
        self.clear_results_table()
        
        # Load local settings for timeout, browser configurations
        settings = self._db.get_all_settings()

        # Update labels
        self.progress_bar.set(0.0)
        self.status_lbl.configure(text="Engine: RUNNING", text_color="#ED8936")
        if self.status_bar_callback:
            self.status_bar_callback("Scraping in background thread...", "RUNNING")

        # Timer setup
        self.start_time = time.time()
        self.timer_running = True
        self._update_timer()

        # Trigger background run
        success = self.scraper_engine.start_scrape(
            url=url,
            prompt=prompt,
            settings=settings,
            on_progress=self._thread_progress,
            on_success=self._thread_success,
            on_failure=self._thread_failure
        )

        if not success:
            self._thread_failure("Scraper already running in the background.")

    def stop_scraping(self):
        """Interrupts and closes active scraper task."""
        self.console_panel.append_log("[WARNING] Scraping thread stop requested by user.")
        self.scraper_engine.stop_active_scrape()
        self.timer_running = False
        self.status_lbl.configure(text="Engine: STOPPED", text_color="#E53E3E")
        self._reset_gui_controls()
        if self.status_bar_callback:
            self.status_bar_callback("Scraper terminated.", "ERROR")

    def _update_timer(self):
        """Drives the tick clock label."""
        if self.timer_running:
            elapsed = time.time() - self.start_time
            self.time_lbl.configure(text=f"Timer: {elapsed:.1f}s")
            self.after(100, self._update_timer)

    def _reset_gui_controls(self):
        """Re-enables standard buttons."""
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.clear_btn.configure(state="normal")
        self.url_entry.configure(state="normal")
        self.template_combobox.configure(state="normal")
        self.progress_bar.set(1.0)

    # --- Worker Thread Threadsafe Callbacks ---

    def _thread_progress(self, progress: float, msg: str):
        """Runs sequentially from background thread updates."""
        self.after(0, lambda: self._on_ui_progress(progress, msg))

    def _on_ui_progress(self, progress: float, msg: str):
        self.progress_bar.set(progress)
        self.console_panel.append_log(f"[INFO] {msg}")

    def _thread_success(self, results: List[Dict[str, Any]], explanation: str):
        self.after(0, lambda: self._on_ui_success(results, explanation))

    def _on_ui_success(self, results: List[Dict[str, Any]], explanation: str):
        self.timer_running = False
        self.progress_bar.set(1.0)
        self._reset_gui_controls()

        self.extracted_results = results
        self.active_explanation = explanation
        self.count_lbl.configure(text=f"Items Found: {len(results)}")
        self.status_lbl.configure(text="Engine: COMPLETED", text_color="#48BB78")

        self.console_panel.append_log(f"[SUCCESS] Scraping completed successfully! Found {len(results)} items.")
        self.console_panel.append_log(f"[AI DECISION] Heuristics logic: {explanation}")
        
        if self.status_bar_callback:
            self.status_bar_callback(f"Scrape successful. Found {len(results)} items.", "SUCCESS")
            
        self._populate_results_table()

    def _thread_failure(self, error_message: str):
        self.after(0, lambda: self._on_ui_failure(error_message))

    def _on_ui_failure(self, error_message: str):
        self.timer_running = False
        self.progress_bar.set(0.0)
        self._reset_gui_controls()
        
        self.status_lbl.configure(text="Engine: FAILED", text_color="#E53E3E")
        self.console_panel.append_log(f"[ERROR] Scrape execution failed: {error_message}")
        
        if self.status_bar_callback:
            self.status_bar_callback(f"Scraping failed: {error_message}", "ERROR")

    # --- Render Results Grid ---

    def _populate_results_table(self):
        """Draws dynamic columns and records inside the results preview frame."""
        for child in self.table_scroll_container.winfo_children():
            child.destroy()

        if not self.extracted_results:
            empty_lbl = ctk.CTkLabel(
                self.table_scroll_container,
                text="The scraping execution succeeded but no tabular elements were returned.",
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#718096"
            )
            empty_lbl.pack(pady=40)
            return

        # Determine dynamic headers from data keys
        headers = list(self.extracted_results[0].keys())

        # Construct Header Grid Frame
        header_frame = ctk.CTkFrame(self.table_scroll_container, fg_color="#2D3748", corner_radius=4)
        header_frame.pack(fill="x", pady=(0, 6))

        # Grid column weights
        col_count = len(headers)
        for i in range(col_count):
            header_frame.grid_columnconfigure(i, weight=1, uniform="col")

        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(
                header_frame,
                text=str(h).upper(),
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color="#F7FAFC",
                padx=10,
                pady=6
            )
            lbl.grid(row=0, column=idx, sticky="w")

        # Construct Alternating Data Rows
        for r_idx, row_dict in enumerate(self.extracted_results):
            row_frame = ctk.CTkFrame(
                self.table_scroll_container,
                fg_color="#1A202C" if r_idx % 2 == 0 else "#171923",
                corner_radius=4
            )
            row_frame.pack(fill="x", pady=2)
            
            for i in range(col_count):
                row_frame.grid_columnconfigure(i, weight=1, uniform="col")

            for c_idx, h in enumerate(headers):
                cell_text = str(row_dict.get(h, ""))
                
                # Truncate text for grid preview
                if len(cell_text) > 80:
                    cell_text = cell_text[:80] + "..."

                cell_lbl = ctk.CTkLabel(
                    row_frame,
                    text=cell_text,
                    font=ctk.CTkFont(family="Inter", size=11),
                    text_color="#E2E8F0",
                    padx=10,
                    pady=4,
                    anchor="w",
                    justify="left"
                )
                cell_lbl.grid(row=0, column=c_idx, sticky="ew")
