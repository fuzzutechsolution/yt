"""
Universal AI Web Scraper - About View
Displays app metadata, license agreements, and an ethical scraping compliance notice.
"""

import customtkinter as ctk

class AboutView(ctk.CTkFrame):
    """
    Informational layout outlining the terms, license parameters, and ethical guidelines.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=1) # Panel Card

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="ew")

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="ABOUT APPLICATION",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#F7FAFC"
        )
        self.title_lbl.pack(side="left")

        # 2. Main Content Card
        self.card_frame = ctk.CTkFrame(self, fg_color="#1A202C", border_width=1, border_color="#2D3748")
        self.card_frame.grid(row=1, column=0, padx=30, pady=(10, 30), sticky="nsew")
        self.card_frame.grid_columnconfigure(0, weight=1)

        # App Identity
        self.app_title = ctk.CTkLabel(
            self.card_frame,
            text="UNIVERSAL AI WEB SCRAPER",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#63B3ED",
            anchor="w"
        )
        self.app_title.pack(anchor="w", padx=30, pady=(30, 2))

        self.app_ver = ctk.CTkLabel(
            self.card_frame,
            text="Version 1.0.0 (Production Quality Release)",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#718096",
            anchor="w"
        )
        self.app_ver.pack(anchor="w", padx=30, pady=(0, 20))

        # Ethical Scraping Charter
        self.lbl_charter_title = ctk.CTkLabel(
            self.card_frame,
            text="🛡️ ETHICAL SCRAPING COMPLIANCE & LEGAL NOTICE",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#F56565", # Warning red/coral
            anchor="w"
        )
        self.lbl_charter_title.pack(anchor="w", padx=30, pady=(10, 5))

        charter_text = (
            "This application is designed solely for extracting publicly available information from websites "
            "where you have explicit permission or legal authority to crawl and scrape data. "
            "It operates in full compliance with standard ethical scraping directives:\n\n"
            "• ROBOTS.TXT COMPLIANCE: The background scraping core checks domain robots.txt directives and "
            "notifies users if the route is blocked by the host administrator.\n"
            "• RATE LIMITING & THROTTLING: Web requests are paced logically to respect server constraints and "
            "avoid overloading target services (Denial of Service).\n"
            "• ACCESS CONTROL RESPECT: This application does NOT bypass firewalls, CAPTCHAs, authentication "
            "systems, or any encrypted/private endpoint layers."
        )

        self.lbl_charter_desc = ctk.CTkLabel(
            self.card_frame,
            text=charter_text,
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#E2E8F0",
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.lbl_charter_desc.pack(anchor="w", padx=30, pady=(0, 25))

        # System Tech Stack details
        self.lbl_tech_title = ctk.CTkLabel(
            self.card_frame,
            text="⚙️ ARCHITECTURE & TECH STACK INTEGRATION",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#63B3ED",
            anchor="w"
        )
        self.lbl_tech_title.pack(anchor="w", padx=30, pady=(10, 5))

        tech_text = (
            "Built with Python and structured under OOP architecture. Includes:\n"
            "• GUI Engine: CustomTkinter framework for a high-performance modern visual theme.\n"
            "• Core Scraper: Integration of Selenium WebDrivers (for JS rendering) and BeautifulSoup4 (for HTML DOM parsing).\n"
            "• DB Persistence: SQLite local client executing thread-safe write serialization.\n"
            "• Exporter Modules: ReportLab (PDF), Pandas, and OpenPyXL (Excel spreadsheets)."
        )

        self.lbl_tech_desc = ctk.CTkLabel(
            self.card_frame,
            text=tech_text,
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#CBD5E0",
            anchor="w",
            justify="left",
            wraplength=700
        )
        self.lbl_tech_desc.pack(anchor="w", padx=30, pady=(0, 30))
