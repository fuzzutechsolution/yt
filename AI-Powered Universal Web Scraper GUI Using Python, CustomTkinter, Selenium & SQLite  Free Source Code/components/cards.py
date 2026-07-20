"""
Universal AI Web Scraper - Dashboard Cards Component
Provides styled stats cards with borders, soft background shades, and large text.
"""

import customtkinter as ctk

class StatCard(ctk.CTkFrame):
    """
    Styled UI container that represents a single analytic statistic block.
    Uses glassmorphism-inspired dark borders and bright neon blue details.
    """
    def __init__(self, parent, title: str, value: str, subtext: str = "", accent_color: str = "#63B3ED", **kwargs):
        super().__init__(parent, corner_radius=12, fg_color="#1A202C", border_width=1, border_color="#2D3748", **kwargs)
        
        # Grid settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=1) # Value
        self.grid_rowconfigure(2, weight=0) # Subtext

        # Stat Title
        self.title_lbl = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#A0AEC0",
            anchor="w"
        )
        self.title_lbl.grid(row=0, column=0, padx=18, pady=(15, 5), sticky="ew")

        # Large Numeric Value
        self.value_lbl = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
            text_color=accent_color,
            anchor="w"
        )
        self.value_lbl.grid(row=1, column=0, padx=18, pady=(0, 5), sticky="ew")

        # Subtitle context text
        self.subtext_lbl = ctk.CTkLabel(
            self,
            text=subtext,
            font=ctk.CTkFont(family="Inter", size=10, weight="normal"),
            text_color="#718096",
            anchor="w"
        )
        self.subtext_lbl.grid(row=2, column=0, padx=18, pady=(0, 15), sticky="ew")

    def update_value(self, new_value: str, new_subtext: str = "") -> None:
        """Dynamically updates statistics inside the card."""
        self.value_lbl.configure(text=new_value)
        if new_subtext:
            self.subtext_lbl.configure(text=new_subtext)
