"""
Universal AI Web Scraper - Status Bar Component
Implements the bottom footer status indicator with status details and a colored LED indicator.
"""

import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    """
    Bottom bar showing real-time system state, active driver details,
    and aggregate scrape stats.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=28, corner_radius=0, fg_color="#1A202C", **kwargs)
        
        self.grid_columnconfigure(0, weight=0) # Indicator LED
        self.grid_columnconfigure(1, weight=1) # Message text
        self.grid_columnconfigure(2, weight=0) # Browser info
        self.grid_columnconfigure(3, weight=0) # Total runs info

        # 1. State indicator LED (using Canvas or styled text)
        self.led_indicator = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#48BB78" # Default Green (IDLE)
        )
        self.led_indicator.grid(row=0, column=0, padx=(15, 5), pady=2)

        # 2. Status Label Text
        self.status_label = ctk.CTkLabel(
            self,
            text="Status: Ready",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#A0AEC0"
        )
        self.status_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # 3. Browser details
        self.browser_label = ctk.CTkLabel(
            self,
            text="Browser: Chrome (Headless)",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#718096"
        )
        self.browser_label.grid(row=0, column=2, padx=15, pady=2)

        # 4. Total Stats short display
        self.stats_label = ctk.CTkLabel(
            self,
            text="Runs logged: 0",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#718096"
        )
        self.stats_label.grid(row=0, column=3, padx=(15, 20), pady=2)

    def set_status(self, text: str, state: str = "IDLE"):
        """
        Updates the status message and state LED color.
        States: IDLE, RUNNING, SUCCESS, ERROR
        """
        self.status_label.configure(text=f"Status: {text}")
        
        if state == "IDLE":
            self.led_indicator.configure(text_color="#48BB78") # Green
        elif state == "RUNNING":
            self.led_indicator.configure(text_color="#ED8936") # Orange
        elif state == "SUCCESS":
            self.led_indicator.configure(text_color="#3182CE") # Blue
        elif state == "ERROR":
            self.led_indicator.configure(text_color="#E53E3E") # Red
        else:
            self.led_indicator.configure(text_color="#718096") # Grey

    def update_meta_info(self, browser_name: str, headless: bool, total_runs: int):
        """Updates configurations displayed in the right slots of the status bar."""
        h_str = "Headless" if headless else "GUI mode"
        self.browser_label.configure(text=f"Browser: {browser_name} ({h_str})")
        self.stats_label.configure(text=f"Runs logged: {total_runs}")
