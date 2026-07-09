import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from urllib.parse import urlparse
import re
import ipaddress
from datetime import datetime


# =========================================================
# APP CONFIGURATION
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
# PHISHING DETECTION ENGINE
# =========================================================

class PhishingDetector:

    def __init__(self):

        self.suspicious_keywords = [
            "login",
            "signin",
            "verify",
            "verification",
            "account",
            "secure",
            "security",
            "update",
            "confirm",
            "password",
            "credential",
            "banking",
            "wallet",
            "payment",
            "invoice",
            "recover",
            "unlock",
            "suspended",
            "limited",
            "urgent",
            "bonus",
            "gift",
            "free",
            "winner"
        ]

        self.shorteners = [
            "bit.ly",
            "tinyurl.com",
            "t.co",
            "goo.gl",
            "ow.ly",
            "is.gd",
            "buff.ly",
            "cutt.ly",
            "rb.gy",
            "shorturl.at"
        ]

        self.suspicious_tlds = [
            ".xyz",
            ".top",
            ".click",
            ".link",
            ".work",
            ".gq",
            ".tk",
            ".ml",
            ".cf",
            ".buzz",
            ".rest",
            ".fit"
        ]


    # -----------------------------------------------------
    # URL NORMALIZATION
    # -----------------------------------------------------

    def normalize_url(self, url):

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            url = "http://" + url

        return url


    # -----------------------------------------------------
    # IP ADDRESS DETECTION
    # -----------------------------------------------------

    def contains_ip_address(self, hostname):

        try:

            ipaddress.ip_address(hostname)

            return True

        except ValueError:

            return False


    # -----------------------------------------------------
    # MAIN ANALYSIS
    # -----------------------------------------------------

    def analyze(self, original_url):

        url = self.normalize_url(original_url)

        parsed = urlparse(url)

        hostname = parsed.hostname or ""

        hostname = hostname.lower()

        full_url = url.lower()


        score = 0

        findings = []


        # HTTPS CHECK

        if parsed.scheme != "https":

            score += 15

            findings.append(
                ("WARNING", "Website does not use HTTPS encryption.")
            )

        else:

            findings.append(
                ("SAFE", "HTTPS encryption detected.")
            )


        # IP ADDRESS CHECK

        if self.contains_ip_address(hostname):

            score += 30

            findings.append(
                ("DANGER", "URL uses an IP address instead of a domain name.")
            )


        # URL LENGTH CHECK

        url_length = len(url)

        if url_length > 120:

            score += 20

            findings.append(
                ("DANGER", "Extremely long URL detected.")
            )

        elif url_length > 75:

            score += 10

            findings.append(
                ("WARNING", "URL is unusually long.")
            )

        else:

            findings.append(
                ("SAFE", "URL length appears normal.")
            )


        # @ SYMBOL CHECK

        if "@" in url:

            score += 25

            findings.append(
                ("DANGER", "@ symbol detected. Browser redirection trick may be used.")
            )


        # DOUBLE SLASH REDIRECTION

        path_part = parsed.path

        if "//" in path_part:

            score += 10

            findings.append(
                ("WARNING", "Multiple slash redirection pattern detected.")
            )


        # HYPHEN CHECK

        hyphen_count = hostname.count("-")

        if hyphen_count >= 3:

            score += 15

            findings.append(
                ("WARNING", "Domain contains excessive hyphens.")
            )


        # SUBDOMAIN CHECK

        domain_parts = hostname.split(".")

        if len(domain_parts) > 4:

            score += 15

            findings.append(
                ("WARNING", "Excessive number of subdomains detected.")
            )


        # SUSPICIOUS KEYWORDS

        found_keywords = []

        for keyword in self.suspicious_keywords:

            if keyword in full_url:

                found_keywords.append(keyword)


        if found_keywords:

            keyword_score = min(len(found_keywords) * 4, 20)

            score += keyword_score

            findings.append(
                (
                    "WARNING",
                    "Suspicious keywords detected: "
                    + ", ".join(found_keywords[:8])
                )
            )


        # URL SHORTENER CHECK

        if hostname in self.shorteners:

            score += 20

            findings.append(
                ("WARNING", "URL shortening service detected.")
            )


        # PUNYCODE CHECK

        if "xn--" in hostname:

            score += 35

            findings.append(
                ("DANGER", "Punycode domain detected. Possible homograph attack.")
            )


        # SUSPICIOUS TLD CHECK

        for tld in self.suspicious_tlds:

            if hostname.endswith(tld):

                score += 15

                findings.append(
                    ("WARNING", f"Potentially risky domain extension detected: {tld}")
                )

                break


        # MANY DIGITS IN DOMAIN

        digit_count = sum(char.isdigit() for char in hostname)

        if digit_count >= 5:

            score += 10

            findings.append(
                ("WARNING", "Domain contains an unusual number of digits.")
            )


        # ENCODED CHARACTERS

        if "%" in url:

            score += 10

            findings.append(
                ("WARNING", "Encoded characters detected inside URL.")
            )


        # EXCESSIVE QUERY PARAMETERS

        if parsed.query.count("&") >= 5:

            score += 10

            findings.append(
                ("WARNING", "Large number of query parameters detected.")
            )


        # MULTIPLE HTTP STRINGS

        if full_url.count("http") > 1:

            score += 20

            findings.append(
                ("DANGER", "Multiple HTTP references detected inside URL.")
            )


        score = min(score, 100)


        # RISK CLASSIFICATION

        if score <= 20:

            status = "SAFE"

            message = "LOW PHISHING RISK"

        elif score <= 50:

            status = "SUSPICIOUS"

            message = "MEDIUM PHISHING RISK"

        else:

            status = "DANGEROUS"

            message = "HIGH PHISHING RISK"


        return {

            "url": url,

            "domain": hostname,

            "score": score,

            "status": status,

            "message": message,

            "findings": findings,

            "scan_time": datetime.now().strftime(
                "%d-%m-%Y %I:%M:%S %p"
            )

        }


