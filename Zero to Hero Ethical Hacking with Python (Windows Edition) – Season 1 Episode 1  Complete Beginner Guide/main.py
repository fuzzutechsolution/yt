import os
import sys
import json
import time
import string
import random
import base64
import hashlib
import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import psutil

# -------------------------------------------------------------
# Global Styles & Accent Color Configurations
# -------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Theme color scheme matching Cyberpunk/Obsidian/VS Code style
BG_DARK = "#0b0f19"         # Obsidian Deep Background
SIDEBAR_BG = "#0d1321"      # Slate Sidebar
CARD_BG = "#161f30"         # Translucent Card Dark
BORDER_COLOR = "#1e293b"    # Sleek slate borders
TEXT_PRIMARY = "#ffffff"    # Pure White
TEXT_SECONDARY = "#94a3b8"  # Muted silver grey
TEXT_MUTED = "#64748b"      # Dark grey

ACCENT_COLORS = {
    "Cyber Blue": {
        "accent": "#00f0ff",
        "accent_hover": "#00bcd4",
        "bg_glow": "#002a3a"
    },
    "Neon Green": {
        "accent": "#39ff14",
        "accent_hover": "#32cd32",
        "bg_glow": "#0a3a0a"
    },
    "Cyber Purple": {
        "accent": "#bd00ff",
        "accent_hover": "#9a00d4",
        "bg_glow": "#2b003a"
    }
}

