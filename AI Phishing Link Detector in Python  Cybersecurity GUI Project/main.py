import customtkinter as ctk
import re
import ipaddress
import threading
import time
from urllib.parse import urlparse


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PhishingLinkDetector(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 9:16 PORTRAIT WINDOW
        self.title("AI Phishing Link Detector | FuzzuTech")
        self.geometry("540x960")
        self.resizable(False, False)
        self.configure(fg_color="#030711")

        self.create_header()
        self.create_scanner()
        self.create_result_panel()
        self.create_footer()


    # =========================================================
    # HEADER
    # =========================================================

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            width=540,
            height=125,
            corner_radius=0,
            fg_color="#07101D"
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="🛡",
            font=ctk.CTkFont(size=32)
        ).pack(pady=(15, 0))

        ctk.CTkLabel(
            header,
            text="AI PHISHING LINK DETECTOR",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color="#00E5FF"
        ).pack(pady=(0, 3))

        ctk.CTkLabel(
            header,
            text="INTELLIGENT URL THREAT ANALYSIS SYSTEM",
            font=ctk.CTkFont(size=10),
            text_color="#64748B"
        ).pack()


    # =========================================================
    # SCANNER PANEL
    # =========================================================

    def create_scanner(self):

        self.scanner_panel = ctk.CTkFrame(
            self,
            width=490,
            height=300,
            corner_radius=18,
            fg_color="#0A1220",
            border_width=1,
            border_color="#1B304D"
        )

        self.scanner_panel.pack(
            padx=25,
            pady=(20, 10),
            fill="x"
        )

        self.scanner_panel.pack_propagate(False)

        ctk.CTkLabel(
            self.scanner_panel,
            text="URL SECURITY SCANNER",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=(22, 4))

        ctk.CTkLabel(
            self.scanner_panel,
            text="Enter a suspicious URL to analyze phishing threats",
            font=ctk.CTkFont(size=11),
            text_color="#8193AD"
        ).pack(pady=(0, 15))

        self.url_entry = ctk.CTkEntry(
            self.scanner_panel,
            width=440,
            height=48,
            corner_radius=9,
            placeholder_text="https://example.com/login",
            font=ctk.CTkFont(size=13),
            fg_color="#050B14",
            border_width=2,
            border_color="#1C3657"
        )

        self.url_entry.pack(pady=(5, 12))

        self.scan_button = ctk.CTkButton(
            self.scanner_panel,
            text="SCAN LINK",
            width=440,
            height=48,
            corner_radius=9,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#0878FF",
            hover_color="#0064DA",
            command=self.start_scan
        )

        self.scan_button.pack()

        self.progress = ctk.CTkProgressBar(
            self.scanner_panel,
            width=440,
            height=7,
            progress_color="#00E5FF"
        )

        self.progress.pack(pady=(20, 8))
        self.progress.set(0)

        self.scan_status = ctk.CTkLabel(
            self.scanner_panel,
            text="●  SYSTEM READY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#607899"
        )

        self.scan_status.pack()


    # =========================================================
    # RESULT PANEL
    # =========================================================

    def create_result_panel(self):

        self.result_panel = ctk.CTkFrame(
            self,
            width=490,
            height=420,
            corner_radius=18,
            fg_color="#0A1220",
            border_width=1,
            border_color="#1B304D"
        )

        self.result_panel.pack(
            padx=25,
            pady=10,
            fill="x"
        )

        self.result_panel.pack_propagate(False)

        ctk.CTkLabel(
            self.result_panel,
            text="THREAT ANALYSIS",
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="white"
        ).pack(pady=(22, 10))

        self.result_label = ctk.CTkLabel(
            self.result_panel,
            text="NO SCAN DATA",
            font=ctk.CTkFont(size=27, weight="bold"),
            text_color="#53647E"
        )

        self.result_label.pack(pady=8)

        self.score_label = ctk.CTkLabel(
            self.result_panel,
            text="RISK SCORE\n-- / 100",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color="#00E5FF"
        )

        self.score_label.pack(pady=10)

        self.domain_label = ctk.CTkLabel(
            self.result_panel,
            text="DOMAIN\nWaiting for analysis...",
            font=ctk.CTkFont(size=12),
            text_color="#8CA0BE"
        )

        self.domain_label.pack(pady=10)

        self.threat_label = ctk.CTkLabel(
            self.result_panel,
            text="DETECTED THREATS\n\nNone",
            width=440,
            height=100,
            font=ctk.CTkFont(size=12),
            text_color="#8CA0BE",
            justify="center",
            wraplength=420
        )

        self.threat_label.pack(pady=5)


    # =========================================================
    # FOOTER
    # =========================================================

    def create_footer(self):

        ctk.CTkLabel(
            self,
            text="SECURITY ENGINE ONLINE  •  FUZZUTECH CYBER LAB",
            font=ctk.CTkFont(size=9),
            text_color="#405574"
        ).pack(pady=(5, 0))


    # =========================================================
    # START SCAN
    # =========================================================

    def start_scan(self):

        url = self.url_entry.get().strip()

        if not url:
            self.result_label.configure(
                text="ENTER A URL",
                text_color="#FFB020"
            )
            return

        self.scan_button.configure(
            state="disabled",
            text="SCANNING..."
        )

        self.progress.set(0)

        self.result_label.configure(
            text="ANALYZING...",
            text_color="#00E5FF"
        )

        self.score_label.configure(
            text="RISK SCORE\nCALCULATING..."
        )

        self.domain_label.configure(
            text="DOMAIN\nAnalyzing hostname..."
        )

        self.threat_label.configure(
            text="DETECTED THREATS\n\nScanning URL patterns..."
        )

        threading.Thread(
            target=self.scan_animation,
            args=(url,),
            daemon=True
        ).start()


    # =========================================================
    # SCANNING ANIMATION
    # =========================================================

    def scan_animation(self, url):

        messages = [
            "CHECKING URL STRUCTURE...",
            "ANALYZING DOMAIN...",
            "SCANNING SUSPICIOUS KEYWORDS...",
            "CALCULATING THREAT SCORE...",
            "FINALIZING SECURITY REPORT..."
        ]

        for i in range(101):

            time.sleep(0.015)

            value = i / 100

            self.after(
                0,
                lambda v=value: self.progress.set(v)
            )

            message_index = min(i // 21, 4)

            self.after(
                0,
                lambda m=messages[message_index]:
                self.scan_status.configure(
                    text="●  " + m,
                    text_color="#00E5FF"
                )
            )

        result = self.analyze_url(url)

        self.after(
            0,
            lambda: self.show_result(result)
        )


    # =========================================================
    # URL ANALYSIS
    # =========================================================

    def analyze_url(self, url):

        original_url = url

        if not re.match(
            r"^[a-zA-Z][a-zA-Z0-9+.-]*://",
            url
        ):
            url = "http://" + url

        parsed = urlparse(url)

        hostname = (
            parsed.hostname.lower()
            if parsed.hostname
            else "Unknown"
        )

        score = 0
        threats = []


        # HTTP CHECK

        if parsed.scheme != "https":
            score += 15
            threats.append("No HTTPS Encryption")


        # LONG URL

        if len(original_url) > 75:
            score += 15
            threats.append("Excessive URL Length")


        # IP ADDRESS

        try:
            ipaddress.ip_address(hostname)

            score += 30
            threats.append("IP Address Used as Domain")

        except ValueError:
            pass


        # SUSPICIOUS KEYWORDS

        suspicious_keywords = [
            "verify",
            "account",
            "update",
            "secure",
            "login",
            "signin",
            "bank",
            "wallet",
            "password",
            "confirm",
            "bonus",
            "free",
            "gift",
            "urgent"
        ]

        hits = [
            word
            for word in suspicious_keywords
            if word in original_url.lower()
        ]

        if hits:

            score += min(len(hits) * 7, 25)

            threats.append(
                "Suspicious Keywords: "
                + ", ".join(hits[:3])
            )


        # @ SYMBOL

        if "@" in original_url:

            score += 20
            threats.append("URL Contains @ Symbol")


        # EXCESSIVE SUBDOMAINS

        if hostname != "Unknown" and hostname.count(".") >= 4:

            score += 15
            threats.append("Excessive Subdomains")


        # PUNYCODE

        if "xn--" in hostname:

            score += 25
            threats.append("Punycode Domain Detected")


        # MULTIPLE HYPHENS

        if hostname.count("-") >= 3:

            score += 10
            threats.append("Multiple Domain Hyphens")


        # ENCODED CHARACTERS

        if re.search(r"%[0-9A-Fa-f]{2}", original_url):

            score += 10
            threats.append("Encoded Characters Detected")


        score = min(score, 100)


        if score >= 60:

            status = "PHISHING DETECTED"
            color = "#FF3158"

        elif score >= 30:

            status = "SUSPICIOUS LINK"
            color = "#FFB020"

        else:

            status = "SAFE LINK"
            color = "#00E676"


        return {
            "status": status,
            "score": score,
            "domain": hostname,
            "threats": threats,
            "color": color
        }


    # =========================================================
    # SHOW RESULT
    # =========================================================

    def show_result(self, result):

        color = result["color"]

        self.result_label.configure(
            text=result["status"],
            text_color=color
        )

        self.score_label.configure(
            text=f'RISK SCORE\n{result["score"]} / 100',
            text_color=color
        )

        self.domain_label.configure(
            text=f'DOMAIN\n{result["domain"]}'
        )

        if result["threats"]:

            threats = "\n".join(
                "⚠  " + threat
                for threat in result["threats"][:4]
            )

        else:

            threats = "✓  No suspicious patterns detected"

        self.threat_label.configure(
            text="DETECTED THREATS\n\n" + threats,
            text_color=color
        )

        self.scan_status.configure(
            text="●  SCAN COMPLETED",
            text_color=color
        )

        self.scan_button.configure(
            state="normal",
            text="SCAN ANOTHER LINK"
        )


if __name__ == "__main__":
    app = PhishingLinkDetector()
    app.mainloop()