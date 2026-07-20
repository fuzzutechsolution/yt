"""
Universal AI Web Scraper - Settings Workspace View
Configures system parameters: Theme, WebDriver Browsers, Headless options, timeouts, retries, and save directory.
"""

import os
import logging
import customtkinter as ctk
from tkinter import filedialog
from database import DatabaseManager

logger = logging.getLogger(__name__)

class SettingsView(ctk.CTkFrame):
    """
    Control panel for custom settings parameters.
    Saves and reads keys directly from SQLite.
    """
    def __init__(self, parent, status_bar_callback=None, theme_change_callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.status_bar_callback = status_bar_callback
        self.theme_change_callback = theme_change_callback
        self._db = DatabaseManager.get_instance()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=1) # Form frame

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="ew")

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="SYSTEM CONFIGURATION",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#F7FAFC"
        )
        self.title_lbl.pack(side="left")

        # 2. Settings Panel Cards Form
        self.form_card = ctk.CTkFrame(self, fg_color="#1A202C", border_width=1, border_color="#2D3748")
        self.form_card.grid(row=1, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.form_card.grid_columnconfigure(0, weight=0) # Labels
        self.form_card.grid_columnconfigure(1, weight=1) # Controls

        # Option: Interface Theme
        self.lbl_theme = ctk.CTkLabel(self.form_card, text="GUI Theme Appearance", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#A0AEC0")
        self.lbl_theme.grid(row=0, column=0, padx=30, pady=18, sticky="w")
        
        self.theme_menu = ctk.CTkOptionMenu(self.form_card, values=["Dark", "Light", "System"], width=180, fg_color="#4A5568", button_color="#2D3748")
        self.theme_menu.grid(row=0, column=1, padx=30, pady=18, sticky="w")

        # Option: Web Browser selection
        self.lbl_browser = ctk.CTkLabel(self.form_card, text="Automated Browser Driver", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#A0AEC0")
        self.lbl_browser.grid(row=1, column=0, padx=30, pady=18, sticky="w")
        
        self.browser_menu = ctk.CTkOptionMenu(self.form_card, values=["Chrome", "Firefox", "Edge"], width=180, fg_color="#4A5568", button_color="#2D3748")
        self.browser_menu.grid(row=1, column=1, padx=30, pady=18, sticky="w")

        # Option: Headless Mode Switch
        self.lbl_headless = ctk.CTkLabel(self.form_card, text="Background Execution (Headless)", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#A0AEC0")
        self.lbl_headless.grid(row=2, column=0, padx=30, pady=18, sticky="w")
        
        self.headless_switch = ctk.CTkSwitch(self.form_card, text="Enabled", font=ctk.CTkFont(family="Inter", size=12), progress_color="#3182CE")
        self.headless_switch.grid(row=2, column=1, padx=30, pady=18, sticky="w")

        # Option: Timeout slider
        self.lbl_timeout = ctk.CTkLabel(self.form_card, text="Connection Timeout (seconds)", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#A0AEC0")
        self.lbl_timeout.grid(row=3, column=0, padx=30, pady=18, sticky="w")
        
        self.timeout_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.timeout_frame.grid(row=3, column=1, padx=30, pady=18, sticky="w")
        
        self.timeout_slider = ctk.CTkSlider(self.timeout_frame, from_=5, to=120, number_of_steps=115, width=220, command=self._on_timeout_slider, progress_color="#3182CE")
        self.timeout_slider.pack(side="left")
        
        self.timeout_val_lbl = ctk.CTkLabel(self.timeout_frame, text="30s", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#63B3ED", width=40)
        self.timeout_val_lbl.pack(side="left", padx=10)

        # Option: Retry limit count
        self.lbl_retry = ctk.CTkLabel(self.form_card, text="Max Connection Retries", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#A0AEC0")
        self.lbl_retry.grid(row=4, column=0, padx=30, pady=18, sticky="w")

        self.retry_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.retry_frame.grid(row=4, column=1, padx=30, pady=18, sticky="w")

        self.retry_slider = ctk.CTkSlider(self.retry_frame, from_=0, to=5, number_of_steps=5, width=220, command=self._on_retry_slider, progress_color="#3182CE")
        self.retry_slider.pack(side="left")

        self.retry_val_lbl = ctk.CTkLabel(self.retry_frame, text="3", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#63B3ED", width=40)
        self.retry_val_lbl.pack(side="left", padx=10)

        # Option: Save Directory Location
        self.lbl_folder = ctk.CTkLabel(self.form_card, text="File Export Target Directory", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#A0AEC0")
        self.lbl_folder.grid(row=5, column=0, padx=30, pady=18, sticky="w")
        
        self.folder_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.folder_frame.grid(row=5, column=1, padx=30, pady=18, sticky="ew")
        
        self.folder_entry = ctk.CTkEntry(self.folder_frame, font=ctk.CTkFont(family="Inter", size=12), width=350, border_color="#4A5568", fg_color="#2D3748")
        self.folder_entry.pack(side="left", fill="x", expand=True)

        self.folder_btn = ctk.CTkButton(self.folder_frame, text="Browse...", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), width=80, fg_color="#4A5568", hover_color="#2D3748", command=self.select_output_folder)
        self.folder_btn.pack(side="left", padx=10)

        # Save Button Row
        self.save_btn = ctk.CTkButton(
            self.form_card,
            text="💾 Save Configurations",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            fg_color="#3182CE",
            hover_color="#2B6CB0",
            height=40,
            width=200,
            command=self.save_configurations
        )
        self.save_btn.grid(row=6, column=0, columnspan=2, padx=30, pady=(30, 20), sticky="w")

        # Load configurations from SQLite
        self.read_configurations()

    def _on_timeout_slider(self, val):
        self.timeout_val_lbl.configure(text=f"{int(val)}s")

    def _on_retry_slider(self, val):
        self.retry_val_lbl.configure(text=f"{int(val)}")

    def select_output_folder(self):
        """Displays dialog selector for export output directories."""
        current = self.folder_entry.get().strip() or os.getcwd()
        selected = filedialog.askdirectory(initialdir=current, title="Select Output Save Folder")
        if selected:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, os.path.abspath(selected))

    def read_configurations(self):
        """Pulls settings values from DB and configures interface state."""
        settings = self._db.get_all_settings()
        
        # Theme
        theme = settings.get("theme", "Dark")
        self.theme_menu.set(theme)

        # Browser
        browser = settings.get("browser", "Chrome")
        self.browser_menu.set(browser)

        # Headless mode
        headless = settings.get("headless", "True").lower() == "true"
        if headless:
            self.headless_switch.select()
        else:
            self.headless_switch.deselect()

        # Timeout
        timeout = float(settings.get("timeout", "30"))
        self.timeout_slider.set(timeout)
        self.timeout_val_lbl.configure(text=f"{int(timeout)}s")

        # Retries
        retries = float(settings.get("retry_count", "3"))
        self.retry_slider.set(retries)
        self.retry_val_lbl.configure(text=f"{int(retries)}")

        # Folder
        folder = settings.get("output_folder", os.getcwd())
        self.folder_entry.delete(0, "end")
        self.folder_entry.insert(0, folder)

    def save_configurations(self):
        """Persists input options into SQLite and triggers callback for instant visual changes."""
        theme = self.theme_menu.get()
        browser = self.browser_menu.get()
        headless = "True" if self.headless_switch.get() else "False"
        timeout = str(int(self.timeout_slider.get()))
        retries = str(int(self.retry_slider.get()))
        folder = self.folder_entry.get().strip() or os.path.abspath(os.getcwd())

        # Save to DB
        self._db.set_setting("theme", theme)
        self._db.set_setting("browser", browser)
        self._db.set_setting("headless", headless)
        self._db.set_setting("timeout", timeout)
        self._db.set_setting("retry_count", retries)
        self._db.set_setting("output_folder", folder)

        logger.info("Saved settings configurations successfully.")
        
        # Display feedback in status bar
        if self.status_bar_callback:
            self.status_bar_callback("Settings updated successfully.", "SUCCESS")

        # Trigger live theme changes if callback exists
        if self.theme_change_callback:
            self.theme_change_callback(theme)