# -------------------------------------------------------------
# AppState (JSON Persistence for progress, XP, settings)
# -------------------------------------------------------------
class AppState:
    def __init__(self):
        # Progress saved in local file cyber_hub_progress.json
        self.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyber_hub_progress.json")
        self.completed_lessons = []
        self.quiz_high_score = 0
        self.xp = 0
        self.level = 1
        self.achievements = []
        self.settings = {
            "accent_color": "Cyber Blue",
            "font_size": "Standard",
            "dark_theme": True
        }
        self.load()

    def save(self):
        try:
            data = {
                "completed_lessons": self.completed_lessons,
                "quiz_high_score": self.quiz_high_score,
                "xp": self.xp,
                "level": self.level,
                "achievements": self.achievements,
                "settings": self.settings
            }
            with open(self.filepath, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    self.completed_lessons = data.get("completed_lessons", [])
                    self.quiz_high_score = data.get("quiz_high_score", 0)
                    self.xp = data.get("xp", 0)
                    self.level = data.get("level", 1)
                    self.achievements = data.get("achievements", [])
                    self.settings = data.get("settings", self.settings)
            except Exception as e:
                print(f"Error loading progress: {e}")

    def complete_lesson(self, lesson_id):
        if lesson_id not in self.completed_lessons:
            self.completed_lessons.append(lesson_id)
            self.add_xp(50)
            self.check_achievements()
            self.save()
            return True
        return False

    def update_quiz_score(self, score):
        if score > self.quiz_high_score:
            self.quiz_high_score = score
        self.add_xp(score * 10)
        self.check_achievements()
        self.save()

    def add_xp(self, amount):
        self.xp += amount
        self.level = 1 + self.xp // 500
        self.save()

    def check_achievements(self):
        new_ach = []
        if len(self.completed_lessons) >= 1 and "First Step" not in self.achievements:
            new_ach.append("First Step")
        if len(self.completed_lessons) >= 6 and "Knowledge Seeker" not in self.achievements:
            new_ach.append("Knowledge Seeker")
        if len(self.completed_lessons) >= 11 and "Master Thinker" not in self.achievements:
            new_ach.append("Master Thinker")
        if self.quiz_high_score >= 10 and "Competent Hacker" not in self.achievements:
            new_ach.append("Competent Hacker")
        if self.quiz_high_score >= 20 and "Certified Genius" not in self.achievements:
            new_ach.append("Certified Genius")
        if self.xp >= 1000 and "XP Collector" not in self.achievements:
            new_ach.append("XP Collector")
            
        for a in new_ach:
            self.achievements.append(a)

    def reset_progress(self):
        self.completed_lessons = []
        self.quiz_high_score = 0
        self.xp = 0
        self.level = 1
        self.achievements = []
        self.save()

# -------------------------------------------------------------
# Curated Quiz Content (20 cybersecurity & Python MCQ)
# -------------------------------------------------------------
QUIZ_QUESTIONS = [
    {
        "question": "What is the primary goal of Confidentiality in the CIA Triad?",
        "options": [
            "Ensuring only authorized individuals have access to the data",
            "Ensuring data remains accurate and has not been altered",
            "Ensuring systems and networks are available when requested",
            "Ensuring that all user passwords are encrypted using MD5"
        ],
        "answer": 0,
        "explanation": "Confidentiality ensures that sensitive information is accessible only to those authorized to have access."
    },
    {
        "question": "Which of the following describes the 'Integrity' pillar of the CIA Triad?",
        "options": [
            "Keeping system components online during an attack",
            "Preventing unauthorized readout of private user records",
            "Ensuring information is accurate, complete, and uncorrupted",
            "Making sure servers are backed up in multiple geographic regions"
        ],
        "answer": 2,
        "explanation": "Integrity is about preserving the correctness and consistency of data throughout its lifecycle."
    },
    {
        "question": "How does 'Authentication' differ from 'Authorization'?",
        "options": [
            "Authentication is one-way hashing; Authorization is two-way encryption",
            "Authentication verifies who you are; Authorization verifies what you can access",
            "Authentication works on networks; Authorization works on applications",
            "Authentication requires a firewall; Authorization requires an antivirus"
        ],
        "answer": 1,
        "explanation": "Authentication checks identity (e.g. log in). Authorization checks permissions and access rights."
    },
    {
        "question": "What is the primary code of conduct for an 'Ethical Hacker'?",
        "options": [
            "Hacking target systems first, then asking for payment to reveal bugs",
            "Operating with explicit authorization and strictly within scope",
            "Sharing discovered vulnerabilities on public social networks immediately",
            "Infiltrating competitor companies to steal their proprietary scripts"
        ],
        "answer": 1,
        "explanation": "Ethical hacking requires written permission, clear scope limits, and adherence to laws."
    },
    {
        "question": "What does the term 'Responsible Disclosure' refer to?",
        "options": [
            "Posting a bug on forums immediately to force vendors to patch it",
            "Selling the exploit code to the highest bidder on dark web auctions",
            "Reporting a vulnerability privately to the vendor and allowing time for a fix before publishing",
            "Anonymously sending exploit payloads to database servers"
        ],
        "answer": 2,
        "explanation": "Responsible disclosure gives the vendor time to release a security update before the vulnerability is made public."
    },
    {
        "question": "Which of the following is considered a core practice of 'Cyber Hygiene'?",
        "options": [
            "Using the same strong password for all accounts so you don't lose it",
            "Disabling multi-factor authentication (MFA) to avoid locks",
            "Running system updates and security patches as soon as they are released",
            "Opening all email attachments from unknown senders to inspect them"
        ],
        "answer": 2,
        "explanation": "Keeping systems up to date with patches is critical to close known security vulnerabilities."
    },
    {
        "question": "What defines a 'White Hat' hacker?",
        "options": [
            "A hacker who operates with permission to improve security posturing",
            "A hacker who acts maliciously for political protest (hacktivist)",
            "A hacker who breaches systems without permission but releases patches",
            "A hacker working strictly to steal financial banking coordinates"
        ],
        "answer": 0,
        "explanation": "White hats use their skills legally to help organizations identify and fix flaws."
    },
    {
        "question": "Which port does standard secure web communication (HTTPS) run on?",
        "options": [
            "Port 80",
            "Port 22",
            "Port 443",
            "Port 8080"
        ],
        "answer": 2,
        "explanation": "HTTPS runs on TCP port 443. Non-secure HTTP runs on TCP port 80."
    },
    {
        "question": "Which security tool is primarily designed for real-time network packet analysis?",
        "options": [
            "Nmap",
            "Wireshark",
            "Burp Suite",
            "Git"
        ],
        "answer": 1,
        "explanation": "Wireshark is a packet sniffer that captures and inspects traffic flowing over network interfaces."
    },
    {
        "question": "What is the primary function of Nmap?",
        "options": [
            "Intercepting web requests and tampering with form data",
            "Compiling Python source code into binary executables",
            "Network scanning, host discovery, and port enumeration",
            "Encrypting local system files to request a recovery ransom"
        ],
        "answer": 2,
        "explanation": "Nmap is used to scan networks to find active hosts, open ports, and running services."
    },
    {
        "question": "What is the main difference between Hashing and Encryption?",
        "options": [
            "Hashing is two-way; Encryption is one-way only",
            "Hashing is one-way (irreversible); Encryption is two-way (reversible)",
            "Hashing is for files; Encryption is for network interfaces only",
            "Hashing is insecure; Encryption is always secure"
        ],
        "answer": 1,
        "explanation": "Hashing maps data to a fixed-size representation that cannot be mathematically reversed. Encryption can be decrypted with a key."
    },
    {
        "question": "Which standard Python library is used to generate cryptographic hashes like SHA-256?",
        "options": [
            "cryptography",
            "socket",
            "hashlib",
            "psutil"
        ],
        "answer": 2,
        "explanation": "Python's built-in 'hashlib' module provides interfaces for SHA256, SHA1, MD5, and other hashing algorithms."
    },
    {
        "question": "What is the main benefit of using a Python virtual environment (venv)?",
        "options": [
            "It makes your Python scripts execute up to 5x faster",
            "It isolates project dependencies, preventing version conflicts",
            "It automatically uploads your security scripts to a remote cloud backup",
            "It encrypts your Python scripts to protect them from theft"
        ],
        "answer": 1,
        "explanation": "Virtual environments isolate packages needed by different projects, avoiding global dependency clutter."
    },
    {
        "question": "In Python OOP, what does the '__init__' method do?",
        "options": [
            "It starts the Python interpreter loop",
            "It serves as the constructor to initialize a newly created object",
            "It imports external library modules",
            "It deletes class variables from runtime memory"
        ],
        "answer": 1,
        "explanation": "The __init__ method is automatically called when a new instance of a class is created."
    },
    {
        "question": "What is Burp Suite primarily used for by security professionals?",
        "options": [
            "Analyzing Windows system processes and active CPU registers",
            "Writing and versioning security scripting code",
            "Intercepting, analyzing, and tampering with HTTP traffic",
            "Scanning remote subnets for active open SSH ports"
        ],
        "answer": 2,
        "explanation": "Burp Suite is a web proxy tool widely used for penetration testing of web applications."
    },
    {
        "question": "What is the role of the 'socket' library in Python?",
        "options": [
            "Generating randomized cryptographic passwords",
            "Providing low-level network communication interfaces",
            "Designing glassmorphic graphical user interfaces",
            "Monitoring system process lists and RAM statistics"
        ],
        "answer": 1,
        "explanation": "The socket library allows Python scripts to open TCP/UDP connections and send/receive raw bytes."
    },
    {
        "question": "In cryptography, what is 'Salting'?",
        "options": [
            "Adding random data to inputs before hashing to protect against rainbow table attacks",
            "Encrypting a file multiple times with different secret keys",
            "Sending fake packets over a network to confuse sniffing tools",
            "Compressing hash files to save disk storage space"
        ],
        "answer": 0,
        "explanation": "Salting adds unique random strings to passwords before hashing, ensuring identical passwords have different hash values."
    },
    {
        "question": "What service is responsible for translating human-readable hostnames to IP addresses?",
        "options": [
            "DHCP",
            "DNS",
            "FTP",
            "SSH"
        ],
        "answer": 1,
        "explanation": "DNS (Domain Name System) maps hostnames like 'google.com' to computer-readable IP addresses."
    },
    {
        "question": "Which of the following Python modules is standard for tracking process and system resource usage?",
        "options": [
            "psutil",
            "os",
            "sys",
            "pathlib"
        ],
        "answer": 0,
        "explanation": "psutil (process and system utilities) is a cross-platform library for retrieving information on running processes and system utilization."
    },
    {
        "question": "What is 'Application Security' focused on?",
        "options": [
            "Analyzing hardware physical vulnerabilities in microcontrollers",
            "Finding, fixing, and preventing vulnerabilities in software code",
            "Protecting wide area network lines and routers from DDoS",
            "Collecting evidence from storage disks for legal trials"
        ],
        "answer": 1,
        "explanation": "Application security focuses on securing app logic and code against attacks like injection or cross-site scripting."
    }
]

# -------------------------------------------------------------
# Reusable Custom Widgets
# -------------------------------------------------------------
class GlassCard(ctk.CTkFrame):
    """Modern translucent glassmorphic card widget with neon border highlights on hover."""
    def __init__(self, master, hover_effect=True, **kwargs):
        fg_color = kwargs.pop("fg_color", CARD_BG)
        border_color = kwargs.pop("border_color", BORDER_COLOR)
        border_width = kwargs.pop("border_width", 2)
        corner_radius = kwargs.pop("corner_radius", 12)
        
        super().__init__(
            master, 
            fg_color=fg_color, 
            border_color=border_color, 
            border_width=border_width, 
            corner_radius=corner_radius, 
            **kwargs
        )
        self.hover_effect = hover_effect
        self.default_border = border_color

        if self.hover_effect:
            self.bind("<Enter>", self.on_hover)
            self.bind("<Leave>", self.off_hover)
            self.bind_children_hover(self)

    def bind_children_hover(self, widget):
        for child in widget.winfo_children():
            # Apply enter/leave event triggers recursively down the widget tree
            child.bind("<Enter>", lambda e: self.on_hover(), add="+")
            child.bind("<Leave>", lambda e: self.off_hover(), add="+")
            self.bind_children_hover(child)

    def on_hover(self, event=None):
        accent = getattr(self.winfo_toplevel(), "accent_color", "#00f0ff")
        self.configure(border_color=accent)

    def off_hover(self, event=None):
        self.configure(border_color=self.default_border)


class GradientCard(ctk.CTkFrame):
    """Displays a CTkFrame with a custom linear gradient canvas background."""
    def __init__(self, master, color_start="#0055ff", color_end="#00ffcc", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.color_start = color_start
        self.color_end = color_end
        self.canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.draw_gradient)

    def draw_gradient(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        r1, g1, b1 = self.hex_to_rgb(self.color_start)
        r2, g2, b2 = self.hex_to_rgb(self.color_end)
        
        for x in range(w):
            t = x / w
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(x, 0, x, h, fill=color)

    def hex_to_rgb(self, hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


class SyntaxTextBox(ctk.CTkTextbox):
    """Custom read-only text box widget that parses and syntax-highlights Python snippets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(font=("Consolas", 12))
        self.tag_config("keyword", foreground="#ff79c6")  # Dracula Pink
        self.tag_config("string", foreground="#f1fa8c")   # Dracula Yellow
        self.tag_config("comment", foreground="#6272a4")  # Dracula Comment Grey
        self.tag_config("number", foreground="#bd93f9")   # Dracula Purple
        self.tag_config("builtin", foreground="#8be9fd")  # Dracula Cyan
        self.tag_config("def", foreground="#50fa7b")      # Dracula Green

    def set_code(self, code_text):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.insert("1.0", code_text)
        self.highlight()
        self.configure(state="disabled")

    def highlight(self):
        text = self.get("1.0", "end")
        for tag in ["keyword", "string", "comment", "number", "builtin", "def"]:
            self.tag_remove(tag, "1.0", "end")

        import re
        keywords = r"\b(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b"
        builtins = r"\b(print|len|range|int|str|float|list|dict|set|tuple|type|open|abs|all|any|sum|max|min)\b"
        
        # 1. Comments
        for m in re.finditer(r"#.*", text):
            self.tag_add("comment", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")
            
        # 2. Strings
        for m in re.finditer(r"(['\"])(.*?)\1", text):
            self.tag_add("string", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

        # 3. Keywords
        for m in re.finditer(keywords, text):
            self.tag_add("keyword", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

        # 4. Builtins
        for m in re.finditer(builtins, text):
            self.tag_add("builtin", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")

        # 5. Numbers
        for m in re.finditer(r"\b\d+\b", text):
            self.tag_add("number", f"1.0 + {m.start()} chars", f"1.0 + {m.end()} chars")


class PerformanceChart(tk.Canvas):
    """Custom canvas-drawn responsive bar chart representing domain stats."""
    def __init__(self, parent, data=None, color_accent="#00f0ff", **kwargs):
        super().__init__(parent, bg=CARD_BG, highlightthickness=0, **kwargs)
        self.data = data or {}
        self.color_accent = color_accent
        self.bind("<Configure>", self.draw_chart)

    def update_data(self, data, color_accent=None):
        self.data = data
        if color_accent:
            self.color_accent = color_accent
        self.draw_chart()

    def draw_chart(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 50 or h < 50:
            return

        p_left = 60
        p_right = 20
        p_top = 30
        p_bottom = 40

        chart_w = w - p_left - p_right
        chart_h = h - p_top - p_bottom

        # Grid lines (0%, 25%, 50%, 75%, 100%)
        for i in range(5):
            y = p_top + chart_h - (i / 4.0) * chart_h
            val = i * 25
            self.create_line(p_left, y, w - p_right, y, fill="#233554", dash=(4, 4))
            self.create_text(p_left - 10, y, text=f"{val}%", fill=TEXT_SECONDARY, font=("Segoe UI", 9), anchor="e")

        if not self.data:
            return

        items = list(self.data.items())
        num_bars = len(items)
        if num_bars == 0:
            return

        spacing = chart_w / num_bars
        bar_w = spacing * 0.5

        for idx, (label, val) in enumerate(items):
            cx = p_left + (idx + 0.5) * spacing
            x1 = cx - bar_w / 2
            x2 = cx + bar_w / 2
            
            bar_h = (val / 100.0) * chart_h
            y1 = p_top + chart_h - bar_h
            y2 = p_top + chart_h

            # Glow effect behind the bar
            self.create_rectangle(x1 - 2, y1 - 2, x2 + 2, y2, fill="", outline=self.color_accent, width=1)
            self.create_rectangle(x1, y1, x2, y2, fill=self.color_accent, outline="")
            
            self.create_text(cx, p_top + chart_h + 15, text=label, fill=TEXT_PRIMARY, font=("Segoe UI", 10, "bold"))
            self.create_text(cx, y1 - 12, text=f"{val}%", fill=self.color_accent, font=("Segoe UI", 10, "bold"))


class RoadmapTimeline(tk.Canvas):
    """Horizontal interactive roadmap timeline showing 4 training milestones."""
    def __init__(self, parent, current_season=1, **kwargs):
        super().__init__(parent, bg=CARD_BG, highlightthickness=0, **kwargs)
        self.current_season = current_season
        self.bind("<Configure>", self.draw_timeline)

    def set_season(self, season):
        self.current_season = season
        self.draw_timeline()

    def draw_timeline(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 100 or h < 50:
            return

        y_center = h / 2
        margin = 80
        line_w = w - 2 * margin
        self.create_line(margin, y_center, w - margin, y_center, fill="#1e293b", width=6)

        seasons = [
            ("Season 1", "Foundations", "Python Basics, CIA Triad, Networking"),
            ("Season 2", "Tools Mastery", "Nmap scans, Wireshark packet capture"),
            ("Season 3", "Interactive Labs", "Hashing, check sums, generators"),
            ("Season 4", "Advanced Pentesting", "Web app proxy, exploit scripting")
        ]

        step = line_w / 3
        for idx, (title, subtitle, desc) in enumerate(seasons):
            cx = margin + idx * step
            cy = y_center

            is_active = (idx + 1) <= self.current_season
            color = "#39ff14" if is_active else "#64748b"
            glow_color = "#00f0ff" if is_active else "#1e293b"

            # Connect line highlight
            if idx > 0 and is_active:
                prev_cx = margin + (idx - 1) * step
                self.create_line(prev_cx, y_center, cx, y_center, fill="#39ff14", width=6)

            # Node glow & circle
            self.create_oval(cx - 16, cy - 16, cx + 16, cy + 16, fill="#0b0f19", outline=glow_color, width=4)
            self.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=color, outline="")

            # Text Labels
            self.create_text(cx, cy - 40, text=title, fill=color, font=("Segoe UI", 12, "bold"))
            self.create_text(cx, cy - 22, text=subtitle, fill=TEXT_PRIMARY, font=("Segoe UI", 10))
            
            # Multi-line descriptions
            lines = desc.split(", ")
            offset_y = 35
            for line in lines:
                self.create_text(cx, cy + offset_y, text=line, fill=TEXT_SECONDARY, font=("Segoe UI", 9), width=step - 10)
                offset_y += 15

# -------------------------------------------------------------
# Base Page Class & View Implementations
# -------------------------------------------------------------
class PageFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.state = app.app_state

    def update_view(self):
        """Called automatically when the page is navigated to, allowing dynamic updates."""
        pass


class DashboardPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        
        # Grid settings
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Welcome Gradient Card
        self.welcome_card = GradientCard(self, color_start="#00f0ff", color_end="#1e293b", height=130)
        self.welcome_card.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="nsew")
        self.welcome_card.pack_propagate(False)

        # Content on top of Welcome Canvas
        lbl_frame = ctk.CTkFrame(self.welcome_card, fg_color="transparent")
        lbl_frame.pack(side="left", padx=30, fill="y")
        
        self.welcome_lbl = ctk.CTkLabel(
            lbl_frame, 
            text="Welcome Agent, FuzzuTech", 
            font=("Segoe UI", 24, "bold"), 
            text_color=TEXT_PRIMARY, 
            anchor="w"
        )
        self.welcome_lbl.pack(pady=(20, 2))
        
        self.sub_lbl = ctk.CTkLabel(
            lbl_frame, 
            text="Season 1: Zero to Hero – Ethical Hacking with Python", 
            font=("Segoe UI", 13), 
            text_color="#00f0ff", 
            anchor="w"
        )
        self.sub_lbl.pack()

        # Stats Cards Grid
        self.stats_container = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_container.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.stats_container.grid_columnconfigure((0, 1), weight=1)
        self.stats_container.grid_rowconfigure((0, 1), weight=1)

        self.card_level = GlassCard(self.stats_container)
        self.card_level.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.lbl_level_val = ctk.CTkLabel(self.card_level, text="1", font=("Segoe UI", 36, "bold"), text_color="#39ff14")
        self.lbl_level_val.pack(expand=True, pady=(15, 2))
        ctk.CTkLabel(self.card_level, text="🎖 Current Level", font=("Segoe UI", 13), text_color=TEXT_SECONDARY).pack(pady=(0, 15))

        self.card_xp = GlassCard(self.stats_container)
        self.card_xp.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.lbl_xp_val = ctk.CTkLabel(self.card_xp, text="0", font=("Segoe UI", 36, "bold"), text_color="#00f0ff")
        self.lbl_xp_val.pack(expand=True, pady=(15, 2))
        ctk.CTkLabel(self.card_xp, text="⚡ Total XP", font=("Segoe UI", 13), text_color=TEXT_SECONDARY).pack(pady=(0, 15))

        self.card_lessons = GlassCard(self.stats_container)
        self.card_lessons.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.lbl_less_val = ctk.CTkLabel(self.card_lessons, text="0 / 11", font=("Segoe UI", 36, "bold"), text_color="#bd00ff")
        self.lbl_less_val.pack(expand=True, pady=(15, 2))
        ctk.CTkLabel(self.card_lessons, text="📖 Lessons Completed", font=("Segoe UI", 13), text_color=TEXT_SECONDARY).pack(pady=(0, 15))

        self.card_quiz = GlassCard(self.stats_container)
        self.card_quiz.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.lbl_quiz_val = ctk.CTkLabel(self.card_quiz, text="0", font=("Segoe UI", 36, "bold"), text_color="#ffcc00")
        self.lbl_quiz_val.pack(expand=True, pady=(15, 2))
        ctk.CTkLabel(self.card_quiz, text="📝 Quiz High Score", font=("Segoe UI", 13), text_color=TEXT_SECONDARY).pack(pady=(0, 15))

        # Overview & Recommended Lesson Frame
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=1, column=1, padx=15, pady=5, sticky="nsew")
        self.right_container.grid_columnconfigure(0, weight=1)
        self.right_container.grid_rowconfigure((0, 1), weight=1)

        # Recommendation Card
        self.rec_card = GlassCard(self.right_container)
        self.rec_card.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.rec_title = ctk.CTkLabel(self.rec_card, text="Recommended Lesson", font=("Segoe UI", 16, "bold"), text_color="#00f0ff")
        self.rec_title.pack(anchor="w", padx=20, pady=(15, 5))
        self.rec_text = ctk.CTkLabel(
            self.rec_card, 
            text="Recommended lessons load here...", 
            font=("Segoe UI", 12), 
            text_color=TEXT_SECONDARY, 
            justify="left", 
            wraplength=350
        )
        self.rec_text.pack(anchor="w", padx=20, pady=5)
        
        self.rec_btn = ctk.CTkButton(
            self.rec_card, 
            text="Jump to Lesson", 
            font=("Segoe UI", 11, "bold"),
            command=lambda: self.app.switch_page("Learn")
        )
        self.rec_btn._is_accent_btn = True
        self.rec_btn.pack(anchor="w", padx=20, pady=(10, 15))

        # Course overview summary card
        self.summary_card = GlassCard(self.right_container)
        self.summary_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        ctk.CTkLabel(self.summary_card, text="Course Progress", font=("Segoe UI", 16, "bold"), text_color="#39ff14").pack(anchor="w", padx=20, pady=(15, 5))
        
        self.bar_lbl = ctk.CTkLabel(self.summary_card, text="Level Progress (0/500 XP to next Level)", font=("Segoe UI", 11), text_color=TEXT_SECONDARY)
        self.bar_lbl.pack(anchor="w", padx=20, pady=(5, 2))
        
        self.prog_bar = ctk.CTkProgressBar(self.summary_card, height=8, fg_color="#1e293b")
        self.prog_bar._is_accent_progress = True
        self.prog_bar.pack(fill="x", padx=20, pady=10)

        # Quick access layout
        qa_frame = ctk.CTkFrame(self.summary_card, fg_color="transparent")
        qa_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        btn_lab = ctk.CTkButton(qa_frame, text="🧪 Labs", width=80, command=lambda: self.app.switch_page("Mini Labs"))
        btn_lab._is_accent_btn = True
        btn_lab.pack(side="left", padx=5)
        
        btn_quiz = ctk.CTkButton(qa_frame, text="📝 Quiz", width=80, command=lambda: self.app.switch_page("Quiz"))
        btn_quiz._is_accent_btn = True
        btn_quiz.pack(side="left", padx=5)
        
        btn_map = ctk.CTkButton(qa_frame, text="🗺 Roadmap", width=80, command=lambda: self.app.switch_page("Roadmap"))
        btn_map._is_accent_btn = True
        btn_map.pack(side="left", padx=5)

    def update_view(self):
        # Read stats from state
        self.lbl_level_val.configure(text=str(self.state.level))
        self.lbl_xp_val.configure(text=str(self.state.xp))
        self.lbl_less_val.configure(text=f"{len(self.state.completed_lessons)} / 11")
        self.lbl_quiz_val.configure(text=f"{self.state.quiz_high_score} / 20")

        # Level XP Progress Bar
        level_start_xp = (self.state.level - 1) * 500
        current_level_xp = self.state.xp - level_start_xp
        percent = current_level_xp / 500.0
        self.prog_bar.set(percent)
        self.bar_lbl.configure(text=f"Level Progress ({current_level_xp} / 500 XP)")

        # Recommended Lesson text computation
        lesson_meta = [
            ("intro", "What is Cybersecurity", "Learn the essential definitions of information safety and defensive measures."),
            ("cia", "The CIA Triad", "Explore the pillars of secure systems: Confidentiality, Integrity, and Availability."),
            ("auth", "Authentication & AuthZ", "Understand authorization boundaries and verifying identities securely."),
            ("ethical", "Ethical Hacking Rules", "Analyze laws, boundaries, and authorization permissions of white hat security."),
            ("disclosure", "Responsible Disclosure", "Discover the pathways of reporting vulnerabilities safely to vendors."),
            ("hygiene", "Cyber Hygiene Rules", "Learn about multi-factor authentication, robust update pipelines, and passwords."),
            ("hackers", "Types of Hackers", "Examine categories: White Hats, Black Hats, and Grey Hat hacking profiles."),
            ("netsec", "Network Security", "Analyze routers, firewalls, and ethernet protocol layers."),
            ("appsec", "Application Security", "Discover source auditing, injection shielding, and software patches."),
            ("cloudsec", "Cloud Security", "Learn about cloud endpoints, databases, and encryption nodes."),
            ("forensics", "Digital Forensics", "Explore disc preservation, log investigations, and audit lines.")
        ]
        
        recs = [m for m in lesson_meta if m[0] not in self.state.completed_lessons]
        if recs:
            next_id, next_title, next_desc = recs[0]
            self.rec_title.configure(text=f"Next Up: {next_title}")
            self.rec_text.configure(text=next_desc)
            self.rec_btn.configure(state="normal")
        else:
            self.rec_title.configure(text="All Lessons Complete!")
            self.rec_text.configure(text="Excellent work! Test your cybersecurity knowledge in the Quiz page.")
            self.rec_btn.configure(state="disabled")


class LearnPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left scrollable list of lessons
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Lessons details list
        self.lessons = [
            {
                "id": "intro",
                "title": "What is Cybersecurity",
                "content": (
                    "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks. "
                    "These cyberattacks are usually aimed at accessing, changing, or destroying sensitive information; "
                    "extorting money from users; or interrupting normal business processes.\n\n"
                    "In modern society, where systems control banking, power grids, communication, and intelligence, "
                    "defensive code acts as the digital infrastructure shield safeguarding human operations. A failure "
                    "to write secure software introduces devastating pathways for data breaches and corporate espionage."
                )
            },
            {
                "id": "cia",
                "title": "The CIA Triad",
                "content": (
                    "The CIA Triad is a fundamental cybersecurity model designed to guide information security policies:\n\n"
                    "• Confidentiality: Ensuring that information is not disclosed to unauthorized individuals, entities, or processes. "
                    "Common measures include end-to-end encryption, multi-factor authentication, and strict user access lists.\n\n"
                    "• Integrity: Preserving the accuracy, completeness, and validity of data throughout its lifecycle. This implies "
                    "data cannot be modified undetected. Measures include file checksum hashing (SHA256) and audit logging.\n\n"
                    "• Availability: Ensuring that authorized users have reliable and prompt access to systems and databases. "
                    "Maintained using server load balancing, RAID storage, backups, and DDoS protection frameworks."
                )
            },
            {
                "id": "auth",
                "title": "Authentication vs. Authorization",
                "content": (
                    "• Authentication (AuthN): The process of verifying who a user claims to be. It answers 'Who are you?'. "
                    "Implemented using user credentials (usernames/passwords), biometric sensors, security tokens, or MFA.\n\n"
                    "• Authorization (AuthZ): The process of verifying what resources or operations a verified user can access. "
                    "It answers 'What permissions do you have?'. Implemented using RBAC (Role-Based Access Control) models."
                )
            },
            {
                "id": "ethical",
                "title": "Ethical Hacking Principles",
                "content": (
                    "Ethical Hacking is the authorized testing of systems to uncover vulnerabilities before malicious hackers can exploit them.\n\n"
                    "Key Principles of Ethical Conduct:\n"
                    "1. Explicit Permission: A penetration tester must hold written, legally binding permission (Rules of Engagement) before touching target infrastructure.\n"
                    "2. Scope Definition: Testing must occur strictly inside defined IP boundaries. Crossing lines is illegal.\n"
                    "3. Professional Honesty: Discovered flaws must be reported comprehensively, detailing risk metrics and remediation steps without tampering with data."
                )
            },
            {
                "id": "disclosure",
                "title": "Responsible Disclosure",
                "content": (
                    "Responsible Disclosure is a vulnerability reporting model where security researchers discover a bug and alert "
                    "the vendor privately. The vendor is granted a standard timeline (e.g., 90 days) to deploy a security patch "
                    "before public release.\n\n"
                    "This prevents malicious threat actors from constructing zero-day exploits, ensuring software ecosystems remain "
                    "safe. Many corporations facilitate bug bounty programs to incentivize researchers to execute responsible disclosure."
                )
            },
            {
                "id": "hygiene",
                "title": "Cyber Hygiene",
                "content": (
                    "Cyber Hygiene is a set of practices users and organizations perform regularly to maintain device health and block intrusions:\n\n"
                    "• Multi-Factor Authentication (MFA): Adding layers beyond passwords (authenticator apps, physical security keys).\n"
                    "• Patch Management: Updating operating systems, apps, and dependencies immediately to eliminate known vulnerabilities.\n"
                    "• Password Hygiene: Using non-repeating, high-entropy passwords stored in trusted vaults.\n"
                    "• Asset Control: Disabling unused services, ports, and software libraries to reduce the attack surface."
                )
            },
            {
                "id": "hackers",
                "title": "Types of Hackers",
                "content": (
                    "Hacker profiles are defined by intent and authorization:\n\n"
                    "• White Hat Hackers: Ethical security professionals, consultants, and developers who work with permission to patch flaws.\n"
                    "• Black Hat Hackers: Malicious actors executing exploits for ransomware, theft, and disruption without permission.\n"
                    "• Grey Hat Hackers: Hackers who probe systems without authorization but report flaws to owners instead of executing damage. "
                    "Though non-malicious, this remains legally problematic."
                )
            },
            {
                "id": "netsec",
                "title": "Network Security",
                "content": (
                    "Network Security focuses on safeguarding the integrity and usability of data traveling over communication lines.\n\n"
                    "Key concepts include firewalls (packet filtering, stateful inspections), Intrusion Detection Systems (IDS), Virtual "
                    "Private Networks (VPNs) for secure tunneling, and analysis of network packets (Ethernet, IP, TCP/UDP headers) to "
                    "identify active threat payloads."
                )
            },
            {
                "id": "appsec",
                "title": "Application Security",
                "content": (
                    "Application Security covers measures taken during the software development lifecycle (SDLC) to protect code.\n\n"
                    "This includes secure coding practices, input validation to prevent SQL Injection (SQLi) and Cross-Site Scripting (XSS), "
                    "static application security testing (SAST), dynamic testing (DAST), and automated package dependency updates."
                )
            },
            {
                "id": "cloudsec",
                "title": "Cloud Security",
                "content": (
                    "Cloud Security handles security controls protecting cloud assets (AWS, GCP, Azure).\n\n"
                    "Key aspects focus on the Shared Responsibility Model (cloud provider secures the hardware, user secures configurations "
                    "and data), identity management, API endpoint shielding, and utilizing cloud encryption keys to secure data-at-rest and transit."
                )
            },
            {
                "id": "forensics",
                "title": "Digital Forensics",
                "content": (
                    "Digital Forensics is the identification, preservation, analysis, and presentation of digital evidence.\n\n"
                    "Investigators map system compromises, recover deleted registry records, inspect security event logs, and build "
                    "cryptographically signed disk clones (bitstream copies) to preserve data integrity for presentation in legal systems."
                )
            }
        ]

        self.card_widgets = {}
        self.draw_lesson_cards()

    def draw_lesson_cards(self):
        for idx, lesson in enumerate(self.lessons):
            card = GlassCard(self.scroll_frame, hover_effect=True)
            card.pack(fill="x", padx=10, pady=5)
            
            # Header line: Title + Status label
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=10)
            
            lbl_title = ctk.CTkLabel(header_frame, text=lesson["title"], font=("Segoe UI", 16, "bold"), text_color=TEXT_PRIMARY)
            lbl_title.pack(side="left")
            
            lbl_status = ctk.CTkLabel(header_frame, text="⏳ Uncompleted", font=("Segoe UI", 11, "bold"), text_color=TEXT_SECONDARY)
            lbl_status.pack(side="right")
            
            # Hidden detail section
            detail_frame = ctk.CTkFrame(card, fg_color="transparent")
            
            lbl_content = ctk.CTkLabel(
                detail_frame, 
                text=lesson["content"], 
                font=("Segoe UI", 13), 
                text_color=TEXT_SECONDARY, 
                justify="left", 
                wraplength=1000
            )
            lbl_content.pack(anchor="w", padx=20, pady=10)
            
            btn_complete = ctk.CTkButton(
                detail_frame, 
                text="✓ Mark Completed (+50 XP)", 
                font=("Segoe UI", 12, "bold"),
                command=lambda lid=lesson["id"]: self.complete_lesson_action(lid)
            )
            btn_complete._is_accent_btn = True
            btn_complete.pack(anchor="w", padx=20, pady=(5, 15))

            # Bind header click to toggle detail expansion
            lbl_title.bind("<Button-1>", lambda e, f=detail_frame: self.toggle_details(f))
            header_frame.bind("<Button-1>", lambda e, f=detail_frame: self.toggle_details(f))

            self.card_widgets[lesson["id"]] = {
                "card": card,
                "detail_frame": detail_frame,
                "lbl_status": lbl_status,
                "btn_complete": btn_complete
            }

    def toggle_details(self, frame):
        if frame.winfo_viewable():
            frame.pack_forget()
        else:
            frame.pack(fill="x", expand=True)

    def complete_lesson_action(self, lesson_id):
        if self.state.complete_lesson(lesson_id):
            self.update_view()
            self.app.apply_accent()
            messagebox.showinfo("Security Center", "Lesson completed! Added 50 XP to your agent profile.")
        else:
            messagebox.showinfo("Security Center", "You have already completed this lesson.")

    def update_view(self):
        for lid, widgets in self.card_widgets.items():
            if lid in self.state.completed_lessons:
                widgets["lbl_status"].configure(text="✓ Completed", text_color="#39ff14")
                widgets["btn_complete"].configure(state="disabled", text="Completed")
            else:
                widgets["lbl_status"].configure(text="⏳ Uncompleted", text_color=TEXT_SECONDARY)
                widgets["btn_complete"].configure(state="normal", text="✓ Mark Completed (+50 XP)")


class PythonPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=2)  # Topic List
        self.grid_columnconfigure(1, weight=5)  # Code Detail View
        self.grid_rowconfigure(0, weight=1)

        # Topic Selector Left Pane
        self.left_pane = GlassCard(self, hover_effect=False)
        self.left_pane.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="nsew")
        
        lbl_title = ctk.CTkLabel(self.left_pane, text="🐍 Python Basics", font=("Segoe UI", 16, "bold"), text_color="#00f0ff")
        lbl_title.pack(anchor="w", padx=20, pady=15)

        self.scroll_topics = ctk.CTkScrollableFrame(self.left_pane, fg_color="transparent")
        self.scroll_topics.pack(fill="both", expand=True, padx=5, pady=5)

        # Python Topic Meta
        self.topics = [
            ("hist", "1. History & Philosophy"),
            ("vars", "2. Variables & Data Types"),
            ("conds", "3. Control Flow: Conditions"),
            ("loops", "4. Iterations: Loops"),
            ("funcs", "5. Modularity: Functions"),
            ("mods", "6. Modules & Packages"),
            ("venvs", "7. Virtual Environments"),
            ("oops", "8. Object-Oriented Py")
        ]

        self.topic_contents = {
            "hist": {
                "title": "Python History & Philosophy",
                "desc": (
                    "Python was conceived in the late 1980s by Guido van Rossum at CWI in the Netherlands. "
                    "The language emphasizes code readability and simplicity, famously conceptualized in 'The Zen of Python' "
                    "(PEP 20).\n\n"
                    "Key aphorisms include:\n"
                    "• Beautiful is better than ugly.\n"
                    "• Explicit is better than implicit.\n"
                    "• Simple is better than complex.\n"
                    "In defensive security, Python is the industry-standard scripting language due to its rapid prototyping "
                    "capabilities and powerful networking packages."
                ),
                "code": (
                    "# The Zen of Python - Core philosophy\n"
                    "import this\n\n"
                    "# Python code emphasizes clean whitespace indentation over curly braces.\n"
                    "def execute_zen():\n"
                    "    print('Simplicity is key to bug-free code.')\n\n"
                    "execute_zen()"
                )
            },
            "vars": {
                "title": "Variables & Data Types",
                "desc": (
                    "Python is dynamically typed: variables adjust type based on assigned values. Core types include:\n\n"
                    "• Integers / Floats: Numbers (e.g., port values, timers).\n"
                    "• Strings: Text characters (IP targets, domain paths).\n"
                    "• Lists: Ordered collections (ports scanned, list of targets).\n"
                    "• Dictionaries: Key-value maps (host header structures, configuration fields)."
                ),
                "code": (
                    "# Define target system data structures\n"
                    "target_ip = '10.0.0.45'  # String type\n"
                    "port_list = [22, 80, 443]  # List type\n"
                    "host_meta = {              # Dictionary type\n"
                    "    'os': 'Linux Kernel 5.4',\n"
                    "    'secured': True,\n"
                    "    'threat_index': 2\n"
                    "}\n\n"
                    "print(f'Checking {target_ip} on port list: {port_list}')"
                )
            },
            "conds": {
                "title": "Control Flow: Conditions",
                "desc": (
                    "Conditionals check truth requirements to control execution flow. Structured using 'if', "
                    "'elif', and 'else'. Indentation defines scope blocks."
                ),
                "code": (
                    "# Network port security assessment\n"
                    "port = 21\n\n"
                    "if port == 80:\n"
                    "    print('Standard HTTP Web Service detected (Unencrypted)')\n"
                    "elif port == 21:\n"
                    "    print('FTP service active. Risk: Plaintext passwords')\n"
                    "elif port == 22 or port == 443:\n"
                    "    print('Secure service channel detected (SSH/HTTPS)')\n"
                    "else:\n"
                    "    print('Unknown port interface. Investigation advised.')"
                )
            },
            "loops": {
                "title": "Iterations: Loops",
                "desc": (
                    "Loops repeat blocks of code. Python supports two main loop structures:\n\n"
                    "• 'for' loop: Iterates over lists, ranges, or generator pipelines.\n"
                    "• 'while' loop: Executes as long as a logical requirement remains true."
                ),
                "code": (
                    "# Basic subnet scanner simulator\n"
                    "ports = [21, 22, 80, 443, 8080]\n\n"
                    "print('Initiating port check...')\n"
                    "for p in ports:\n"
                    "    # Simulating connection request\n"
                    "    if p == 22 or p == 443:\n"
                    "        print(f'Port {p:04d}: [OPEN] - Secured Service')\n"
                    "    else:\n"
                    "        print(f'Port {p:04d}: [CLOSED]')\n\n"
                    "print('Check sequence finished.')"
                )
            },
            "funcs": {
                "title": "Modularity: Functions",
                "desc": (
                    "Functions encapsulate logic into reusable blocks, helping code stay DRY (Don't Repeat Yourself). "
                    "Declared using 'def' keyword with arguments and optional returned results."
                ),
                "code": (
                    "# Reusable cryptographic hash check utility\n"
                    "import hashlib\n\n"
                    "def compute_hash(data_str, algorithm='sha256'):\n"
                    "    data_bytes = data_str.encode('utf-8')\n"
                    "    if algorithm == 'sha256':\n"
                    "        return hashlib.sha256(data_bytes).hexdigest()\n"
                    "    elif algorithm == 'md5':\n"
                    "        return hashlib.md5(data_bytes).hexdigest()\n"
                    "    return None\n\n"
                    "key_hash = compute_hash('admin123', 'sha256')\n"
                    "print(f'SHA-256 Signature: {key_hash}')"
                )
            },
            "mods": {
                "title": "Modules & Packages",
                "desc": (
                    "Modules are single `.py` files containing code. Packages are directories of modules. "
                    "Import code using standard 'import' paths, or leverage external packages using the 'pip' package manager."
                ),
                "code": (
                    "# Import standard libraries to resolve local networks\n"
                    "import socket\n"
                    "import sys\n\n"
                    "try:\n"
                    "    resolved_ip = socket.gethostbyname('google.com')\n"
                    "    print(f'Google resolution: {resolved_ip}')\n"
                    "except socket.gaierror as e:\n"
                    "    print(f'DNS Failure: {e}')"
                )
            },
            "venvs": {
                "title": "Virtual Environments",
                "desc": (
                    "Virtual environments isolate python package installs for individual projects. "
                    "This prevents dependency version clashes and keeps standard global system setups pristine."
                ),
                "code": (
                    "# Creation steps in terminal command line\n"
                    "# 1. Create isolation container:\n"
                    "#    python -m venv my_sec_env\n"
                    "#\n"
                    "# 2. Activate scripting layer:\n"
                    "#    Windows:  .\\my_sec_env\\Scripts\\activate\n"
                    "#    Unix:     source my_sec_env/bin/activate\n"
                    "#\n"
                    "# 3. Run localized package installers:\n"
                    "#    pip install requests cryptography"
                )
            },
            "oops": {
                "title": "Object-Oriented Python",
                "desc": (
                    "OOP models system attributes and functions using Classes and Objects. "
                    "Classes establish structures. Objects instantiate them into memory. "
                    "Features inheritance, encapsulation, and polymorphism."
                ),
                "code": (
                    "# OOP framework representing target systems\n"
                    "class TargetAsset:\n"
                    "    def __init__(self, hostname, ip_address):\n"
                    "        self.hostname = hostname\n"
                    "        self.ip_address = ip_address\n"
                    "        self.open_ports = []\n\n"
                    "    def register_port(self, port):\n"
                    "        self.open_ports.append(port)\n\n"
                    "class SecureAsset(TargetAsset):\n"
                    "    # Inherits from TargetAsset\n"
                    "    def verify_sec_level(self):\n"
                    "        return 'SSL Shield Engaged'\n\n"
                    "host = SecureAsset('DB_PROD', '10.0.2.15')\n"
                    "host.register_port(443)\n"
                    "print(f'{host.hostname} status: {host.verify_sec_level()}')"
                )
            }
        }

        self.topic_buttons = []
        self.draw_topic_list()

        # Right pane detail view
        self.right_pane = GlassCard(self, hover_effect=False)
        self.right_pane.grid(row=0, column=1, padx=(10, 15), pady=15, sticky="nsew")
        self.right_pane.grid_columnconfigure(0, weight=1)
        self.right_pane.grid_rowconfigure(2, weight=1)  # syntax editor expands

        self.lbl_det_title = ctk.CTkLabel(self.right_pane, text="Details Title", font=("Segoe UI", 20, "bold"), text_color="#00f0ff")
        self.lbl_det_title.grid(row=0, column=0, padx=25, pady=(20, 5), sticky="w")

        self.lbl_det_desc = ctk.CTkLabel(
            self.right_pane, 
            text="Detailed descriptions will load here when selecting a Python topic.", 
            font=("Segoe UI", 13), 
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=700
        )
        self.lbl_det_desc.grid(row=1, column=0, padx=25, pady=5, sticky="w")

        # Syntax editor mockup
        self.syntax_frame = ctk.CTkFrame(self.right_pane, fg_color="#0d1321", border_color=BORDER_COLOR, border_width=1)
        self.syntax_frame.grid(row=2, column=0, padx=25, pady=(15, 20), sticky="nsew")
        
        # Header bar for code window
        code_header = ctk.CTkFrame(self.syntax_frame, fg_color="#131c30", height=30)
        code_header.pack(fill="x")
        code_header.pack_propagate(False)
        
        ctk.CTkLabel(code_header, text="● ● ●", text_color="#64748b", font=("Consolas", 12)).pack(side="left", padx=10)
        ctk.CTkLabel(code_header, text="main.py - Virtual Python Interpreter", font=("Consolas", 11), text_color=TEXT_SECONDARY).pack(side="left")

        self.code_box = SyntaxTextBox(self.syntax_frame, height=200)
        self.code_box.pack(fill="both", expand=True, padx=5, pady=5)

        # Default select first topic
        self.select_topic("hist")

    def draw_topic_list(self):
        for idx, (tid, label) in enumerate(self.topics):
            btn = ctk.CTkButton(
                self.scroll_topics, 
                text=label, 
                anchor="w",
                fg_color="transparent",
                hover_color=BORDER_COLOR,
                text_color=TEXT_PRIMARY,
                font=("Segoe UI", 12),
                command=lambda t=tid: self.select_topic(t)
            )
            btn.pack(fill="x", pady=2, padx=5)
            self.topic_buttons.append((tid, btn))

    def select_topic(self, topic_id):
        # Update button highlights
        accent = self.app.accent_color
        for tid, btn in self.topic_buttons:
            if tid == topic_id:
                btn.configure(fg_color="#1c2b42", text_color=accent, font=("Segoe UI", 12, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY, font=("Segoe UI", 12))

        # Load content
        data = self.topic_contents.get(topic_id)
        if data:
            self.lbl_det_title.configure(text=data["title"])
            self.lbl_det_desc.configure(text=data["desc"])
            self.code_box.set_code(data["code"])


class ToolsPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Grid inside scroll frame
        self.scroll_frame.grid_columnconfigure((0, 1), weight=1)

        self.tools = [
            {
                "name": "Python 3",
                "badge": "Language",
                "desc": "The primary language of cybersecurity engineering. Crucial for creating network listeners, scanning servers, parsing system logs, and constructing automated scripting scripts.",
                "usecase": "Exploit scripting, raw TCP listener setups, utility tools."
            },
            {
                "name": "VS Code",
                "badge": "IDE",
                "desc": "A lightweight but powerful source code editor. Features native debugging terminals, Git controls, and standard syntax highlighting extensions for defensive python.",
                "usecase": "Writing and managing secure Python scripts."
            },
            {
                "name": "Git",
                "badge": "Version Control",
                "desc": "An open-source distributed version control system. Used globally to host security scripts, pull repository tools, and trace changes across project iterations.",
                "usecase": "Collaboration, open-source script acquisition, versioning."
            },
            {
                "name": "Wireshark",
                "badge": "Packet Sniffer",
                "desc": "A widely used network protocol analyzer. Captures and inspects traffic flowing over network cards in real-time, displaying packet header breakdowns.",
                "usecase": "Threat detection, analyzing cleartext traffic, protocol validation."
            },
            {
                "name": "Nmap",
                "badge": "Network Scanner",
                "desc": "A tool used for network discovery and security auditing. Resolves active hosts on a network, enumerates running services, and identifies host operating systems.",
                "usecase": "Port scanning, service audits, OS detection."
            },
            {
                "name": "Burp Suite",
                "badge": "Web Proxy",
                "desc": "An integrated platform for testing web application security. Acts as an interception proxy, allowing users to inspect and tamper with raw HTTP request streams.",
                "usecase": "Web application penetration testing, API vulnerability checking."
            }
        ]

        self.draw_tool_cards()

    def draw_tool_cards(self):
        for idx, tool in enumerate(self.tools):
            row = idx // 2
            col = idx % 2

            card = GlassCard(self.scroll_frame, hover_effect=True)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Badge & Title
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(15, 5))
            
            lbl_title = ctk.CTkLabel(header, text=tool["name"], font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY)
            lbl_title.pack(side="left")
            
            lbl_badge = ctk.CTkLabel(
                header, 
                text=tool["badge"], 
                font=("Consolas", 10, "bold"), 
                text_color="#00f0ff", 
                fg_color="#002a3a", 
                corner_radius=6,
                padx=8,
                pady=2
            )
            lbl_badge.pack(side="right")

            # Description
            lbl_desc = ctk.CTkLabel(
                card, 
                text=tool["desc"], 
                font=("Segoe UI", 12), 
                text_color=TEXT_SECONDARY, 
                justify="left", 
                wraplength=450
            )
            lbl_desc.pack(anchor="w", padx=20, pady=5)

            # Usecase
            lbl_use = ctk.CTkLabel(
                card, 
                text=f"🔑 Primary Use Case:\n{tool['usecase']}", 
                font=("Segoe UI", 11, "bold"), 
                text_color="#39ff14", 
                justify="left"
            )
            lbl_use.pack(anchor="w", padx=20, pady=(5, 15))


class LibrariesPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.scroll_frame.grid_columnconfigure((0, 1), weight=1)

        self.libraries = [
            {
                "name": "hashlib",
                "desc": "Built-in cryptographic hash generation library. Used to calculate SHA256, MD5, and SHA512 signatures.",
                "example": "import hashlib\nsig = hashlib.sha256(b'payload').hexdigest()"
            },
            {
                "name": "socket",
                "desc": "Low-level networking interface module. Vital for opening client connections or binding servers.",
                "example": "import socket\ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)"
            },
            {
                "name": "requests",
                "desc": "Elegant HTTP library to make network calls to web APIs and applications without low-level socket handling.",
                "example": "import requests\nresponse = requests.get('https://api.github.com')"
            },
            {
                "name": "psutil",
                "desc": "Cross-platform process and system monitoring tool. Retrieves CPU, Memory, Disk, and Network stats.",
                "example": "import psutil\ncpu_load = psutil.cpu_percent(interval=1.0)"
            },
            {
                "name": "cryptography",
                "desc": "High-standard cryptographic recipe provider. Supports symmetric encryption (AES, Fernet) and asymmetric keying.",
                "example": "from cryptography.fernet import Fernet\nkey = Fernet.generate_key()"
            },
            {
                "name": "customtkinter",
                "desc": "High-fidelity, responsive GUI element provider wrapped around native Tkinter blocks.",
                "example": "import customtkinter as ctk\nctk.set_appearance_mode('dark')"
            },
            {
                "name": "tkinter",
                "desc": "Standard built-in graphic toolkit of the Python library system.",
                "example": "import tkinter as tk\nroot = tk.Tk()"
            },
            {
                "name": "threading",
                "desc": "Concurrent thread manager. Used to run operations in the background keeping the main UI responsive.",
                "example": "import threading\nt = threading.Thread(target=my_func)\nt.start()"
            },
            {
                "name": "sqlite3",
                "desc": "Serverless, file-backed database system embedded directly in standard Python platforms.",
                "example": "import sqlite3\nconn = sqlite3.connect('audit.db')"
            },
            {
                "name": "os",
                "desc": "Operating system interaction API. Essential for environment parameters and system calls.",
                "example": "import os\ncurrent_user = os.getlogin()"
            },
            {
                "name": "pathlib",
                "desc": "Object-oriented wrapper resolving filepath pointers safely across Windows/Linux file paths.",
                "example": "from pathlib import Path\np = Path('.').resolve()"
            }
        ]

        self.draw_library_cards()

    def draw_library_cards(self):
        for idx, lib in enumerate(self.libraries):
            row = idx // 2
            col = idx % 2

            card = GlassCard(self.scroll_frame, hover_effect=True)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Lib Title & Copy button
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=20, pady=(15, 5))
            
            lbl_title = ctk.CTkLabel(header, text=lib["name"], font=("Segoe UI", 16, "bold"), text_color=TEXT_PRIMARY)
            lbl_title.pack(side="left")

            btn_copy = ctk.CTkButton(
                header, 
                text="📋 Copy", 
                width=60, 
                height=22, 
                font=("Segoe UI", 10),
                command=lambda code=lib["example"]: self.copy_snippet(code)
            )
            btn_copy._is_accent_btn = True
            btn_copy.pack(side="right")

            # Description
            lbl_desc = ctk.CTkLabel(
                card, 
                text=lib["desc"], 
                font=("Segoe UI", 12), 
                text_color=TEXT_SECONDARY, 
                justify="left", 
                wraplength=450
            )
            lbl_desc.pack(anchor="w", padx=20, pady=5)

            # Code Codebox Container
            code_container = ctk.CTkFrame(card, fg_color="#0d1321", border_color=BORDER_COLOR, border_width=1)
            code_container.pack(fill="x", padx=20, pady=(5, 15))
            
            lbl_code = ctk.CTkLabel(
                code_container, 
                text=lib["example"], 
                font=("Consolas", 11), 
                text_color="#39ff14", 
                justify="left",
                padx=10,
                pady=8
            )
            lbl_code.pack(anchor="w")

    def copy_snippet(self, code):
        self.clipboard_clear()
        self.clipboard_append(code)
        messagebox.showinfo("Clipboard", "Code template copied to clipboard!")


class MiniLabsPage(PageFrame):
    """Contains 5 interactive sandboxed educational labs: Password Checker, Hashing, Password Generator, B64, SysInfo."""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tabview for labs
        self.tabview = ctk.CTkTabview(self, segmented_button_selected_color="#00f0ff", segmented_button_selected_hover_color="#00bcd4")
        self.tabview.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Create tab containers
        self.tabview.add("Password Checker")
        self.tabview.add("Hash Generator")
        self.tabview.add("Password Generator")
        self.tabview.add("Base64 Coder")
        self.tabview.add("System Info")

        self.setup_password_checker_tab()
        self.setup_hash_tab()
        self.setup_generator_tab()
        self.setup_b64_tab()
        self.setup_sysinfo_tab()

    # -------------------------------------------------------------
    # Lab 1: Password Strength Checker
    # -------------------------------------------------------------
    def setup_password_checker_tab(self):
        tab = self.tabview.tab("Password Checker")
        tab.grid_columnconfigure(0, weight=1)

        card = GlassCard(tab, hover_effect=False)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(card, text="🛡 Password Strength & Entropy Evaluator", font=("Segoe UI", 16, "bold"), text_color="#00f0ff").pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(card, text="Type a test password below to calculate character complexity and Shannon Entropy metrics.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(anchor="w", padx=25, pady=(0, 15))

        self.pass_entry = ctk.CTkEntry(card, placeholder_text="Enter password here...", show="*", width=350, font=("Consolas", 13))
        self.pass_entry.pack(anchor="w", padx=25, pady=10)
        self.pass_entry.bind("<KeyRelease>", self.evaluate_password)

        # Visibility Toggle
        self.chk_reveal = ctk.CTkCheckBox(card, text="Show characters", font=("Segoe UI", 11), command=self.toggle_pass_reveal)
        self.chk_reveal.pack(anchor="w", padx=25, pady=5)

        # Strength indicators
        self.lbl_strength = ctk.CTkLabel(card, text="Strength: Empty", font=("Segoe UI", 14, "bold"), text_color=TEXT_SECONDARY)
        self.lbl_strength.pack(anchor="w", padx=25, pady=(15, 5))

        self.strength_bar = ctk.CTkProgressBar(card, width=350, height=8, fg_color="#1e293b")
        self.strength_bar.set(0)
        self.strength_bar.pack(anchor="w", padx=25, pady=5)

        # Conditions Checklist
        self.lbl_cond_len = ctk.CTkLabel(card, text="✗ At least 8 characters", text_color="#ff5555", font=("Segoe UI", 12))
        self.lbl_cond_len.pack(anchor="w", padx=30, pady=1)

        self.lbl_cond_upper = ctk.CTkLabel(card, text="✗ Contains uppercase letters", text_color="#ff5555", font=("Segoe UI", 12))
        self.lbl_cond_upper.pack(anchor="w", padx=30, pady=1)

        self.lbl_cond_lower = ctk.CTkLabel(card, text="✗ Contains lowercase letters", text_color="#ff5555", font=("Segoe UI", 12))
        self.lbl_cond_lower.pack(anchor="w", padx=30, pady=1)

        self.lbl_cond_num = ctk.CTkLabel(card, text="✗ Contains numbers", text_color="#ff5555", font=("Segoe UI", 12))
        self.lbl_cond_num.pack(anchor="w", padx=30, pady=1)

        self.lbl_cond_spec = ctk.CTkLabel(card, text="✗ Contains special characters", text_color="#ff5555", font=("Segoe UI", 12))
        self.lbl_cond_spec.pack(anchor="w", padx=30, pady=(1, 15))

        # Entropy metrics
        self.lbl_entropy = ctk.CTkLabel(card, text="Calculated Entropy: 0.0 bits", font=("Consolas", 12), text_color="#00f0ff")
        self.lbl_entropy.pack(anchor="w", padx=25, pady=5)

    def toggle_pass_reveal(self):
        if self.chk_reveal.get():
            self.pass_entry.configure(show="")
        else:
            self.pass_entry.configure(show="*")

    def evaluate_password(self, event=None):
        password = self.pass_entry.get()
        if not password:
            self.lbl_strength.configure(text="Strength: Empty", text_color=TEXT_SECONDARY)
            self.strength_bar.set(0)
            self.strength_bar.configure(progress_color="#1e293b")
            self.lbl_entropy.configure(text="Calculated Entropy: 0.0 bits")
            for lbl in [self.lbl_cond_len, self.lbl_cond_upper, self.lbl_cond_lower, self.lbl_cond_num, self.lbl_cond_spec]:
                lbl.configure(text=lbl.cget("text").replace("✓", "✗"), text_color="#ff5555")
            return

        # Check conditions
        has_len = len(password) >= 8
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_num = any(c.isdigit() for c in password)
        has_spec = any(c in string.punctuation for c in password)

        # Update checklist labels
        def update_lbl(lbl, cond):
            text = lbl.cget("text")
            clean_text = text.lstrip("✓ ").lstrip("✗ ")
            if cond:
                lbl.configure(text=f"✓ {clean_text}", text_color="#39ff14")
            else:
                lbl.configure(text=f"✗ {clean_text}", text_color="#ff5555")

        update_lbl(self.lbl_cond_len, has_len)
        update_lbl(self.lbl_cond_upper, has_upper)
        update_lbl(self.lbl_cond_lower, has_lower)
        update_lbl(self.lbl_cond_num, has_num)
        update_lbl(self.lbl_cond_spec, has_spec)

        # Score calculation (0-5)
        score = sum([has_len, has_upper, has_lower, has_num, has_spec])
        percent = score / 5.0
        self.strength_bar.set(percent)

        if score <= 1:
            self.lbl_strength.configure(text="Strength: Very Weak", text_color="#ff5555")
            self.strength_bar.configure(progress_color="#ff5555")
        elif score <= 3:
            self.lbl_strength.configure(text="Strength: Weak/Medium", text_color="#ffaa00")
            self.strength_bar.configure(progress_color="#ffaa00")
        elif score == 4:
            self.lbl_strength.configure(text="Strength: Strong", text_color="#00f0ff")
            self.strength_bar.configure(progress_color="#00f0ff")
        else:
            self.lbl_strength.configure(text="Strength: Excellent (Very Strong)", text_color="#39ff14")
            self.strength_bar.configure(progress_color="#39ff14")

        # Entropy computation: Shannon Entropy H = -sum(p_i * log2(p_i))
        import math
        char_counts = {}
        for c in password:
            char_counts[c] = char_counts.get(c, 0) + 1
        
        entropy = 0.0
        total_chars = len(password)
        for c, count in char_counts.items():
            prob = count / total_chars
            entropy -= prob * math.log2(prob)
        
        self.lbl_entropy.configure(text=f"Calculated Entropy: {entropy:.2f} bits (Ideal > 3.5 bits)")

    # -------------------------------------------------------------
    # Lab 2: Hash Generator & File Checksum
    # -------------------------------------------------------------
    def setup_hash_tab(self):
        tab = self.tabview.tab("Hash Generator")
        tab.grid_columnconfigure(0, weight=1)

        card = GlassCard(tab, hover_effect=False)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Live Text Hashing
        ctk.CTkLabel(card, text="🔒 Text Hashing Engine", font=("Segoe UI", 16, "bold"), text_color="#00f0ff").pack(anchor="w", padx=25, pady=(20, 5))
        
        self.hash_entry = ctk.CTkEntry(card, placeholder_text="Type text to hash...", width=450)
        self.hash_entry.pack(anchor="w", padx=25, pady=10)
        self.hash_entry.bind("<KeyRelease>", self.generate_live_hashes)

        # Output SHA-256
        sha_frame = ctk.CTkFrame(card, fg_color="transparent")
        sha_frame.pack(fill="x", padx=25, pady=3)
        ctk.CTkLabel(sha_frame, text="SHA-256 Signature:", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_sha = ctk.CTkEntry(sha_frame, width=450, font=("Consolas", 11), fg_color="#0d1321")
        self.lbl_sha.pack(side="left", padx=10)
        btn_copy_sha = ctk.CTkButton(sha_frame, text="Copy", width=60, command=lambda: self.copy_to_clip(self.lbl_sha.get()))
        btn_copy_sha._is_accent_btn = True
        btn_copy_sha.pack(side="left")

        # Output MD5
        md5_frame = ctk.CTkFrame(card, fg_color="transparent")
        md5_frame.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(md5_frame, text="MD5 Signature:   ", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_md5 = ctk.CTkEntry(md5_frame, width=450, font=("Consolas", 11), fg_color="#0d1321")
        self.lbl_md5.pack(side="left", padx=10)
        btn_copy_md5 = ctk.CTkButton(md5_frame, text="Copy", width=60, command=lambda: self.copy_to_clip(self.lbl_md5.get()))
        btn_copy_md5._is_accent_btn = True
        btn_copy_md5.pack(side="left")

        # Divider line
        ctk.CTkFrame(card, height=2, fg_color=BORDER_COLOR).pack(fill="x", padx=25, pady=15)

        # File Checksum tool
        ctk.CTkLabel(card, text="📁 File Integrity Checksum Utility", font=("Segoe UI", 16, "bold"), text_color="#39ff14").pack(anchor="w", padx=25, pady=(0, 5))
        
        file_actions = ctk.CTkFrame(card, fg_color="transparent")
        file_actions.pack(fill="x", padx=25, pady=5)

        btn_select_file = ctk.CTkButton(file_actions, text="Select File...", command=self.checksum_file_action)
        btn_select_file._is_accent_btn = True
        btn_select_file.pack(side="left")

        self.lbl_filepath = ctk.CTkLabel(file_actions, text="No file selected.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY)
        self.lbl_filepath.pack(side="left", padx=15)

        checksum_result = ctk.CTkFrame(card, fg_color="transparent")
        checksum_result.pack(fill="x", padx=25, pady=(5, 20))
        ctk.CTkLabel(checksum_result, text="File SHA-256:    ", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY).pack(side="left")
        self.lbl_file_sha = ctk.CTkEntry(checksum_result, width=450, font=("Consolas", 11), fg_color="#0d1321")
        self.lbl_file_sha.pack(side="left", padx=10)
        btn_copy_file_sha = ctk.CTkButton(checksum_result, text="Copy", width=60, command=lambda: self.copy_to_clip(self.lbl_file_sha.get()))
        btn_copy_file_sha._is_accent_btn = True
        btn_copy_file_sha.pack(side="left")

    def generate_live_hashes(self, event=None):
        text = self.hash_entry.get()
        if not text:
            self.lbl_sha.configure(state="normal")
            self.lbl_sha.delete(0, "end")
            self.lbl_sha.configure(state="readonly")
            
            self.lbl_md5.configure(state="normal")
            self.lbl_md5.delete(0, "end")
            self.lbl_md5.configure(state="readonly")
            return

        data_bytes = text.encode("utf-8")
        
        sha256 = hashlib.sha256(data_bytes).hexdigest()
        md5 = hashlib.md5(data_bytes).hexdigest()

        self.lbl_sha.configure(state="normal")
        self.lbl_sha.delete(0, "end")
        self.lbl_sha.insert(0, sha256)
        self.lbl_sha.configure(state="readonly")

        self.lbl_md5.configure(state="normal")
        self.lbl_md5.delete(0, "end")
        self.lbl_md5.insert(0, md5)
        self.lbl_md5.configure(state="readonly")

    def checksum_file_action(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return

        self.lbl_filepath.configure(text=os.path.basename(filepath))
        self.lbl_file_sha.configure(state="normal")
        self.lbl_file_sha.delete(0, "end")
        self.lbl_file_sha.insert(0, "Computing checksum...")
        self.lbl_file_sha.configure(state="readonly")

        # Compute checksum in background thread to avoid freezing UI
        def worker():
            try:
                sha256 = hashlib.sha256()
                with open(filepath, "rb") as f:
                    while chunk := f.read(8192):
                        sha256.update(chunk)
                hex_digest = sha256.hexdigest()
                self.app.after(0, lambda: self.update_file_checksum(hex_digest))
            except Exception as e:
                self.app.after(0, lambda err=str(e): self.update_file_checksum(f"Error: {err}"))

        threading.Thread(target=worker, daemon=True).start()

    def update_file_checksum(self, result_str):
        self.lbl_file_sha.configure(state="normal")
        self.lbl_file_sha.delete(0, "end")
        self.lbl_file_sha.insert(0, result_str)
        self.lbl_file_sha.configure(state="readonly")

    def copy_to_clip(self, val):
        if val:
            self.clipboard_clear()
            self.clipboard_append(val)
            messagebox.showinfo("Clipboard", "Hash copied to clipboard!")

    # -------------------------------------------------------------
    # Lab 3: Random Password Generator
    # -------------------------------------------------------------
    def setup_generator_tab(self):
        tab = self.tabview.tab("Password Generator")
        tab.grid_columnconfigure(0, weight=1)

        card = GlassCard(tab, hover_effect=False)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(card, text="🔑 High-Entropy Password Generator", font=("Segoe UI", 16, "bold"), text_color="#00f0ff").pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(card, text="Configure rules and length sliders to construct secure keys locally.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(anchor="w", padx=25, pady=(0, 15))

        # Length Slider
        slider_frame = ctk.CTkFrame(card, fg_color="transparent")
        slider_frame.pack(fill="x", padx=25, pady=5)
        
        self.lbl_len_text = ctk.CTkLabel(slider_frame, text="Password Length: 16", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY)
        self.lbl_len_text.pack(anchor="w")

        self.len_slider = ctk.CTkSlider(slider_frame, from_=8, to=32, number_of_steps=24, command=self.update_length_label)
        self.len_slider.set(16)
        self.len_slider.pack(anchor="w", pady=5)

        # Character switches
        self.chk_upper = ctk.CTkCheckBox(card, text="Include Uppercase Letters (A-Z)", font=("Segoe UI", 12))
        self.chk_upper.pack(anchor="w", padx=25, pady=3)
        self.chk_upper.select()

        self.chk_lower = ctk.CTkCheckBox(card, text="Include Lowercase Letters (a-z)", font=("Segoe UI", 12))
        self.chk_lower.pack(anchor="w", padx=25, pady=3)
        self.chk_lower.select()

        self.chk_num = ctk.CTkCheckBox(card, text="Include Numbers (0-9)", font=("Segoe UI", 12))
        self.chk_num.pack(anchor="w", padx=25, pady=3)
        self.chk_num.select()

        self.chk_spec = ctk.CTkCheckBox(card, text="Include Special Characters (!@#$...)", font=("Segoe UI", 12))
        self.chk_spec.pack(anchor="w", padx=25, pady=3)
        self.chk_spec.select()

        # Output entry
        output_frame = ctk.CTkFrame(card, fg_color="transparent")
        output_frame.pack(fill="x", padx=25, pady=15)

        self.pass_gen_entry = ctk.CTkEntry(output_frame, width=350, font=("Consolas", 13), fg_color="#0d1321")
        self.pass_gen_entry.pack(side="left")

        btn_generate = ctk.CTkButton(output_frame, text="Generate", width=90, command=self.generate_password_action)
        btn_generate._is_accent_btn = True
        btn_generate.pack(side="left", padx=10)

        btn_copy_gen = ctk.CTkButton(output_frame, text="Copy", width=60, command=lambda: self.copy_to_clip(self.pass_gen_entry.get()))
        btn_copy_gen._is_accent_btn = True
        btn_copy_gen.pack(side="left")

        # Initial pass generation
        self.generate_password_action()

    def update_length_label(self, val):
        self.lbl_len_text.configure(text=f"Password Length: {int(val)}")

    def generate_password_action(self):
        pw_len = int(self.len_slider.get())
        
        char_pools = []
        if self.chk_upper.get():
            char_pools.append(string.ascii_uppercase)
        if self.chk_lower.get():
            char_pools.append(string.ascii_lowercase)
        if self.chk_num.get():
            char_pools.append(string.digits)
        if self.chk_spec.get():
            char_pools.append(string.punctuation)

        if not char_pools:
            messagebox.showwarning("Warning", "Select at least one character type option!")
            return

        # Build password ensuring at least one character from each selected pool is used
        pw_chars = []
        for pool in char_pools:
            pw_chars.append(random.choice(pool))

        full_pool = "".join(char_pools)
        while len(pw_chars) < pw_len:
            pw_chars.append(random.choice(full_pool))

        random.shuffle(pw_chars)
        password = "".join(pw_chars)

        self.pass_gen_entry.configure(state="normal")
        self.pass_gen_entry.delete(0, "end")
        self.pass_gen_entry.insert(0, password)

    # -------------------------------------------------------------
    # Lab 4: Base64 Encoder/Decoder
    # -------------------------------------------------------------
    def setup_b64_tab(self):
        tab = self.tabview.tab("Base64 Coder")
        tab.grid_columnconfigure((0, 1), weight=1)
        tab.grid_rowconfigure(2, weight=1)

        card = GlassCard(tab, hover_effect=False)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(card, text="🔗 Base64 Encoder / Decoder Utility", font=("Segoe UI", 16, "bold"), text_color="#00f0ff").grid(row=0, column=0, columnspan=2, sticky="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(card, text="Convert text inputs to and from Base64 binary serialization schemas securely.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY).grid(row=1, column=0, columnspan=2, sticky="w", padx=25, pady=(0, 10))

        # Left: Plaintext Area
        lbl_plain = ctk.CTkLabel(card, text="Plain Text Input/Output:", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY)
        lbl_plain.grid(row=2, column=0, sticky="w", padx=25, pady=(5, 2))
        
        self.txt_plain = ctk.CTkTextbox(card, height=130, fg_color="#0d1321", font=("Consolas", 12))
        self.txt_plain.grid(row=3, column=0, padx=(25, 10), pady=(0, 15), sticky="nsew")

        # Right: Encoded Area
        lbl_b64 = ctk.CTkLabel(card, text="Base64 Encoded Text:", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY)
        lbl_b64.grid(row=2, column=1, sticky="w", padx=10, pady=(5, 2))

        self.txt_b64 = ctk.CTkTextbox(card, height=130, fg_color="#0d1321", font=("Consolas", 12))
        self.txt_b64.grid(row=3, column=1, padx=(10, 25), pady=(0, 15), sticky="nsew")

        # Central Control Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20))

        btn_encode = ctk.CTkButton(btn_frame, text="Encode Plaintext ➔", font=("Segoe UI", 12, "bold"), command=self.base64_encode_action)
        btn_encode._is_accent_btn = True
        btn_encode.pack(side="left", padx=10)

        btn_decode = ctk.CTkButton(btn_frame, text="◀ Decode Base64", font=("Segoe UI", 12, "bold"), command=self.base64_decode_action)
        btn_decode._is_accent_btn = True
        btn_decode.pack(side="left", padx=10)

    def base64_encode_action(self):
        plain_text = self.txt_plain.get("1.0", "end-1c")
        if not plain_text:
            return
        
        try:
            encoded_bytes = base64.b64encode(plain_text.encode("utf-8"))
            encoded_str = encoded_bytes.decode("utf-8")
            self.txt_b64.delete("1.0", "end")
            self.txt_b64.insert("1.0", encoded_str)
        except Exception as e:
            messagebox.showerror("Error", f"Failed encoding payload: {e}")

    def base64_decode_action(self):
        b64_text = self.txt_b64.get("1.0", "end-1c").strip()
        if not b64_text:
            return

        try:
            decoded_bytes = base64.b64decode(b64_text)
            decoded_str = decoded_bytes.decode("utf-8")
            self.txt_plain.delete("1.0", "end")
            self.txt_plain.insert("1.0", decoded_str)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid Base64 sequence: {e}")

    # -------------------------------------------------------------
    # Lab 5: System Information Viewer
    # -------------------------------------------------------------
    def setup_sysinfo_tab(self):
        tab = self.tabview.tab("System Info")
        tab.grid_columnconfigure(0, weight=1)

        card = GlassCard(tab, hover_effect=False)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(card, text="📊 Live System Diagnostic Monitor", font=("Segoe UI", 16, "bold"), text_color="#00f0ff").pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(card, text="Monitors process details and hardware levels locally via psutil queries.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(anchor="w", padx=25, pady=(0, 15))

        # Specs grid layout
        grid_frame = ctk.CTkFrame(card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=25, pady=5)
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        # OS Details
        self.lbl_sys_os = ctk.CTkLabel(grid_frame, text="OS Platform: Loading...", font=("Segoe UI", 13, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.lbl_sys_os.grid(row=0, column=0, pady=5, sticky="w")

        # CPU Usage
        self.lbl_sys_cpu = ctk.CTkLabel(grid_frame, text="CPU Usage: 0%", font=("Segoe UI", 13, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.lbl_sys_cpu.grid(row=0, column=1, pady=5, sticky="w")

        # RAM Usage
        self.lbl_sys_ram = ctk.CTkLabel(grid_frame, text="RAM Usage: 0 / 0 GB", font=("Segoe UI", 13, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.lbl_sys_ram.grid(row=1, column=0, pady=5, sticky="w")

        # Current system local time
        self.lbl_sys_time = ctk.CTkLabel(grid_frame, text="System Time: --:--:--", font=("Segoe UI", 13, "bold"), text_color=TEXT_PRIMARY, anchor="w")
        self.lbl_sys_time.grid(row=1, column=1, pady=5, sticky="w")

        # Network interface details
        self.lbl_sys_ip = ctk.CTkLabel(card, text="Local Host IP: resolving...", font=("Segoe UI", 13, "bold"), text_color="#39ff14", anchor="w")
        self.lbl_sys_ip.pack(anchor="w", padx=25, pady=(10, 20))

        # Trigger first diagnostic query
        self.update_system_diagnostics()

    def update_system_diagnostics(self):
        # Retrieve system metrics
        os_platform = sys.platform.upper()
        cpu_usage = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        ram_used_gb = ram.used / (1024 ** 3)
        ram_total_gb = ram.total / (1024 ** 3)
        local_time = time.strftime("%H:%M:%S")

        # Update displays
        self.lbl_sys_os.configure(text=f"💻 Platform System: {os_platform}")
        self.lbl_sys_cpu.configure(text=f"⚡ CPU Core Usage: {cpu_usage}%")
        self.lbl_sys_ram.configure(text=f"💾 Memory Load: {ram_used_gb:.2f} / {ram_total_gb:.2f} GB ({ram.percent}%)")
        self.lbl_sys_time.configure(text=f"🕒 Secure Time: {local_time}")

        # Resolve local IP address
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.lbl_sys_ip.configure(text=f"🌐 Internal Host Link: {hostname} ({local_ip})")
        except Exception:
            self.lbl_sys_ip.configure(text="🌐 Internal Host Link: Error resolving socket.")

        # Update loop once per second
        self.after(1000, self.update_system_diagnostics)


class QuizPage(PageFrame):
    """Integrates the 20 multiple-choice cybersecurity and Python queries."""
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.questions = QUIZ_QUESTIONS
        self.current_idx = 0
        self.user_answers = [-1] * len(self.questions)
        self.quiz_completed = False

        # Container Frame
        self.container = GlassCard(self, hover_effect=False)
        self.container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Active question layout components
        self.setup_question_view()

        # Score Summary view (hidden by default)
        self.setup_result_view()

        self.load_question(0)

    def setup_question_view(self):
        self.quiz_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.quiz_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Header Info
        header = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        header.pack(fill="x")
        
        self.lbl_progress = ctk.CTkLabel(header, text="Question 1 of 20", font=("Segoe UI", 16, "bold"), text_color="#00f0ff")
        self.lbl_progress.pack(side="left")

        # Numeric tracker e.g. 1/20
        self.quiz_prog_bar = ctk.CTkProgressBar(self.quiz_frame, height=6, fg_color="#1e293b")
        self.quiz_prog_bar._is_accent_progress = True
        self.quiz_prog_bar.pack(fill="x", pady=10)

        # Question label
        self.lbl_question = ctk.CTkLabel(
            self.quiz_frame, 
            text="Question content text loads here...", 
            font=("Segoe UI", 15, "bold"), 
            text_color=TEXT_PRIMARY,
            justify="left",
            wraplength=800
        )
        self.lbl_question.pack(anchor="w", pady=(15, 20))

        # Radio button answers options group
        self.radio_var = tk.IntVar(value=-1)
        self.option_radios = []
        
        for i in range(4):
            radio = ctk.CTkRadioButton(
                self.quiz_frame, 
                text=f"Option {i+1}", 
                variable=self.radio_var, 
                value=i,
                font=("Segoe UI", 12),
                text_color=TEXT_SECONDARY,
                hover_color="#00f0ff"
            )
            radio.pack(anchor="w", pady=8, padx=10)
            self.option_radios.append(radio)

        # Bottom navigation controls
        nav_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        nav_frame.pack(fill="x", pady=(25, 10))

        self.btn_prev = ctk.CTkButton(nav_frame, text="◀ Previous", font=("Segoe UI", 12, "bold"), command=self.prev_question)
        self.btn_prev._is_accent_btn = True
        self.btn_prev.pack(side="left")

        self.btn_next = ctk.CTkButton(nav_frame, text="Next ▶", font=("Segoe UI", 12, "bold"), command=self.next_question)
        self.btn_next._is_accent_btn = True
        self.btn_next.pack(side="right")

    def setup_result_view(self):
        self.result_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        
        # Circle Score visualization
        self.lbl_score_title = ctk.CTkLabel(self.result_frame, text="Audit Results", font=("Segoe UI", 24, "bold"), text_color="#39ff14")
        self.lbl_score_title.pack(pady=(20, 5))

        self.lbl_score_val = ctk.CTkLabel(self.result_frame, text="0 / 20", font=("Segoe UI", 48, "bold"), text_color="#00f0ff")
        self.lbl_score_val.pack(pady=10)

        self.lbl_score_desc = ctk.CTkLabel(
            self.result_frame, 
            text="Review and improve your cybersecurity profile.", 
            font=("Segoe UI", 13), 
            text_color=TEXT_SECONDARY
        )
        self.lbl_score_desc.pack(pady=5)

        # Scroll review answers box
        self.review_scroll = ctk.CTkScrollableFrame(self.result_frame, width=700, height=200, fg_color="#0d1321", border_color=BORDER_COLOR, border_width=1)
        self.review_scroll.pack(fill="both", expand=True, padx=25, pady=15)

        self.btn_restart = ctk.CTkButton(self.result_frame, text="Restart Quiz", font=("Segoe UI", 12, "bold"), command=self.restart_quiz)
        self.btn_restart._is_accent_btn = True
        self.btn_restart.pack(pady=(5, 20))

    def load_question(self, idx):
        self.current_idx = idx
        q_data = self.questions[idx]

        # Update labels
        self.lbl_progress.configure(text=f"Audit Query {idx + 1} of {len(self.questions)}")
        self.quiz_prog_bar.set((idx + 1) / len(self.questions))
        
        self.lbl_question.configure(text=q_data["question"])
        
        # Update Radio Options
        for i, text in enumerate(q_data["options"]):
            self.option_radios[i].configure(text=text)

        # Restore user saved radio choice
        saved_ans = self.user_answers[idx]
        self.radio_var.set(saved_ans)

        # Toggle button text if reaching end
        self.btn_prev.configure(state="disabled" if idx == 0 else "normal")
        if idx == len(self.questions) - 1:
            self.btn_next.configure(text="Submit Audit")
        else:
            self.btn_next.configure(text="Next ▶")

    def save_current_answer(self):
        self.user_answers[self.current_idx] = self.radio_var.get()

    def next_question(self):
        self.save_current_answer()
        
        # Verify user has made a selection
        if self.user_answers[self.current_idx] == -1:
            messagebox.showwarning("Warning", "Select an option before continuing.")
            return

        if self.current_idx == len(self.questions) - 1:
            self.submit_quiz()
        else:
            self.load_question(self.current_idx + 1)

    def prev_question(self):
        self.save_current_answer()
        if self.current_idx > 0:
            self.load_question(self.current_idx - 1)

    def submit_quiz(self):
        self.save_current_answer()
        
        # Count Correct
        score = 0
        for idx, q_data in enumerate(self.questions):
            if self.user_answers[idx] == q_data["answer"]:
                score += 1

        self.quiz_completed = True
        self.state.update_quiz_score(score)
        self.app.apply_accent()

        # Display results panel
        self.quiz_frame.pack_forget()
        self.result_frame.pack(fill="both", expand=True, padx=30, pady=25)

        # Update score summary
        self.lbl_score_val.configure(text=f"{score} / {len(self.questions)}")
        
        percent = (score / len(self.questions)) * 100
        if percent >= 90:
            self.lbl_score_desc.configure(text="🎖 Certified Expert: Excellent penetration and defense knowledge!", text_color="#39ff14")
        elif percent >= 70:
            self.lbl_score_desc.configure(text="⚡ Qualified Agent: Competent scripting and network concept base.", text_color="#00f0ff")
        else:
            self.lbl_score_desc.configure(text="⏳ Trainee Level: Review Python basics and tools before retrying.", text_color="#ffcc00")

        # Render list for review
        # Clear previous scroll items
        for child in self.review_scroll.winfo_children():
            child.destroy()

        for idx, q_data in enumerate(self.questions):
            review_card = GlassCard(self.review_scroll, hover_effect=False)
            review_card.pack(fill="x", padx=10, pady=5)

            u_ans = self.user_answers[idx]
            is_correct = u_ans == q_data["answer"]
            
            lbl_title = ctk.CTkLabel(
                review_card, 
                text=f"Question {idx + 1}: {q_data['question']}", 
                font=("Segoe UI", 12, "bold"), 
                text_color=TEXT_PRIMARY,
                wraplength=600,
                justify="left"
            )
            lbl_title.pack(anchor="w", padx=15, pady=5)

            status_text = "✓ Correct" if is_correct else f"✗ Incorrect (Your choice: {q_data['options'][u_ans] if u_ans != -1 else 'None'})"
            status_color = "#39ff14" if is_correct else "#ff5555"
            lbl_status = ctk.CTkLabel(review_card, text=status_text, font=("Segoe UI", 11, "bold"), text_color=status_color)
            lbl_status.pack(anchor="w", padx=15, pady=2)

            lbl_expl = ctk.CTkLabel(
                review_card, 
                text=f"Explanation: {q_data['explanation']}", 
                font=("Segoe UI", 11), 
                text_color=TEXT_SECONDARY,
                wraplength=600,
                justify="left"
            )
            lbl_expl.pack(anchor="w", padx=15, pady=5)

    def restart_quiz(self):
        self.user_answers = [-1] * len(self.questions)
        self.current_idx = 0
        self.quiz_completed = False
        
        self.result_frame.pack_forget()
        self.quiz_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        self.load_question(0)


class RoadmapPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Roadmap Card
        card = GlassCard(self.scroll_frame, hover_effect=False)
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(card, text="🗺 Learning Roadmap: Zero to Hero", font=("Segoe UI", 18, "bold"), text_color="#00f0ff").pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(card, text="Follow the step-by-step season guides to level up from foundations to ethical hacking scripts.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(anchor="w", padx=25, pady=(0, 15))

        # Embed custom canvas timeline
        self.timeline = RoadmapTimeline(card, height=180)
        self.timeline.pack(fill="x", padx=25, pady=10)

        # Timeline description grids
        self.setup_season_details()

    def setup_season_details(self):
        seasons_info = [
            ("Season 1: Cyber Foundations & Python Basics", "Focus on basic cybersecurity definitions, understanding systems security structures, basic authentication scripts, loop parsing, variables, and list indexing patterns. Best for Level 1-2 students."),
            ("Season 2: Networking & Security Tool Operations", "Covers low-level socket bindings, executing port probes, analyzing packet headers in real-time, capturing network interfaces, and utilizing Nmap and Wireshark parameters. Best for Level 3-4 students."),
            ("Season 3: Defensive & Cryptographic Operations", "Develop cryptography tools, password checkers, checksum generators, encryption keys, and understand digital forensic disk clone protocols. Best for Level 5-6 students."),
            ("Season 4: Application Vulnerabilities & Penetration Auditing", "Covers interception proxy testing, testing API vulnerabilities, injecting sanitization shields, and building secure software architectures in corporate platforms. Best for Level 7+ students.")
        ]

        for title, desc in seasons_info:
            detail_card = GlassCard(self.scroll_frame, hover_effect=True)
            detail_card.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(detail_card, text=title, font=("Segoe UI", 14, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(12, 4))
            ctk.CTkLabel(detail_card, text=desc, font=("Segoe UI", 12), text_color=TEXT_SECONDARY, justify="left", wraplength=900).pack(anchor="w", padx=20, pady=(0, 12))

    def update_view(self):
        # Set current active season on timeline based on user level
        # Level 1-2 = Season 1, Level 3-4 = Season 2, Level 5-6 = Season 3, Level 7+ = Season 4
        season_num = min(4, 1 + (self.state.level - 1) // 2)
        self.timeline.set_season(season_num)


class ProgressPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=3)  # Left: Stats & Charts
        self.grid_columnconfigure(1, weight=2)  # Right: Achievements
        self.grid_rowconfigure(0, weight=1)

        # Left Column: Stats Cards & Canvas Performance Chart
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="nsew")
        left_container.grid_columnconfigure(0, weight=1)
        left_container.grid_rowconfigure(1, weight=1)

        # Dynamic profile card
        self.profile_card = GlassCard(left_container, hover_effect=False)
        self.profile_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.lbl_profile_lvl = ctk.CTkLabel(self.profile_card, text="LEVEL: 1", font=("Segoe UI", 18, "bold"), text_color="#39ff14")
        self.lbl_profile_lvl.pack(anchor="w", padx=25, pady=(15, 2))
        
        self.lbl_profile_xp = ctk.CTkLabel(self.profile_card, text="0 XP Gained", font=("Segoe UI", 12), text_color=TEXT_SECONDARY)
        self.lbl_profile_xp.pack(anchor="w", padx=25, pady=(0, 15))

        # Chart Container
        chart_card = GlassCard(left_container, hover_effect=False)
        chart_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(chart_card, text="📊 Skills Audit Graph", font=("Segoe UI", 16, "bold"), text_color="#00f0ff").grid(row=0, column=0, sticky="w", padx=25, pady=(15, 5))
        
        self.chart = PerformanceChart(chart_card)
        self.chart.grid(row=1, column=0, padx=25, pady=(5, 20), sticky="nsew")

        # Right Column: Achievements list
        self.right_card = GlassCard(self, hover_effect=False)
        self.right_card.grid(row=0, column=1, padx=(10, 15), pady=15, sticky="nsew")
        
        ctk.CTkLabel(self.right_card, text="🏆 Agent Achievements", font=("Segoe UI", 16, "bold"), text_color="#bd00ff").pack(anchor="w", padx=25, pady=15)

        self.scroll_achievements = ctk.CTkScrollableFrame(self.right_card, fg_color="transparent")
        self.scroll_achievements.pack(fill="both", expand=True, padx=5, pady=5)

        self.achievement_meta = [
            ("First Step", "Complete your first lesson.", "⚡ +50 XP"),
            ("Knowledge Seeker", "Complete at least 6 core lessons.", "⚡ +100 XP"),
            ("Master Thinker", "Complete all 11 cybersecurity lessons.", "⚡ +200 XP"),
            ("Competent Hacker", "Score 10+ points on the system quiz.", "⚡ +100 XP"),
            ("Certified Genius", "Score a perfect 20/20 on the system quiz.", "⚡ +300 XP"),
            ("XP Collector", "Accumulate more than 1000 total XP.", "⚡ +150 XP")
        ]

        self.ach_widgets = {}
        self.draw_achievements()

    def draw_achievements(self):
        for idx, (title, desc, reward) in enumerate(self.achievement_meta):
            card = GlassCard(self.scroll_frame_dummy if hasattr(self, 'scroll_frame_dummy') else self.scroll_achievements, hover_effect=True)
            card.pack(fill="x", padx=10, pady=5)

            # Left side content, right side badge
            lbl_title = ctk.CTkLabel(card, text=f"🔒 {title}", font=("Segoe UI", 14, "bold"), text_color=TEXT_SECONDARY)
            lbl_title.pack(anchor="w", padx=15, pady=(10, 2))

            lbl_desc = ctk.CTkLabel(card, text=desc, font=("Segoe UI", 11), text_color=TEXT_MUTED)
            lbl_desc.pack(anchor="w", padx=15, pady=1)

            lbl_reward = ctk.CTkLabel(card, text=reward, font=("Segoe UI", 11, "bold"), text_color=TEXT_MUTED)
            lbl_reward.pack(anchor="w", padx=15, pady=(1, 10))

            self.ach_widgets[title] = {
                "card": card,
                "lbl_title": lbl_title,
                "lbl_desc": lbl_desc,
                "lbl_reward": lbl_reward
            }

    def update_view(self):
        # Update Profile card text
        self.lbl_profile_lvl.configure(text=f"🎖 PROFILE LEVEL: {self.state.level}")
        self.lbl_profile_xp.configure(text=f"Total: {self.state.xp} XP (Season 1)")

        # Update Skill Chart Data
        # Calculate scores dynamically:
        # Python: proportion of python topics vs overall. Let's make it reflect lessons completed + quiz score
        lessons_ratio = len(self.state.completed_lessons) / 11.0 * 100
        quiz_ratio = self.state.quiz_high_score / 20.0 * 100
        
        python_skill = min(100, int(lessons_ratio * 0.6 + quiz_ratio * 0.4))
        netsec_skill = min(100, int((("netsec" in self.state.completed_lessons) * 50) + (quiz_ratio * 0.5)))
        crypto_skill = min(100, int((("cia" in self.state.completed_lessons) * 30) + (self.state.xp / 1000.0 * 70)))
        tools_skill = min(100, int((len(self.state.completed_lessons) / 11.0 * 50) + (quiz_ratio * 0.5)))

        chart_data = {
            "Python": python_skill,
            "NetSec": netsec_skill,
            "Crypto": crypto_skill,
            "Tools": tools_skill
        }
        self.chart.update_data(chart_data, color_accent=self.app.accent_color)

        # Update achievement visual highlights
        for title, widgets in self.ach_widgets.items():
            if title in self.state.achievements:
                # Highlight active
                widgets["lbl_title"].configure(text=f"🏆 {title}", text_color="#39ff14")
                widgets["lbl_desc"].configure(text_color=TEXT_PRIMARY)
                widgets["lbl_reward"].configure(text_color="#00f0ff")
                widgets["card"].configure(border_color="#39ff14")
            else:
                # Lock status
                widgets["lbl_title"].configure(text=f"🔒 {title}", text_color=TEXT_SECONDARY)
                widgets["lbl_desc"].configure(text_color=TEXT_MUTED)
                widgets["lbl_reward"].configure(text_color=TEXT_MUTED)
                widgets["card"].configure(border_color=BORDER_COLOR)


class SettingsPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = GlassCard(self, hover_effect=False)
        card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(card, text="⚙ Hub Configuration Panel", font=("Segoe UI", 18, "bold"), text_color="#bd00ff").pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(card, text="Adjust aesthetic variables and reload database parameters below.", font=("Segoe UI", 12), text_color=TEXT_SECONDARY).pack(anchor="w", padx=25, pady=(0, 15))

        # Setting 1: Accent Color
        ctk.CTkLabel(card, text="Select Theme Accent Color:", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=25, pady=5)
        
        self.accent_option = ctk.CTkOptionMenu(
            card, 
            values=["Cyber Blue", "Neon Green", "Cyber Purple"], 
            command=self.accent_change_action,
            fg_color="#131c30",
            button_color="#0d1321"
        )
        self.accent_option.set(self.state.settings.get("accent_color", "Cyber Blue"))
        self.accent_option.pack(anchor="w", padx=25, pady=(0, 15))

        # Setting 2: Font size adjustments
        ctk.CTkLabel(card, text="Font Display Scale:", font=("Segoe UI", 12, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w", padx=25, pady=5)
        
        self.font_option = ctk.CTkOptionMenu(
            card,
            values=["Standard", "Large"],
            command=self.font_change_action,
            fg_color="#131c30",
            button_color="#0d1321"
        )
        self.font_option.set(self.state.settings.get("font_size", "Standard"))
        self.font_option.pack(anchor="w", padx=25, pady=(0, 15))

        # Setting 3: Reset Progress
        ctk.CTkLabel(card, text="Danger Zone", font=("Segoe UI", 12, "bold"), text_color="#ff5555").pack(anchor="w", padx=25, pady=(20, 5))
        
        btn_reset = ctk.CTkButton(card, text="Reset All Progress", fg_color="#aa0000", hover_color="#ff2222", text_color=TEXT_PRIMARY, font=("Segoe UI", 12, "bold"), command=self.reset_progress_action)
        btn_reset.pack(anchor="w", padx=25, pady=(5, 20))

    def accent_change_action(self, val):
        self.state.settings["accent_color"] = val
        self.state.save()
        self.app.apply_accent()

    def font_change_action(self, val):
        self.state.settings["font_size"] = val
        self.state.save()
        self.app.apply_fonts()

    def reset_progress_action(self):
        confirm = messagebox.askyesno("Confirm Reset", "Are you sure you want to clear all lessons, XP, levels, and high scores? This actions cannot be undone.")
        if confirm:
            self.state.reset_progress()
            self.app.switch_page("Dashboard")
            messagebox.showinfo("Security Center", "Database progress initialized successfully.")


class AboutPage(PageFrame):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        card = GlassCard(self, hover_effect=False)
        card.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(card, text="ℹ Application Information", font=("Segoe UI", 18, "bold"), text_color="#00f0ff").pack(anchor="w", padx=25, pady=(20, 5))
        ctk.CTkLabel(card, text="Episode 1: Zero to Hero – Ethical Hacking with Python", font=("Segoe UI", 13), text_color=TEXT_SECONDARY).pack(anchor="w", padx=25, pady=(0, 15))

        # Specs cards
        ctk.CTkLabel(
            card, 
            text=(
                "Developer: FuzzuTech\n"
                "Version: 1.0\n"
                "Local Integrity Check: Passed\n"
                "Network Status: Offline Sandbox Mode\n"
                "Target Audience: Beginners to Intermediate cybersecurity analysts."
            ),
            font=("Consolas", 12),
            text_color="#39ff14",
            justify="left"
        ).pack(anchor="w", padx=25, pady=10)

        ctk.CTkLabel(
            card, 
            text=(
                "Legal & Educational Disclaimer:\n"
                "The interactive modules, password checkers, base64 operations, and checksum verifications "
                "integrated in this application are built for defensive educational demonstrations only. "
                "Any unauthorized attempts to target network nodes or systems without explicit prior "
                "written permission is illegal and prosecutable under computer protection laws. "
                "Ensure your actions strictly follow ethical rules of engagement."
            ),
            font=("Segoe UI", 12),
            text_color=TEXT_SECONDARY,
            justify="left",
            wraplength=800
        ).pack(anchor="w", padx=25, pady=(15, 20))

# -------------------------------------------------------------
# Animated Console router transitions overlay
# -------------------------------------------------------------
class ConsoleOverlay(ctk.CTkFrame):
    def __init__(self, parent, dest_name, callback):
        super().__init__(parent, fg_color=BG_DARK)
        self.callback = callback
        self.dest_name = dest_name
        
        self.text_widget = ctk.CTkTextbox(self, font=("Consolas", 12), text_color="#39ff14", fg_color="transparent")
        self.text_widget.pack(fill="both", expand=True, padx=30, pady=30)
        self.text_widget.configure(state="disabled")

        self.lines = [
            f"[SYSTEM] Dispatching route pipeline request...",
            f"[ROUTING] Target Frame: {dest_name.upper()}",
            f"[SECURITY] Verifying local integrity checksum: {hashlib.md5(dest_name.encode()).hexdigest()[:16]}",
            f"[SUCCESS] Environment clean. Displaying page interface..."
        ]
        self.current_line = 0
        self.write_line()

    def write_line(self):
        if self.current_line < len(self.lines):
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", self.lines[self.current_line] + "\n")
            self.text_widget.configure(state="disabled")
            self.current_line += 1
            # fast micro animation speed for premium feel
            self.after(60, self.write_line)
        else:
            self.after(50, self.callback)

# -------------------------------------------------------------
# Startup Loading Screen
# -------------------------------------------------------------
class LoadingScreen(ctk.CTkFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, fg_color=BG_DARK)
        self.callback = callback
        self.progress = 0.0

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Visual elements
        self.title_lbl = ctk.CTkLabel(self.container, text="CYBERSECURITY LEARNING HUB", font=("Segoe UI", 26, "bold"), text_color="#00f0ff")
        self.title_lbl.pack(pady=5)

        self.sub_lbl = ctk.CTkLabel(self.container, text="Episode 1: Zero to Hero – Ethical Hacking with Python", font=("Segoe UI", 14), text_color=TEXT_SECONDARY)
        self.sub_lbl.pack(pady=(0, 20))

        self.prog_bar = ctk.CTkProgressBar(self.container, width=320, height=8, progress_color="#39ff14", fg_color="#1e293b")
        self.prog_bar.set(0)
        self.prog_bar.pack(pady=10)

        self.status_lbl = ctk.CTkLabel(self.container, text="Initializing cryptographic engine...", font=("Consolas", 11), text_color="#39ff14")
        self.status_lbl.pack(pady=5)

        self.start_loading()

    def start_loading(self):
        self.progress += 0.04
        self.prog_bar.set(min(1.0, self.progress))

        messages = [
            "Initializing cryptographic engine...",
            "Loading local security modules...",
            "Validating system diagnostic sensors...",
            "Establishing sandboxed python interpreter...",
            "Pre-compiling interactive dashboard UI...",
            "Integrity assessment passed. Launching..."
        ]
        msg_idx = min(int(self.progress * len(messages)), len(messages) - 1)
        self.status_lbl.configure(text=messages[msg_idx])

        if self.progress < 1.0:
            self.after(60, self.start_loading)
        else:
            self.after(200, self.callback)

# -------------------------------------------------------------
# Main Application Window
# -------------------------------------------------------------
class CybersecurityLearningHub(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Minimum specifications
        self.title("Cybersecurity Learning Hub")
        self.geometry("1400x900")
        self.minsize(1400, 900)

        self.app_state = AppState()
        self.active_page = None

        # Grid configuration
        self.grid_columnconfigure(0, weight=0)  # Left Sidebar
        self.grid_columnconfigure(1, weight=1)  # Main Content View
        self.grid_rowconfigure(0, weight=1)

        # Loading screen overlay (covers entire frame)
        self.loading = LoadingScreen(self, self.on_loading_complete)
        self.loading.place(relx=0, rely=0, relwidth=1, relheight=1)

    @property
    def accent_color(self):
        c_name = self.app_state.settings.get("accent_color", "Cyber Blue")
        return ACCENT_COLORS.get(c_name, ACCENT_COLORS["Cyber Blue"])["accent"]

    @property
    def accent_hover(self):
        c_name = self.app_state.settings.get("accent_color", "Cyber Blue")
        return ACCENT_COLORS.get(c_name, ACCENT_COLORS["Cyber Blue"])["accent_hover"]

    @property
    def bg_glow(self):
        c_name = self.app_state.settings.get("accent_color", "Cyber Blue")
        return ACCENT_COLORS.get(c_name, ACCENT_COLORS["Cyber Blue"])["bg_glow"]

    def on_loading_complete(self):
        self.loading.place_forget()
        self.setup_ui()

    def setup_ui(self):
        # 1. Left Sidebar
        self.sidebar = ctk.CTkFrame(self, width=260, fg_color=SIDEBAR_BG, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.pack_propagate(False)

        # App title inside Sidebar
        title_lbl = ctk.CTkLabel(self.sidebar, text="🤖 CyberHub", font=("Segoe UI", 22, "bold"), text_color=TEXT_PRIMARY)
        title_lbl.pack(pady=(25, 5), padx=25, anchor="w")
        
        subtitle_lbl = ctk.CTkLabel(self.sidebar, text="Zero to Hero - v1.0", font=("Segoe UI", 11, "bold"), text_color="#00f0ff")
        subtitle_lbl._is_accent_label = True
        subtitle_lbl.pack(pady=(0, 25), padx=25, anchor="w")

        # Navigation buttons mapping
        self.nav_items = [
            ("Dashboard", "🏠 Dashboard"),
            ("Learn", "📖 Learn"),
            ("Python Basics", "🐍 Python Basics"),
            ("Tools", "🛠 Tools"),
            ("Libraries", "📚 Libraries"),
            ("Mini Labs", "🧪 Mini Labs"),
            ("Quiz", "📝 Quiz"),
            ("Roadmap", "🗺 Roadmap"),
            ("Progress", "📊 Progress"),
            ("Settings", "⚙ Settings"),
            ("About", "ℹ About")
        ]

        self.nav_buttons = {}
        for page_name, label in self.nav_items:
            btn = ctk.CTkButton(
                self.sidebar, 
                text=label, 
                anchor="w",
                height=40,
                fg_color="transparent",
                hover_color=BORDER_COLOR,
                text_color=TEXT_SECONDARY,
                font=("Segoe UI", 13, "bold"),
                command=lambda name=page_name: self.switch_page(name)
            )
            btn._is_sidebar_btn = True
            btn.pack(fill="x", padx=15, pady=3)
            self.nav_buttons[page_name] = btn

        # 2. Main Content View area
        self.content_container = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Initialize page views
        self.pages = {
            "Dashboard": DashboardPage(self.content_container, self),
            "Learn": LearnPage(self.content_container, self),
            "Python Basics": PythonPage(self.content_container, self),
            "Tools": ToolsPage(self.content_container, self),
            "Libraries": LibrariesPage(self.content_container, self),
            "Mini Labs": MiniLabsPage(self.content_container, self),
            "Quiz": QuizPage(self.content_container, self),
            "Roadmap": RoadmapPage(self.content_container, self),
            "Progress": ProgressPage(self.content_container, self),
            "Settings": SettingsPage(self.content_container, self),
            "About": AboutPage(self.content_container, self)
        }

        # Select initial page
        self.switch_page("Dashboard")
        self.apply_accent()
        self.apply_fonts()

    def switch_page(self, page_name):
        # Update sidebar button selection styling
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#17233b", text_color=self.accent_color)
                btn._is_active = True
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_SECONDARY)
                btn._is_active = False

        self.show_page_frame(page_name)

    def show_page_frame(self, page_name):
        # Clear any overlay or previous page
        for child in self.content_container.winfo_children():
            if child != self.pages[page_name]:
                child.grid_forget()

        # Mount new page
        target_page = self.pages[page_name]
        target_page.grid(row=0, column=0, sticky="nsew")
        target_page.update_view()
        self.active_page = page_name

    def apply_accent(self):
        # Update all active accents on registered widgets recursively
        self.apply_accent_to_widgets(self)

    def apply_accent_to_widgets(self, widget):
        # Custom button accents
        if isinstance(widget, ctk.CTkButton):
            if getattr(widget, "_is_accent_btn", False):
                widget.configure(fg_color=self.accent_color, hover_color=self.accent_hover)
            elif getattr(widget, "_is_sidebar_btn", False):
                if getattr(widget, "_is_active", False):
                    widget.configure(text_color=self.accent_color)
        
        # Labels and accents
        elif isinstance(widget, ctk.CTkLabel):
            if getattr(widget, "_is_accent_label", False):
                widget.configure(text_color=self.accent_color)

        # Custom progress bars
        elif isinstance(widget, ctk.CTkProgressBar):
            if getattr(widget, "_is_accent_progress", False):
                widget.configure(progress_color=self.accent_color)

        # Segmented buttons/Tabviews
        elif isinstance(widget, ctk.CTkTabview):
            widget.configure(segmented_button_selected_color=self.accent_color, segmented_button_selected_hover_color=self.accent_hover)

        # Canvas Charts
        elif isinstance(widget, PerformanceChart):
            widget.update_data(widget.data, color_accent=self.accent_color)

        # Recurse children
        for child in widget.winfo_children():
            self.apply_accent_to_widgets(child)

    def apply_fonts(self):
        font_sz = self.app_state.settings.get("font_size", "Standard")
        
        # Set scales
        body_size = 12 if font_sz == "Standard" else 14
        h3_size = 14 if font_sz == "Standard" else 16
        h2_size = 16 if font_sz == "Standard" else 18
        h1_size = 20 if font_sz == "Standard" else 22
        code_size = 12 if font_sz == "Standard" else 14

        self.update_widget_fonts(self, body_size, h3_size, h2_size, h1_size, code_size)

    def update_widget_fonts(self, widget, body_sz, h3_sz, h2_sz, h1_sz, code_sz):
        # Update CTk Label fonts depending on custom weights
        if isinstance(widget, ctk.CTkLabel):
            curr_font = widget.cget("font")
            if curr_font:
                if isinstance(curr_font, (tuple, list)):
                    fam = curr_font[0] if len(curr_font) > 0 else "Segoe UI"
                    sz = curr_font[1] if len(curr_font) > 1 else body_sz
                    weight = curr_font[2] if len(curr_font) > 2 else ""
                elif hasattr(curr_font, "cget"):
                    fam = curr_font.cget("family")
                    sz = curr_font.cget("size")
                    weight = curr_font.cget("weight")
                else:
                    fam = "Segoe UI"
                    sz = body_sz
                    weight = ""

                # Scale mapping based on layout heights
                if sz >= 24:
                    new_sz = h1_sz + 4
                elif sz >= 20:
                    new_sz = h1_sz
                elif sz >= 16:
                    new_sz = h2_sz
                elif sz >= 13:
                    new_sz = h3_sz
                else:
                    new_sz = body_sz

                if weight:
                    widget.configure(font=(fam, new_sz, weight))
                else:
                    widget.configure(font=(fam, new_sz))

        elif isinstance(widget, SyntaxTextBox):
            widget.configure(font=("Consolas", code_sz))

        for child in widget.winfo_children():
            self.update_widget_fonts(child, body_sz, h3_sz, h2_sz, h1_sz, code_sz)


# -------------------------------------------------------------
# Run execution pipeline
# -------------------------------------------------------------
if __name__ == "__main__":
    app = CybersecurityLearningHub()
    app.mainloop()
