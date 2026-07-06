import os
import re
import time
import uuid
import shutil
import hashlib
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk


# ============================================================
# APP CONFIGURATION
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_NAME = "USB THREAT SCANNER PRO"

BASE_DIR = Path(__file__).resolve().parent

QUARANTINE_DIR = BASE_DIR / "quarantine"
QUARANTINE_DIR.mkdir(exist_ok=True)


# ============================================================
# THREAT DETECTION RULES
# ============================================================

RISKY_EXTENSIONS = {
    ".exe": 25,
    ".scr": 45,
    ".bat": 35,
    ".cmd": 35,
    ".ps1": 40,
    ".vbs": 40,
    ".js": 25,
    ".jar": 20,
    ".com": 45,
    ".pif": 50,
    ".msi": 20,
}

DECOY_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
    ".mp3",
    ".mp4",
    ".zip",
}

SUSPICIOUS_NAMES = {
    "autorun.inf",
    "password.txt",
    "passwords.txt",
    "credentials.txt",
    "login.txt",
    "wallet.dat",
}

SUSPICIOUS_KEYWORDS = {
    "crack",
    "keygen",
    "payload",
    "stealer",
    "password",
    "credential",
    "autorun",
    "injector",
}


# ============================================================
# SECURITY FUNCTIONS
# ============================================================

def calculate_sha256(file_path):

    sha256 = hashlib.sha256()

    try:

        with open(file_path, "rb") as file:

            while True:

                chunk = file.read(1024 * 1024)

                if not chunk:
                    break

                sha256.update(chunk)

        return sha256.hexdigest()

    except (PermissionError, OSError):

        return "UNAVAILABLE"


def analyze_file(file_path):

    filename = os.path.basename(file_path)

    filename_lower = filename.lower()

    score = 0

    reasons = []

    extension = os.path.splitext(filename_lower)[1]

    # --------------------------------------------
    # RISKY FILE EXTENSION
    # --------------------------------------------

    if extension in RISKY_EXTENSIONS:

        score += RISKY_EXTENSIONS[extension]

        reasons.append(
            f"Risky file extension detected ({extension})"
        )

    # --------------------------------------------
    # DOUBLE EXTENSION DETECTION
    # --------------------------------------------

    parts = filename_lower.split(".")

    if len(parts) >= 3:

        previous_extension = "." + parts[-2]

        if (
            previous_extension in DECOY_EXTENSIONS
            and extension in RISKY_EXTENSIONS
        ):

            score += 55

            reasons.append(
                "Misleading double extension"
            )

    # --------------------------------------------
    # AUTORUN DETECTION
    # --------------------------------------------

    if filename_lower == "autorun.inf":

        score += 75

        reasons.append(
            "USB autorun configuration detected"
        )

    # --------------------------------------------
    # SUSPICIOUS FILE NAME
    # --------------------------------------------

    if filename_lower in SUSPICIOUS_NAMES:

        score += 25

        reasons.append(
            "Sensitive or suspicious filename"
        )

    # --------------------------------------------
    # SUSPICIOUS KEYWORDS
    # --------------------------------------------

    for keyword in SUSPICIOUS_KEYWORDS:

        if keyword in filename_lower:

            score += 10

            reasons.append(
                f"Suspicious keyword: {keyword}"
            )

            break

    # --------------------------------------------
    # HIDDEN-STYLE FILE
    # --------------------------------------------

    if filename.startswith("."):

        score += 10

        reasons.append(
            "Hidden-style filename"
        )

    return {

        "path": file_path,

        "name": filename,

        "score": min(score, 100),

        "reasons": reasons,

    }


def get_files(root_path):

    files = []

    for root, directories, filenames in os.walk(root_path):

        for filename in filenames:

            files.append(

                os.path.join(
                    root,
                    filename
                )

            )

    return files


