"""
Universal AI Web Scraper - Sidebar Component
Implements the navigation sidebar with hover states, selecting different workspace panels.
"""

import customtkinter as ctk
from typing import Callable

class Sidebar(ctk.CTkFrame):
    """
    Left-hand sidebar for navigation within the application.
    Enforces a dark futuristic theme with consistent blue active indicators.
    """
    def __init__(self, parent, select_callback: Callable[[str], None], **kwargs):
        super().__init__(parent, corner_radius=0, **kwargs)
        self.select_callback = select_callback
        
        # Configure grid layout
        self.grid_rowconfigure(9, weight=1) # Spacer row at bottom
        self.grid_columnconfigure(0, weight=1)

        # Application Title Brand
        self.title_label = ctk.CTkLabel(
            self,
            text="AI WEB SCRAPER",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#63B3ED"  # Soft Neon Blue
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="ew")

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="UNIVERSAL ENGINE v1.0",
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            text_color="#A0AEC0"  # Cool grey
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="ew")

        # Sidebar Items config: (Internal Name, Button Text, Symbol)
        self.nav_items = [
            ("Dashboard", "Dashboard", "📊"),
            ("Scraper", "Scraper", "🕷️"),
            ("History", "History", "📜"),
            ("Database", "Database", "💾"),
            ("Settings", "Settings", "⚙️"),
            ("About", "About", "ℹ️")
        ]
        
        self.buttons = {}
        
        # Build Navigation Buttons
        for idx, (name, label, symbol) in enumerate(self.nav_items):
            btn = ctk.CTkButton(
                self,
                text=f"  {symbol}  {label}",
                font=ctk.CTkFont(family="Inter", size=14, weight="normal"),
                anchor="w",
                height=45,
                corner_radius=8,
                fg_color="transparent",
                text_color="#E2E8F0",
                hover_color="#2D3748",
                border_spacing=10,
                command=lambda n=name: self._on_button_clicked(n)
            )
            btn.grid(row=idx + 2, column=0, padx=15, pady=6, sticky="ew")
            self.buttons[name] = btn

        # Set default active tab style
        self.active_tab = None

    def set_active_tab(self, tab_name: str):
        """Updates UI highlight states to reflect the active tab."""
        if self.active_tab and self.active_tab in self.buttons:
            # Revert old button
            self.buttons[self.active_tab].configure(
                fg_color="transparent",
                text_color="#E2E8F0",
                font=ctk.CTkFont(family="Inter", size=14, weight="normal")
            )

        if tab_name in self.buttons:
            # Style active button
            self.buttons[tab_name].configure(
                fg_color="#1A365D", # Deep blue theme base
                text_color="#63B3ED", # Highlight light blue
                font=ctk.CTkFont(family="Inter", size=14, weight="bold")
            )
            self.active_tab = tab_name

    def _on_button_clicked(self, name: str):
        self.set_active_tab(name)
        self.select_callback(name)