# =========================================================
# MAIN APPLICATION
# =========================================================

class PhishingDetectorApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(
            "AI Phishing Detector Pro | FuzzuTech"
        )

        self.geometry("1250x760")

        self.minsize(1050, 680)


        self.detector = PhishingDetector()

        self.current_result = None

        self.scan_history = []


        self.create_layout()


    # =====================================================
    # CREATE LAYOUT
    # =====================================================

    def create_layout(self):

        # MAIN GRID

        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)


        # =================================================
        # SIDEBAR
        # =================================================

        self.sidebar = ctk.CTkFrame(

            self,

            width=230,

            corner_radius=0

        )

        self.sidebar.grid(

            row=0,

            column=0,

            sticky="nsew"

        )


        logo = ctk.CTkLabel(

            self.sidebar,

            text="FUZZUTECH",

            font=ctk.CTkFont(

                size=27,

                weight="bold"

            )

        )

        logo.pack(

            pady=(35, 5)

        )


        subtitle = ctk.CTkLabel(

            self.sidebar,

            text="CYBER SECURITY LAB",

            text_color="#6b7280",

            font=ctk.CTkFont(

                size=12,

                weight="bold"

            )

        )

        subtitle.pack(

            pady=(0, 35)

        )


        self.dashboard_button = ctk.CTkButton(

            self.sidebar,

            text="URL SCANNER",

            height=45,

            command=self.show_scanner

        )

        self.dashboard_button.pack(

            padx=20,

            pady=8,

            fill="x"

        )


        self.history_button = ctk.CTkButton(

            self.sidebar,

            text="SCAN HISTORY",

            height=45,

            fg_color="transparent",

            border_width=1,

            command=self.show_history

        )

        self.history_button.pack(

            padx=20,

            pady=8,

            fill="x"

        )


        self.clear_button = ctk.CTkButton(

            self.sidebar,

            text="CLEAR SCANNER",

            height=45,

            fg_color="transparent",

            border_width=1,

            command=self.clear_scanner

        )

        self.clear_button.pack(

            padx=20,

            pady=8,

            fill="x"

        )


        self.export_button = ctk.CTkButton(

            self.sidebar,

            text="EXPORT REPORT",

            height=45,

            fg_color="transparent",

            border_width=1,

            command=self.export_report

        )

        self.export_button.pack(

            padx=20,

            pady=8,

            fill="x"

        )


        version = ctk.CTkLabel(

            self.sidebar,

            text="AI PHISHING DETECTOR\nVERSION 1.0",

            text_color="#4b5563",

            font=ctk.CTkFont(

                size=11

            )

        )

        version.pack(

            side="bottom",

            pady=30

        )


        # =================================================
        # CONTENT CONTAINER
        # =================================================

        self.content = ctk.CTkFrame(

            self,

            fg_color="transparent"

        )

        self.content.grid(

            row=0,

            column=1,

            sticky="nsew",

            padx=30,

            pady=25

        )


        self.content.grid_columnconfigure(

            0,

            weight=1

        )

        self.content.grid_rowconfigure(

            4,

            weight=1

        )


        # =================================================
        # HEADER
        # =================================================

        title = ctk.CTkLabel(

            self.content,

            text="AI PHISHING DETECTOR",

            font=ctk.CTkFont(

                size=30,

                weight="bold"

            )

        )

        title.grid(

            row=0,

            column=0,

            sticky="w"

        )


        description = ctk.CTkLabel(

            self.content,

            text=(
                "Analyze suspicious URLs using intelligent "
                "cybersecurity heuristics."
            ),

            text_color="#9ca3af"

        )

        description.grid(

            row=1,

            column=0,

            sticky="w",

            pady=(3, 20)

        )


        # =================================================
        # URL INPUT CARD
        # =================================================

        input_card = ctk.CTkFrame(

            self.content

        )

        input_card.grid(

            row=2,

            column=0,

            sticky="ew",

            pady=(0, 18)

        )


        input_card.grid_columnconfigure(

            0,

            weight=1

        )


        self.url_entry = ctk.CTkEntry(

            input_card,

            height=52,

            placeholder_text=(

                "Enter suspicious URL... "

                "Example: secure-account-login.example"

            ),

            font=ctk.CTkFont(

                size=15

            )

        )

        self.url_entry.grid(

            row=0,

            column=0,

            sticky="ew",

            padx=(18, 10),

            pady=18

        )


        scan_button = ctk.CTkButton(

            input_card,

            text="ANALYZE URL",

            width=160,

            height=52,

            font=ctk.CTkFont(

                weight="bold"

            ),

            command=self.scan_url

        )

        scan_button.grid(

            row=0,

            column=1,

            padx=(0, 18),

            pady=18

        )


        self.url_entry.bind(

            "<Return>",

            lambda event: self.scan_url()

        )


        # =================================================
        # RESULT CARD
        # =================================================

        self.result_card = ctk.CTkFrame(

            self.content

        )

        self.result_card.grid(

            row=3,

            column=0,

            sticky="ew",

            pady=(0, 18)

        )


        self.result_card.grid_columnconfigure(

            (0, 1, 2),

            weight=1

        )


        # STATUS

        status_title = ctk.CTkLabel(

            self.result_card,

            text="SECURITY STATUS",

            text_color="#9ca3af"

        )

        status_title.grid(

            row=0,

            column=0,

            pady=(18, 5)

        )


        self.status_label = ctk.CTkLabel(

            self.result_card,

            text="WAITING",

            font=ctk.CTkFont(

                size=23,

                weight="bold"

            )

        )

        self.status_label.grid(

            row=1,

            column=0,

            pady=(0, 18)

        )


        # SCORE

        score_title = ctk.CTkLabel(

            self.result_card,

            text="RISK SCORE",

            text_color="#9ca3af"

        )

        score_title.grid(

            row=0,

            column=1,

            pady=(18, 5)

        )


        self.score_label = ctk.CTkLabel(

            self.result_card,

            text="0 / 100",

            font=ctk.CTkFont(

                size=23,

                weight="bold"

            )

        )

        self.score_label.grid(

            row=1,

            column=1,

            pady=(0, 18)

        )


        # DOMAIN

        domain_title = ctk.CTkLabel(

            self.result_card,

            text="DETECTED DOMAIN",

            text_color="#9ca3af"

        )

        domain_title.grid(

            row=0,

            column=2,

            pady=(18, 5)

        )


        self.domain_label = ctk.CTkLabel(

            self.result_card,

            text="NONE",

            font=ctk.CTkFont(

                size=18,

                weight="bold"

            )

        )

        self.domain_label.grid(

            row=1,

            column=2,

            pady=(0, 18)

        )


        # =================================================
        # REPORT AREA
        # =================================================

        report_card = ctk.CTkFrame(

            self.content

        )

        report_card.grid(

            row=4,

            column=0,

            sticky="nsew"

        )


        report_card.grid_columnconfigure(

            0,

            weight=1

        )

        report_card.grid_rowconfigure(

            1,

            weight=1

        )


        report_title = ctk.CTkLabel(

            report_card,

            text="DETAILED SECURITY ANALYSIS",

            font=ctk.CTkFont(

                size=17,

                weight="bold"

            )

        )

        report_title.grid(

            row=0,

            column=0,

            sticky="w",

            padx=20,

            pady=(16, 8)

        )


        self.report_box = ctk.CTkTextbox(

            report_card,

            font=(

                "Consolas",

                13

            )

        )

        self.report_box.grid(

            row=1,

            column=0,

            sticky="nsew",

            padx=18,

            pady=(0, 18)

        )


        self.show_welcome_message()


    # =====================================================
    # WELCOME MESSAGE
    # =====================================================

    def show_welcome_message(self):

        self.report_box.delete(

            "1.0",

            "end"

        )


        message = """

============================================================
              FUZZUTECH AI PHISHING DETECTOR
============================================================

SYSTEM STATUS : ONLINE

SECURITY ENGINE : ACTIVE

THREAT ANALYSIS MODULE : READY


Enter a suspicious URL above and click ANALYZE URL.


The security engine will inspect:

[+] HTTPS encryption

[+] IP address usage

[+] Suspicious keywords

[+] URL length

[+] URL shortening services

[+] Punycode attacks

[+] Suspicious domain extensions

[+] Excessive subdomains

[+] Redirection patterns

[+] Encoded characters

[+] Query parameter anomalies


DISCLAIMER:

This application uses heuristic-based threat detection.

A low risk score does not guarantee that a website is safe.

Do not open unknown links without additional verification.

============================================================

"""

        self.report_box.insert(

            "end",

            message

        )


    # =====================================================
    # SCAN URL
    # =====================================================

    def scan_url(self):

        url = self.url_entry.get().strip()


        if not url:

            messagebox.showwarning(

                "Missing URL",

                "Please enter a URL to analyze."

            )

            return


        result = self.detector.analyze(url)


        self.current_result = result


        self.scan_history.insert(

            0,

            result

        )


        if len(self.scan_history) > 50:

            self.scan_history.pop()


        self.update_result(result)


    # =====================================================
    # UPDATE RESULT
    # =====================================================

    def update_result(self, result):

        score = result["score"]

        status = result["status"]


        if status == "SAFE":

            color = "#22c55e"

        elif status == "SUSPICIOUS":

            color = "#f59e0b"

        else:

            color = "#ef4444"


        self.status_label.configure(

            text=status,

            text_color=color

        )


        self.score_label.configure(

            text=f"{score} / 100",

            text_color=color

        )


        domain = result["domain"]


        if len(domain) > 32:

            domain = domain[:29] + "..."


        self.domain_label.configure(

            text=domain.upper()

        )


        self.report_box.delete(

            "1.0",

            "end"

        )


        report = f"""

============================================================
                    SECURITY SCAN REPORT
============================================================

SCAN TIME     : {result["scan_time"]}

TARGET URL    : {result["url"]}

DOMAIN        : {result["domain"]}

SECURITY      : {result["status"]}

RISK SCORE    : {result["score"]} / 100

CLASSIFICATION: {result["message"]}


============================================================
                    THREAT ANALYSIS
============================================================

"""


        for index, finding in enumerate(

            result["findings"],

            start=1

        ):

            level, text = finding

            report += (

                f"{index:02}. [{level}] {text}\n\n"

            )


        report += """

============================================================
                    SECURITY RECOMMENDATION
============================================================

"""


        if score <= 20:

            report += """

The URL shows few common phishing indicators.

However, verify the domain ownership and website reputation
before entering passwords or sensitive information.

"""

        elif score <= 50:

            report += """

The URL contains multiple suspicious indicators.

Avoid entering passwords, banking details, OTP codes,
credit card information, or personal information.

Perform additional domain reputation analysis.

"""

        else:

            report += """

HIGH-RISK URL DETECTED.

Do not open the website.

Do not download files.

Do not enter credentials.

Do not provide banking information or OTP codes.

Consider blocking and reporting the suspicious URL.

"""


        report += """

============================================================
                    END OF SECURITY REPORT
============================================================

"""


        self.report_box.insert(

            "end",

            report

        )


    # =====================================================
    # SHOW SCANNER
    # =====================================================

    def show_scanner(self):

        if self.current_result:

            self.update_result(

                self.current_result

            )

        else:

            self.show_welcome_message()


    # =====================================================
    # SHOW HISTORY
    # =====================================================

    def show_history(self):

        self.report_box.delete(

            "1.0",

            "end"

        )


        if not self.scan_history:

            self.report_box.insert(

                "end",

                "\n\nNO SCAN HISTORY AVAILABLE.\n"

            )

            return


        report = """

============================================================
                       SCAN HISTORY
============================================================

"""


        for index, result in enumerate(

            self.scan_history,

            start=1

        ):

            report += (

                f"{index:02}. "

                f"{result['scan_time']}\n"

                f"    DOMAIN : {result['domain']}\n"

                f"    STATUS : {result['status']}\n"

                f"    SCORE  : {result['score']} / 100\n"

                f"    URL    : {result['url']}\n"

                + "-" * 60

                + "\n\n"

            )


        self.report_box.insert(

            "end",

            report

        )


    # =====================================================
    # CLEAR SCANNER
    # =====================================================

    def clear_scanner(self):

        self.url_entry.delete(

            0,

            "end"

        )


        self.status_label.configure(

            text="WAITING",

            text_color=(

                "gray10",

                "gray90"

            )

        )


        self.score_label.configure(

            text="0 / 100",

            text_color=(

                "gray10",

                "gray90"

            )

        )


        self.domain_label.configure(

            text="NONE"

        )


        self.current_result = None


        self.show_welcome_message()


    # =====================================================
    # EXPORT REPORT
    # =====================================================

    def export_report(self):

        if not self.current_result:

            messagebox.showwarning(

                "No Report",

                "Scan a URL before exporting the report."

            )

            return


        filename = filedialog.asksaveasfilename(

            title="Export Security Report",

            defaultextension=".txt",

            filetypes=[

                ("Text Report", "*.txt"),

                ("All Files", "*.*")

            ]

        )


        if not filename:

            return


        report_text = self.report_box.get(

            "1.0",

            "end"

        )


        try:

            with open(

                filename,

                "w",

                encoding="utf-8"

            ) as file:

                file.write(report_text)


            messagebox.showinfo(

                "Report Exported",

                "Security report exported successfully."

            )


        except Exception as error:

            messagebox.showerror(

                "Export Error",

                str(error)

            )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app = PhishingDetectorApp()

    app.mainloop()