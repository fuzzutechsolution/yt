"""
Universal AI Web Scraper - Console Panel Component
Implements a self-updating terminal log visualizer that polls logger's log_queue.
"""

import customtkinter as ctk
import logging
from logger import log_queue

logger = logging.getLogger(__name__)

class ConsolePanel(ctk.CTkFrame):
    """
    GUI Panel simulating a live log console.
    Polls the thread-safe queue periodically using Tkinter's 'after' loop.
    """
    def __init__(self, parent, max_lines: int = 500, **kwargs):
        super().__init__(parent, **kwargs)
        self.max_lines = max_lines
        
        # Grid layout
        self.grid_rowconfigure(0, weight=0) # Header bar
        self.grid_rowconfigure(1, weight=1) # Log text area
        self.grid_columnconfigure(0, weight=1)

        # 1. Header Bar
        self.header_frame = ctk.CTkFrame(self, height=35, fg_color="#1A202C", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="💻 SYSTEM CONSOLE LOGS",
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#CBD5E0"
        )
        self.title_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        # Clear Console Button
        self.clear_btn = ctk.CTkButton(
            self.header_frame,
            text="Clear",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            width=60,
            height=24,
            fg_color="#2D3748",
            hover_color="#E53E3E",
            command=self.clear_console
        )
        self.clear_btn.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        # 2. Log Text Box
        self.text_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#171923", # Near pitch black terminal
            text_color="#A0AEC0",
            corner_radius=0,
            border_width=0
        )
        self.text_box.grid(row=1, column=0, sticky="nsew")
        self.text_box.configure(state="disabled") # Read-only initially

        # Start periodic log checking loop
        self._check_logs()

    def clear_console(self):
        """Clears all text in the terminal widget."""
        self.text_box.configure(state="normal")
        self.text_box.delete("1.0", "end")
        self.text_box.configure(state="disabled")

    def append_log(self, message: str):
        """Appends a new line of text, automatically scrolling to the bottom."""
        self.text_box.configure(state="normal")
        
        # Color code levels for beautiful aesthetics
        if "[ERROR]" in message:
            # ReportLab or Selenium crash logs
            tag = "error"
        elif "[WARNING]" in message:
            tag = "warning"
        elif "[SUCCESS]" in message or "completed" in message.lower():
            tag = "success"
        else:
            tag = "normal"

        self.text_box.insert("end", f"{message}\n")
        
        # Enforce line limits to save RAM
        total_lines = int(self.text_box.index("end-1c").split(".")[0])
        if total_lines > self.max_lines:
            self.text_box.delete("1.0", f"{total_lines - self.max_lines}.0")

        self.text_box.configure(state="disabled")
        self.text_box.see("end")

    def _check_logs(self):
        """Checks the queue and drains it, scheduling another check in 150ms."""
        drain_limit = 30
        count = 0
        while not log_queue.empty() and count < drain_limit:
            try:
                msg = log_queue.get_nowait()
                self.append_log(msg)
                count += 1
            except Exception:
                break
        
        # Re-schedule self
        self.after(150, self._check_logs)