def quarantine_file(file_path):

    if not os.path.isfile(file_path):

        return False, "File does not exist."

    quarantine_name = (

        str(uuid.uuid4())

        + "_"

        + os.path.basename(file_path)

        + ".quarantine"

    )

    destination = QUARANTINE_DIR / quarantine_name

    try:

        shutil.move(
            file_path,
            destination
        )

        return True, str(destination)

    except (PermissionError, OSError) as error:

        return False, str(error)


# ============================================================
# MAIN APPLICATION
# ============================================================

class USBThreatScanner(ctk.CTk):

    def __init__(self):

        super().__init__()

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.title(APP_NAME)

        self.geometry("1280x760")

        self.minsize(1100, 680)

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.selected_path = None

        self.threats = []

        self.is_scanning = False

        # ----------------------------------------------------
        # BUILD INTERFACE
        # ----------------------------------------------------

        self.build_ui()


    # ========================================================
    # USER INTERFACE
    # ========================================================

    def build_ui(self):

        # ====================================================
        # SIDEBAR
        # ====================================================

        sidebar = ctk.CTkFrame(

            self,

            width=235,

            corner_radius=0,

            fg_color="#08111f"

        )

        sidebar.pack(

            side="left",

            fill="y"

        )

        sidebar.pack_propagate(False)

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        ctk.CTkLabel(

            sidebar,

            text="USB\nTHREAT\nSCANNER",

            justify="left",

            font=ctk.CTkFont(

                size=27,

                weight="bold"

            )

        ).pack(

            padx=25,

            pady=(35, 10),

            anchor="w"

        )

        ctk.CTkLabel(

            sidebar,

            text="SECURITY COMMAND CENTER",

            text_color="#64748b",

            font=ctk.CTkFont(

                size=10,

                weight="bold"

            )

        ).pack(

            padx=25,

            anchor="w"

        )

        # ----------------------------------------------------
        # SYSTEM STATUS
        # ----------------------------------------------------

        self.system_status = ctk.CTkLabel(

            sidebar,

            text="● SYSTEM READY",

            text_color="#22c55e",

            font=ctk.CTkFont(

                size=13,

                weight="bold"

            )

        )

        self.system_status.pack(

            padx=25,

            pady=(45, 20),

            anchor="w"

        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        self.select_button = ctk.CTkButton(

            sidebar,

            text="SELECT USB / FOLDER",

            height=46,

            corner_radius=8,

            command=self.select_drive

        )

        self.select_button.pack(

            padx=20,

            pady=8,

            fill="x"

        )

        self.scan_button = ctk.CTkButton(

            sidebar,

            text="START SECURITY SCAN",

            height=46,

            corner_radius=8,

            command=self.start_scan

        )

        self.scan_button.pack(

            padx=20,

            pady=8,

            fill="x"

        )

        self.demo_button = ctk.CTkButton(

            sidebar,

            text="▶ VIRAL DEMO MODE",

            height=46,

            corner_radius=8,

            fg_color="#7c3aed",

            hover_color="#6d28d9",

            command=self.start_demo

        )

        self.demo_button.pack(

            padx=20,

            pady=8,

            fill="x"

        )

        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------

        ctk.CTkLabel(

            sidebar,

            text="FUZ­ZUTECH SECURITY LAB\nHEURISTIC ENGINE v1.0",

            justify="left",

            text_color="#475569",

            font=ctk.CTkFont(size=10)

        ).pack(

            side="bottom",

            padx=25,

            pady=25,

            anchor="w"

        )

        # ====================================================
        # MAIN CONTAINER
        # ====================================================

        main = ctk.CTkFrame(

            self,

            fg_color="transparent"

        )

        main.pack(

            side="left",

            fill="both",

            expand=True,

            padx=25,

            pady=22

        )

        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(

            main,

            fg_color="transparent"

        )

        header.pack(fill="x")

        ctk.CTkLabel(

            header,

            text="USB SECURITY COMMAND CENTER",

            font=ctk.CTkFont(

                size=28,

                weight="bold"

            )

        ).pack(side="left")

        self.device_label = ctk.CTkLabel(

            header,

            text="NO DEVICE SELECTED",

            text_color="#64748b",

            font=ctk.CTkFont(

                size=12,

                weight="bold"

            )

        )

        self.device_label.pack(side="right")

        # ====================================================
        # STAT CARDS
        # ====================================================

        cards = ctk.CTkFrame(

            main,

            fg_color="transparent"

        )

        cards.pack(

            fill="x",

            pady=(25, 18)

        )

        self.files_value = self.create_card(

            cards,

            "FILES CHECKED",

            "0"

        )

        self.threat_value = self.create_card(

            cards,

            "THREATS FOUND",

            "0"

        )

        self.risk_value = self.create_card(

            cards,

            "MAX RISK SCORE",

            "0%"

        )

        # ====================================================
        # SCAN STATUS PANEL
        # ====================================================

        scan_panel = ctk.CTkFrame(main)

        scan_panel.pack(

            fill="x",

            pady=(0, 18)

        )

        top_status = ctk.CTkFrame(

            scan_panel,

            fg_color="transparent"

        )

        top_status.pack(

            fill="x",

            padx=18,

            pady=(14, 7)

        )

        self.scan_status = ctk.CTkLabel(

            top_status,

            text="WAITING FOR SECURITY SCAN",

            font=ctk.CTkFont(

                size=14,

                weight="bold"

            )

        )

        self.scan_status.pack(side="left")

        self.progress_value = ctk.CTkLabel(

            top_status,

            text="0%",

            text_color="#38bdf8",

            font=ctk.CTkFont(

                size=13,

                weight="bold"

            )

        )

        self.progress_value.pack(side="right")

        self.progress = ctk.CTkProgressBar(

            scan_panel,

            height=13

        )

        self.progress.pack(

            fill="x",

            padx=18,

            pady=(0, 15)

        )

        self.progress.set(0)

        # ====================================================
        # CONTENT
        # ====================================================

        content = ctk.CTkFrame(

            main,

            fg_color="transparent"

        )

        content.pack(

            fill="both",

            expand=True

        )

        # ====================================================
        # LIVE FEED
        # ====================================================

        log_panel = ctk.CTkFrame(content)

        log_panel.pack(

            side="left",

            fill="both",

            expand=True,

            padx=(0, 9)

        )

        ctk.CTkLabel(

            log_panel,

            text="LIVE SECURITY FEED",

            font=ctk.CTkFont(

                size=15,

                weight="bold"

            )

        ).pack(

            anchor="w",

            padx=16,

            pady=13

        )

        self.log_box = ctk.CTkTextbox(

            log_panel,

            font=("Consolas", 12),

            wrap="none"

        )

        self.log_box.pack(

            fill="both",

            expand=True,

            padx=14,

            pady=(0, 14)

        )

        # ====================================================
        # THREAT PANEL
        # ====================================================

        threat_panel = ctk.CTkFrame(

            content,

            width=350

        )

        threat_panel.pack(

            side="right",

            fill="y",

            padx=(9, 0)

        )

        threat_panel.pack_propagate(False)

        ctk.CTkLabel(

            threat_panel,

            text="THREAT INTELLIGENCE",

            font=ctk.CTkFont(

                size=15,

                weight="bold"

            )

        ).pack(

            anchor="w",

            padx=16,

            pady=13

        )

        self.threat_box = ctk.CTkTextbox(

            threat_panel,

            font=("Consolas", 12),

            wrap="word"

        )

        self.threat_box.pack(

            fill="both",

            expand=True,

            padx=14,

            pady=(0, 10)

        )

        self.quarantine_button = ctk.CTkButton(

            threat_panel,

            text="QUARANTINE DETECTED THREATS",

            height=44,

            fg_color="#dc2626",

            hover_color="#b91c1c",

            command=self.quarantine_threats

        )

        self.quarantine_button.pack(

            fill="x",

            padx=14,

            pady=(0, 14)

        )


    # ========================================================
    # CARD CREATION
    # ========================================================

    def create_card(self, parent, title, value):

        frame = ctk.CTkFrame(

            parent,

            height=105

        )

        frame.pack(

            side="left",

            fill="x",

            expand=True,

            padx=6

        )

        frame.pack_propagate(False)

        ctk.CTkLabel(

            frame,

            text=title,

            text_color="#64748b",

            font=ctk.CTkFont(

                size=11,

                weight="bold"

            )

        ).pack(

            anchor="w",

            padx=18,

            pady=(15, 3)

        )

        value_label = ctk.CTkLabel(

            frame,

            text=value,

            font=ctk.CTkFont(

                size=31,

                weight="bold"

            )

        )

        value_label.pack(

            anchor="w",

            padx=18

        )

        return value_label


    # ========================================================
    # SELECT DRIVE
    # ========================================================

    def select_drive(self):

        path = filedialog.askdirectory(

            title="Select USB Drive or Folder"

        )

        if not path:

            return

        self.selected_path = path

        self.device_label.configure(

            text=f"DEVICE: {path}"

        )

        self.system_status.configure(

            text="● DEVICE READY",

            text_color="#38bdf8"

        )

        self.log(

            f"[DEVICE CONNECTED] {path}"

        )


    # ========================================================
    # START REAL SCAN
    # ========================================================

    def start_scan(self):

        if self.is_scanning:

            return

        if not self.selected_path:

            messagebox.showwarning(

                "No Device",

                "Select a USB drive or folder first."

            )

            return

        self.reset_interface()

        self.is_scanning = True

        thread = threading.Thread(

            target=self.real_scan_worker,

            daemon=True

        )

        thread.start()


    # ========================================================
    # REAL SCAN WORKER
    # ========================================================

    def real_scan_worker(self):

        self.safe_ui(

            self.system_status.configure,

            text="● SECURITY SCAN ACTIVE",

            text_color="#f59e0b"

        )

        self.safe_ui(

            self.scan_status.configure,

            text="ENUMERATING DEVICE FILES..."

        )

        files = get_files(self.selected_path)

        total_files = len(files)

        detected_threats = []

        max_risk = 0

        if total_files == 0:

            self.safe_ui(

                self.finish_real_scan,

                detected_threats,

                0,

                0

            )

            return

        for index, file_path in enumerate(

            files,

            start=1

        ):

            result = analyze_file(file_path)

            result["sha256"] = calculate_sha256(

                file_path

            )

            if result["score"] >= 40:

                detected_threats.append(result)

                max_risk = max(

                    max_risk,

                    result["score"]

                )

            progress = index / total_files

            self.safe_ui(

                self.update_real_scan,

                index,

                total_files,

                file_path,

                result,

                progress,

                len(detected_threats),

                max_risk

            )

        self.threats = detected_threats

        self.safe_ui(

            self.finish_real_scan,

            detected_threats,

            total_files,

            max_risk

        )


    # ========================================================
    # UPDATE REAL SCAN
    # ========================================================

    def update_real_scan(

        self,

        index,

        total,

        file_path,

        result,

        progress,

        threat_count,

        max_risk

    ):

        self.progress.set(progress)

        self.progress_value.configure(

            text=f"{int(progress * 100)}%"

        )

        self.files_value.configure(

            text=str(index)

        )

        self.threat_value.configure(

            text=str(threat_count)

        )

        self.risk_value.configure(

            text=f"{max_risk}%"

        )

        filename = os.path.basename(file_path)

        if result["score"] >= 40:

            self.log(

                f"[THREAT] {filename} "

                f"| RISK {result['score']}%"

            )

        elif result["score"] > 0:

            self.log(

                f"[WARNING] {filename} "

                f"| RISK {result['score']}%"

            )

        else:

            self.log(

                f"[SAFE] {filename}"

            )


    # ========================================================
    # FINISH REAL SCAN
    # ========================================================

    def finish_real_scan(

        self,

        threats,

        total_files,

        max_risk

    ):

        self.is_scanning = False

        self.progress.set(1)

        self.progress_value.configure(

            text="100%"

        )

        self.files_value.configure(

            text=str(total_files)

        )

        self.threat_value.configure(

            text=str(len(threats))

        )

        self.risk_value.configure(

            text=f"{max_risk}%"

        )

        self.threat_box.delete(

            "1.0",

            "end"

        )

        if threats:

            self.system_status.configure(

                text="● SECURITY THREATS FOUND",

                text_color="#ef4444"

            )

            self.scan_status.configure(

                text=(

                    f"SCAN COMPLETE — "

                    f"{len(threats)} THREATS DETECTED"

                )

            )

            for threat in threats:

                reasons = "\n".join(

                    f"• {reason}"

                    for reason in threat["reasons"]

                )

                sha = threat["sha256"]

                self.threat_box.insert(

                    "end",

                    f"CRITICAL FILE\n"

                    f"{threat['name']}\n\n"

                    f"RISK SCORE\n"

                    f"{threat['score']} / 100\n\n"

                    f"DETECTION SIGNALS\n"

                    f"{reasons}\n\n"

                    f"SHA-256\n"

                    f"{sha[:32]}...\n\n"

                    f"{'─' * 35}\n\n"

                )

        else:

            self.system_status.configure(

                text="● DEVICE SECURE",

                text_color="#22c55e"

            )

            self.scan_status.configure(

                text="SCAN COMPLETE — DEVICE SECURE"

            )

            self.threat_box.insert(

                "end",

                "SECURITY ANALYSIS COMPLETE\n\n"

                "No high-risk files were detected.\n\n"

                "DEVICE STATUS\n"

                "SECURE"

            )


    # ========================================================
    # VIRAL DEMO MODE
    # ========================================================

    def start_demo(self):

        if self.is_scanning:

            return

        self.reset_interface()

        self.is_scanning = True

        thread = threading.Thread(

            target=self.demo_worker,

            daemon=True

        )

        thread.start()


    def demo_worker(self):

        demo_files = [

            ("DCIM_1024.jpg", 0),

            ("holiday_video.mp4", 0),

            ("project_source.zip", 0),

            ("resume.pdf", 0),

            ("documents.docx", 0),

            ("backup_data.zip", 0),

            ("invoice.pdf.exe", 92),

            ("autorun.inf", 80),

            ("security_update.scr", 75),

        ]

        self.safe_ui(

            self.device_label.configure,

            text="USB DEVICE CONNECTED • E:\\"

        )

        self.safe_ui(

            self.system_status.configure,

            text="● USB DEVICE DETECTED",

            text_color="#38bdf8"

        )

        self.safe_ui(

            self.scan_status.configure,

            text="NEW USB DEVICE DETECTED..."

        )

        self.safe_ui(

            self.log,

            "[USB] Removable device connected."

        )

        time.sleep(0.8)

        self.safe_ui(

            self.scan_status.configure,

            text="AUTO SECURITY SCAN INITIALIZED..."

        )

        self.safe_ui(

            self.log,

            "[ENGINE] Heuristic scanner activated."

        )

        time.sleep(0.5)

        threats = []

        max_risk = 0

        total_demo_files = len(demo_files)

        for index, (

            filename,

            risk

        ) in enumerate(

            demo_files,

            start=1

        ):

            time.sleep(0.35)

            if risk >= 40:

                max_risk = max(

                    max_risk,

                    risk

                )

                threats.append(

                    {

                        "path": "",

                        "name": filename,

                        "score": risk,

                        "reasons": [

                            "Suspicious USB behavior",

                            "High-risk security signature"

                        ],

                        "sha256": hashlib.sha256(

                            filename.encode()

                        ).hexdigest()

                    }

                )

            fake_checked = int(

                147

                * index

                / total_demo_files

            )

            progress = (

                index

                / total_demo_files

            )

            self.safe_ui(

                self.update_demo,

                filename,

                risk,

                fake_checked,

                len(threats),

                max_risk,

                progress

            )

        time.sleep(0.5)

        self.threats = []

        self.safe_ui(

            self.finish_demo

        )


    def update_demo(

        self,

        filename,

        risk,

        checked,

        threat_count,

        max_risk,

        progress

    ):

        self.progress.set(progress)

        self.progress_value.configure(

            text=f"{int(progress * 100)}%"

        )

        self.files_value.configure(

            text=str(checked)

        )

        self.threat_value.configure(

            text=str(threat_count)

        )

        self.risk_value.configure(

            text=f"{max_risk}%"

        )

        if risk >= 40:

            self.log(

                f"[CRITICAL] {filename} "

                f"| THREAT SCORE {risk}%"

            )

        else:

            self.log(

                f"[SAFE] {filename}"

            )


    def finish_demo(self):

        self.is_scanning = False

        self.progress.set(1)

        self.progress_value.configure(

            text="100%"

        )

        self.files_value.configure(

            text="147"

        )

        self.threat_value.configure(

            text="3"

        )

        self.risk_value.configure(

            text="92%"

        )

        self.system_status.configure(

            text="● CRITICAL SECURITY ALERT",

            text_color="#ef4444"

        )

        self.scan_status.configure(

            text="SCAN COMPLETE — 3 THREATS DETECTED"

        )

        self.threat_box.delete(

            "1.0",

            "end"

        )

        self.threat_box.insert(

            "end",

            "CRITICAL THREAT DETECTED\n\n"

            "FILE\n"

            "invoice.pdf.exe\n\n"

            "RISK SCORE\n"

            "92 / 100\n\n"

            "DETECTION SIGNALS\n"

            "• Misleading double extension\n"

            "• Executable file disguised as PDF\n"

            "• Suspicious USB execution pattern\n"

            "• High-risk heuristic score\n\n"

            "SECONDARY THREATS\n"

            "autorun.inf          80%\n"

            "security_update.scr  75%\n\n"

            "RECOMMENDED ACTION\n"

            "QUARANTINE IMMEDIATELY"

        )


    # ========================================================
    # QUARANTINE
    # ========================================================

    def quarantine_threats(self):

        if not self.threats:

            messagebox.showinfo(

                "Quarantine",

                "No real scanned threats available.\n\n"

                "Demo Mode does not modify files."

            )

            return

        confirm = messagebox.askyesno(

            "Confirm Quarantine",

            f"Move {len(self.threats)} detected files "

            "into the local quarantine folder?"

        )

        if not confirm:

            return

        successful = 0

        for threat in self.threats:

            success, result = quarantine_file(

                threat["path"]

            )

            if success:

                successful += 1

                self.log(

                    f"[QUARANTINED] "

                    f"{threat['name']}"

                )

            else:

                self.log(

                    f"[FAILED] "

                    f"{threat['name']} | {result}"

                )

        self.system_status.configure(

            text="● SYSTEM PROTECTED",

            text_color="#22c55e"

        )

        self.scan_status.configure(

            text=f"{successful} THREATS QUARANTINED"

        )

        messagebox.showinfo(

            "Quarantine Complete",

            f"{successful} files moved to quarantine."

        )


    # ========================================================
    # RESET
    # ========================================================

    def reset_interface(self):

        self.threats = []

        self.progress.set(0)

        self.progress_value.configure(

            text="0%"

        )

        self.files_value.configure(

            text="0"

        )

        self.threat_value.configure(

            text="0"

        )

        self.risk_value.configure(

            text="0%"

        )

        self.log_box.delete(

            "1.0",

            "end"

        )

        self.threat_box.delete(

            "1.0",

            "end"

        )

        self.scan_status.configure(

            text="INITIALIZING SECURITY ENGINE..."

        )


    # ========================================================
    # LOGGING
    # ========================================================

    def log(self, message):

        timestamp = time.strftime("%H:%M:%S")

        self.log_box.insert(

            "end",

            f"{timestamp}  {message}\n"

        )

        self.log_box.see("end")


    # ========================================================
    # THREAD SAFE UI
    # ========================================================

    def safe_ui(self, callback, *args, **kwargs):

        self.after(

            0,

            lambda: callback(

                *args,

                **kwargs

            )

        )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = USBThreatScanner()

    app.mainloop()