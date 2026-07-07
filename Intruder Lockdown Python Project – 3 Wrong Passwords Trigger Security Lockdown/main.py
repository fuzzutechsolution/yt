import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import hashlib
import secrets
import shutil
import json
import threading
import time


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "INTRUDER LOCKDOWN"
WINDOW_WIDTH = 540
WINDOW_HEIGHT = 960

BG = "#080C14"
CARD = "#111824"
CARD_2 = "#0C121D"
BORDER = "#263244"

CYAN = "#00C8FF"
GREEN = "#28D17C"
RED = "#FF334F"
ORANGE = "#FF9F1C"
PURPLE = "#7C3AED"

TEXT = "#F5F7FA"
MUTED = "#7F91A8"

MAX_ATTEMPTS = 3

BASE_DIR = Path.home() / ".fuzzutech_lockdown"
VAULT_DIR = BASE_DIR / "private_vault"
CONFIG_FILE = BASE_DIR / "config.json"

BASE_DIR.mkdir(parents=True, exist_ok=True)
VAULT_DIR.mkdir(parents=True, exist_ok=True)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# SECURITY HELPERS
# ============================================================

def create_password_hash(password, salt=None):
    if salt is None:
        salt = secrets.token_bytes(32)

    result = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    )

    return salt.hex(), result.hex()


def verify_password(password, salt_hex, hash_hex):
    try:
        salt = bytes.fromhex(salt_hex)

        result = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000
        ).hex()

        return secrets.compare_digest(result, hash_hex)

    except (ValueError, TypeError):
        return False


def count_files(folder):
    try:
        return sum(
            1
            for item in Path(folder).rglob("*")
            if item.is_file()
        )
    except (OSError, PermissionError):
        return 0


def load_config():
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except (OSError, json.JSONDecodeError):
        return {}


def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


# ============================================================
# APPLICATION
# ============================================================

class LockdownApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} | FUZZUTECH")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.configure(fg_color=BG)

        self.failed_attempts = 0
        self.lockdown_active = False
        self.selected_folder = None
        self.demo_running = False

        self.config_data = load_config()

        self.build_gui()
        self.load_saved_state()

    # ========================================================
    # CARD HELPER
    # ========================================================

    def make_card(self, parent, height=None):

        options = {
            "fg_color": CARD,
            "corner_radius": 14,
            "border_width": 1,
            "border_color": BORDER
        }

        if height is not None:
            options["height"] = height

        frame = ctk.CTkFrame(parent, **options)

        if height is not None:
            frame.pack_propagate(False)

        return frame

    # ========================================================
    # GUI
    # ========================================================

    def build_gui(self):

        self.page = ctk.CTkScrollableFrame(
            self,
            fg_color=BG,
            corner_radius=0,
            scrollbar_button_color="#1D2938",
            scrollbar_button_hover_color="#34465D"
        )
        self.page.pack(fill="both", expand=True)

        # HEADER

        header = ctk.CTkFrame(
            self.page,
            fg_color="transparent"
        )
        header.pack(fill="x", padx=18, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="FUZZUTECH SECURITY LAB",
            font=("Arial", 11, "bold"),
            text_color=CYAN
        ).pack()

        ctk.CTkLabel(
            header,
            text="INTRUDER\nLOCKDOWN",
            font=("Arial", 34, "bold"),
            text_color=TEXT,
            justify="center"
        ).pack(pady=(3, 0))

        ctk.CTkLabel(
            header,
            text="PYTHON SECURITY SYSTEM",
            font=("Arial", 12, "bold"),
            text_color=MUTED
        ).pack(pady=(2, 8))

        # HOOK CARD

        self.hook_card = ctk.CTkFrame(
            self.page,
            fg_color="#0D1826",
            corner_radius=14,
            border_width=1,
            border_color="#164D70"
        )
        self.hook_card.pack(fill="x", padx=18, pady=7)

        self.hook_label = ctk.CTkLabel(
            self.hook_card,
            text="3 WRONG PASSWORDS = LOCKDOWN",
            font=("Arial", 18, "bold"),
            text_color=CYAN,
            wraplength=460
        )
        self.hook_label.pack(pady=18)

        # STATS

        stats = ctk.CTkFrame(
            self.page,
            fg_color="transparent"
        )
        stats.pack(fill="x", padx=18, pady=7)

        stats.grid_columnconfigure(0, weight=1)
        stats.grid_columnconfigure(1, weight=1)

        attempt_card = self.make_card(stats)
        attempt_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 5)
        )

        ctk.CTkLabel(
            attempt_card,
            text="FAILED ATTEMPTS",
            font=("Arial", 11, "bold"),
            text_color=MUTED
        ).pack(pady=(13, 0))

        self.attempt_value = ctk.CTkLabel(
            attempt_card,
            text="0 / 3",
            font=("Arial", 30, "bold"),
            text_color=GREEN
        )
        self.attempt_value.pack(pady=(2, 13))

        files_card = self.make_card(stats)
        files_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(5, 0)
        )

        ctk.CTkLabel(
            files_card,
            text="FILES PROTECTED",
            font=("Arial", 11, "bold"),
            text_color=MUTED
        ).pack(pady=(13, 0))

        self.files_value = ctk.CTkLabel(
            files_card,
            text="0",
            font=("Arial", 30, "bold"),
            text_color=CYAN
        )
        self.files_value.pack(pady=(2, 13))

        # TARGET CARD

        target_card = self.make_card(self.page)
        target_card.pack(fill="x", padx=18, pady=7)

        ctk.CTkLabel(
            target_card,
            text="PROTECTED TARGET",
            font=("Arial", 11, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=15, pady=(12, 2))

        self.target_label = ctk.CTkLabel(
            target_card,
            text="NO FOLDER SELECTED",
            font=("Arial", 14, "bold"),
            text_color=TEXT,
            wraplength=460,
            justify="left"
        )
        self.target_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        self.select_button = ctk.CTkButton(
            target_card,
            text="SELECT FOLDER",
            height=43,
            corner_radius=10,
            font=("Arial", 14, "bold"),
            fg_color="#1D6FA5",
            hover_color="#2788C5",
            command=self.select_folder
        )
        self.select_button.pack(
            fill="x",
            padx=15,
            pady=(0, 14)
        )

        # AUTH CARD

        auth_card = self.make_card(self.page)
        auth_card.pack(fill="x", padx=18, pady=7)

        ctk.CTkLabel(
            auth_card,
            text="SECURITY PASSWORD",
            font=("Arial", 11, "bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=15, pady=(13, 5))

        self.password_entry = ctk.CTkEntry(
            auth_card,
            placeholder_text="Enter security password...",
            show="*",
            height=46,
            corner_radius=10,
            fg_color=CARD_2,
            border_color=BORDER,
            font=("Arial", 14)
        )
        self.password_entry.pack(
            fill="x",
            padx=15,
            pady=(0, 10)
        )

        self.password_entry.bind(
            "<Return>",
            lambda event: self.verify_access()
        )

        button_row = ctk.CTkFrame(
            auth_card,
            fg_color="transparent"
        )
        button_row.pack(
            fill="x",
            padx=15,
            pady=(0, 14)
        )

        button_row.grid_columnconfigure(0, weight=1)
        button_row.grid_columnconfigure(1, weight=1)

        self.protect_button = ctk.CTkButton(
            button_row,
            text="ACTIVATE",
            height=43,
            corner_radius=10,
            font=("Arial", 13, "bold"),
            fg_color=PURPLE,
            hover_color="#6D28D9",
            command=self.activate_protection
        )
        self.protect_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5)
        )

        self.verify_button = ctk.CTkButton(
            button_row,
            text="VERIFY ACCESS",
            height=43,
            corner_radius=10,
            font=("Arial", 13, "bold"),
            fg_color="#1677B8",
            hover_color="#208FD3",
            command=self.verify_access
        )
        self.verify_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0)
        )

        # ALERT CARD

        self.alert_card = ctk.CTkFrame(
            self.page,
            fg_color="#0B251A",
            corner_radius=14,
            border_width=1,
            border_color="#17623F"
        )
        self.alert_card.pack(fill="x", padx=18, pady=7)

        self.alert_title = ctk.CTkLabel(
            self.alert_card,
            text="SYSTEM ARMED",
            font=("Arial", 20, "bold"),
            text_color=GREEN
        )
        self.alert_title.pack(pady=(15, 2))

        self.alert_subtitle = ctk.CTkLabel(
            self.alert_card,
            text="Waiting for authentication attempts",
            font=("Arial", 12),
            text_color=MUTED,
            wraplength=460
        )
        self.alert_subtitle.pack(pady=(0, 15))

        # PROGRESS

        progress_card = self.make_card(self.page)
        progress_card.pack(fill="x", padx=18, pady=7)

        progress_header = ctk.CTkFrame(
            progress_card,
            fg_color="transparent"
        )
        progress_header.pack(
            fill="x",
            padx=15,
            pady=(12, 5)
        )

        self.progress_text = ctk.CTkLabel(
            progress_header,
            text="SECURITY LEVEL: SAFE",
            font=("Arial", 12, "bold"),
            text_color=GREEN
        )
        self.progress_text.pack(side="left")

        self.progress_percent = ctk.CTkLabel(
            progress_header,
            text="0%",
            font=("Arial", 12, "bold"),
            text_color=GREEN
        )
        self.progress_percent.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(
            progress_card,
            height=12,
            corner_radius=6,
            progress_color=GREEN,
            fg_color="#26313E"
        )
        self.progress_bar.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )
        self.progress_bar.set(0)

        # LIVE FEED

        feed_card = self.make_card(self.page)
        feed_card.pack(fill="x", padx=18, pady=7)

        feed_header = ctk.CTkFrame(
            feed_card,
            fg_color="transparent"
        )
        feed_header.pack(
            fill="x",
            padx=15,
            pady=(12, 5)
        )

        ctk.CTkLabel(
            feed_header,
            text="LIVE SECURITY FEED",
            font=("Arial", 13, "bold"),
            text_color=TEXT
        ).pack(side="left")

        self.feed_state = ctk.CTkLabel(
            feed_header,
            text="LIVE",
            font=("Arial", 11, "bold"),
            text_color=GREEN
        )
        self.feed_state.pack(side="right")

        self.feed = ctk.CTkTextbox(
            feed_card,
            height=145,
            corner_radius=10,
            fg_color="#070B11",
            border_width=1,
            border_color="#1D2938",
            font=("Consolas", 12),
            text_color="#B5C5D8"
        )
        self.feed.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )
        self.feed.configure(state="disabled")

        # BOTTOM BUTTONS

        self.restore_button = ctk.CTkButton(
            self.page,
            text="RESTORE PROTECTED FOLDER",
            height=46,
            corner_radius=12,
            font=("Arial", 14, "bold"),
            fg_color="#A56A12",
            hover_color="#C37D14",
            command=self.restore_folder
        )
        self.restore_button.pack(
            fill="x",
            padx=18,
            pady=(7, 4)
        )

        self.demo_button = ctk.CTkButton(
            self.page,
            text="START VIRAL DEMO MODE",
            height=52,
            corner_radius=12,
            font=("Arial", 16, "bold"),
            fg_color=PURPLE,
            hover_color="#6D28D9",
            command=self.start_demo
        )
        self.demo_button.pack(
            fill="x",
            padx=18,
            pady=(4, 12)
        )

        ctk.CTkLabel(
            self.page,
            text="FUZZUTECH • DEFENSIVE SECURITY DEMO",
            font=("Arial", 10, "bold"),
            text_color="#45566C"
        ).pack(pady=(0, 18))

        self.log("System initialized.")
        self.log("Security engine ready.")

    # ========================================================
    # SAVED STATE
    # ========================================================

    def load_saved_state(self):

        if not self.config_data.get("password_hash"):
            return

        vault_path = self.config_data.get("vault_path")
        original_path = self.config_data.get("original_path")

        if not vault_path:
            return

        vault = Path(vault_path)

        if not vault.exists():
            return

        self.selected_folder = original_path

        if original_path:
            self.target_label.configure(
                text=Path(original_path).name.upper()
            )

        file_count = count_files(vault)

        self.files_value.configure(text=str(file_count))

        self.set_safe_state(
            "PROTECTION ACTIVE",
            "Private vault secured"
        )

        self.log(
            f"Protected vault loaded: {file_count} files."
        )

    # ========================================================
    # LOGGING
    # ========================================================

    def log(self, text):

        timestamp = time.strftime("%H:%M:%S")

        self.feed.configure(state="normal")
        self.feed.insert(
            "end",
            f"[{timestamp}] {text}\n"
        )
        self.feed.see("end")
        self.feed.configure(state="disabled")

    # ========================================================
    # SELECT FOLDER
    # ========================================================

    def select_folder(self):

        if self.config_data.get("password_hash"):
            messagebox.showinfo(
                "Protection Active",
                "Restore the current protected folder before selecting another folder."
            )
            return

        folder = filedialog.askdirectory(
            title="Select Folder To Protect"
        )

        if not folder:
            return

        selected = Path(folder).resolve()

        try:
            base_resolved = BASE_DIR.resolve()

            if (
                selected == base_resolved
                or base_resolved in selected.parents
            ):
                messagebox.showerror(
                    "Invalid Folder",
                    "The application data folder cannot be selected."
                )
                return

        except OSError:
            pass

        self.selected_folder = str(selected)

        self.target_label.configure(
            text=selected.name.upper()
        )

        file_count = count_files(selected)

        self.files_value.configure(
            text=str(file_count)
        )

        self.log(
            f"Target selected: {selected.name}"
        )

        self.log(
            f"{file_count} files detected."
        )

    # ========================================================
    # ACTIVATE PROTECTION
    # ========================================================

    def activate_protection(self):

        if self.config_data.get("password_hash"):
            messagebox.showinfo(
                "Protection Active",
                "A protected vault already exists."
            )
            return

        if not self.selected_folder:
            messagebox.showwarning(
                "Folder Required",
                "Select a folder first."
            )
            return

        password = self.password_entry.get().strip()

        if len(password) < 4:
            messagebox.showwarning(
                "Weak Password",
                "Use at least 4 characters."
            )
            return

        source = Path(self.selected_folder)

        if not source.exists() or not source.is_dir():
            messagebox.showerror(
                "Folder Error",
                "Selected folder does not exist."
            )
            return

        destination = VAULT_DIR / source.name

        if destination.exists():
            destination = (
                VAULT_DIR /
                f"{source.name}_{int(time.time())}"
            )

        confirm = messagebox.askyesno(
            "Activate Protection",
            "Move this folder into the local private vault?\n\n"
            "Use a test folder first."
        )

        if not confirm:
            return

        try:
            file_count = count_files(source)

            salt, password_hash = create_password_hash(
                password
            )

            shutil.move(
                str(source),
                str(destination)
            )

            self.config_data = {
                "original_path": str(source),
                "vault_path": str(destination),
                "salt": salt,
                "password_hash": password_hash
            }

            save_config(self.config_data)

            self.files_value.configure(
                text=str(file_count)
            )

            self.password_entry.delete(0, "end")

            self.log("Folder moved to private vault.")
            self.log("Password protection activated.")

            self.set_safe_state(
                "PROTECTION ACTIVE",
                "Private vault secured"
            )

            messagebox.showinfo(
                "Protection Active",
                "Folder protection activated successfully."
            )

        except (OSError, shutil.Error) as error:
            messagebox.showerror(
                "Protection Error",
                str(error)
            )

    # ========================================================
    # VERIFY ACCESS
    # ========================================================

    def verify_access(self):

        if self.lockdown_active:
            self.log(
                "ACCESS BLOCKED: Lockdown is active."
            )
            self.flash_lockdown()
            return

        if not self.config_data.get("password_hash"):
            messagebox.showwarning(
                "No Protection",
                "Activate protection first."
            )
            return

        password = self.password_entry.get()
        self.password_entry.delete(0, "end")

        if verify_password(
            password,
            self.config_data.get("salt", ""),
            self.config_data.get("password_hash", "")
        ):
            self.access_granted()

        else:
            self.access_denied()

    # ========================================================
    # ACCESS GRANTED
    # ========================================================

    def access_granted(self):

        self.failed_attempts = 0

        self.attempt_value.configure(
            text="0 / 3",
            text_color=GREEN
        )

        self.progress_bar.configure(
            progress_color=GREEN
        )
        self.progress_bar.set(0)

        self.progress_text.configure(
            text="SECURITY LEVEL: SAFE",
            text_color=GREEN
        )

        self.progress_percent.configure(
            text="0%",
            text_color=GREEN
        )

        self.alert_card.configure(
            fg_color="#0B251A",
            border_color="#17623F"
        )

        self.alert_title.configure(
            text="ACCESS GRANTED",
            text_color=GREEN
        )

        self.alert_subtitle.configure(
            text="Identity verified successfully"
        )

        self.hook_label.configure(
            text="PASSWORD VERIFIED • ACCESS GRANTED",
            text_color=GREEN
        )

        self.feed_state.configure(
            text="LIVE",
            text_color=GREEN
        )

        self.log("Password verified.")
        self.log("ACCESS GRANTED.")

    # ========================================================
    # ACCESS DENIED
    # ========================================================

    def access_denied(self):

        self.failed_attempts += 1
        attempt = self.failed_attempts

        if attempt == 1:
            color = ORANGE
            risk = 0.33
            percent = "33%"
            level = "SUSPICIOUS"

        elif attempt == 2:
            color = RED
            risk = 0.66
            percent = "66%"
            level = "HIGH RISK"

        else:
            color = RED
            risk = 1.0
            percent = "100%"
            level = "CRITICAL"

        self.attempt_value.configure(
            text=f"{attempt} / 3",
            text_color=color
        )

        self.progress_bar.configure(
            progress_color=color
        )
        self.progress_bar.set(risk)

        self.progress_text.configure(
            text=f"SECURITY LEVEL: {level}",
            text_color=color
        )

        self.progress_percent.configure(
            text=percent,
            text_color=color
        )

        self.alert_card.configure(
            fg_color="#2A1415",
            border_color="#6D252A"
        )

        self.alert_title.configure(
            text=f"ACCESS DENIED • ATTEMPT {attempt}",
            text_color=color
        )

        remaining = MAX_ATTEMPTS - attempt

        if remaining > 0:
            self.alert_subtitle.configure(
                text=f"{remaining} attempt(s) remaining before lockdown"
            )

        self.hook_label.configure(
            text=f"WRONG PASSWORD #{attempt}",
            text_color=color
        )

        self.log(
            f"Invalid password detected. Attempt {attempt}/3."
        )

        if attempt >= MAX_ATTEMPTS:
            self.activate_lockdown()

    # ========================================================
    # LOCKDOWN
    # ========================================================

    def activate_lockdown(self):

        self.lockdown_active = True

        self.alert_card.configure(
            fg_color="#3A0B12",
            border_color=RED
        )

        self.alert_title.configure(
            text="INTRUDER DETECTED",
            text_color=RED
        )

        self.alert_subtitle.configure(
            text="SECURITY LOCKDOWN ACTIVE • ACCESS BLOCKED"
        )

        self.hook_label.configure(
            text="3 FAILED ATTEMPTS • LOCKDOWN ACTIVE",
            text_color=RED
        )

        self.attempt_value.configure(
            text="3 / 3",
            text_color=RED
        )

        self.progress_bar.configure(
            progress_color=RED
        )
        self.progress_bar.set(1)

        self.progress_text.configure(
            text="SECURITY LEVEL: CRITICAL",
            text_color=RED
        )

        self.progress_percent.configure(
            text="100%",
            text_color=RED
        )

        self.feed_state.configure(
            text="ALERT",
            text_color=RED
        )

        self.log(
            "CRITICAL: Three failed authentication attempts."
        )
        self.log("INTRUDER DETECTED.")
        self.log("SECURITY LOCKDOWN ACTIVATED.")
        self.log("ACCESS BLOCKED.")

        self.flash_lockdown()

    def flash_lockdown(self, count=0):

        if count >= 8:
            self.alert_card.configure(
                fg_color="#3A0B12"
            )
            return

        current = (
            RED
            if count % 2 == 0
            else "#3A0B12"
        )

        self.alert_card.configure(
            fg_color=current
        )

        self.after(
            180,
            lambda: self.flash_lockdown(count + 1)
        )

    # ========================================================
    # SAFE STATE
    # ========================================================

    def set_safe_state(self, title, subtitle):

        self.alert_card.configure(
            fg_color="#0B251A",
            border_color="#17623F"
        )

        self.alert_title.configure(
            text=title,
            text_color=GREEN
        )

        self.alert_subtitle.configure(
            text=subtitle
        )

    # ========================================================
    # RESTORE
    # ========================================================

    def restore_folder(self):

        if not self.config_data.get("vault_path"):
            messagebox.showwarning(
                "No Vault",
                "No protected folder exists."
            )
            return

        password = self.password_entry.get()

        if not verify_password(
            password,
            self.config_data.get("salt", ""),
            self.config_data.get("password_hash", "")
        ):
            messagebox.showerror(
                "Access Denied",
                "Correct password required."
            )
            return

        vault_path = Path(
            self.config_data["vault_path"]
        )

        original_path = Path(
            self.config_data["original_path"]
        )

        try:
            if not vault_path.exists():
                messagebox.showerror(
                    "Restore Error",
                    "Protected vault folder is missing."
                )
                return

            if original_path.exists():
                messagebox.showerror(
                    "Restore Error",
                    "Original destination already exists."
                )
                return

            shutil.move(
                str(vault_path),
                str(original_path)
            )

            self.config_data = {}
            save_config({})

            self.selected_folder = None
            self.failed_attempts = 0
            self.lockdown_active = False

            self.target_label.configure(
                text="NO FOLDER SELECTED"
            )

            self.files_value.configure(text="0")

            self.attempt_value.configure(
                text="0 / 3",
                text_color=GREEN
            )

            self.password_entry.delete(0, "end")

            self.hook_label.configure(
                text="3 WRONG PASSWORDS = LOCKDOWN",
                text_color=CYAN
            )

            self.progress_bar.configure(
                progress_color=GREEN
            )
            self.progress_bar.set(0)

            self.progress_text.configure(
                text="SECURITY LEVEL: SAFE",
                text_color=GREEN
            )

            self.progress_percent.configure(
                text="0%",
                text_color=GREEN
            )

            self.feed_state.configure(
                text="LIVE",
                text_color=GREEN
            )

            self.set_safe_state(
                "SYSTEM ARMED",
                "Waiting for authentication attempts"
            )

            self.log("Protected folder restored.")

            messagebox.showinfo(
                "Restored",
                "Folder restored successfully."
            )

        except (OSError, shutil.Error) as error:
            messagebox.showerror(
                "Restore Error",
                str(error)
            )

    # ========================================================
    # DEMO MODE
    # ========================================================

    def start_demo(self):

        if self.demo_running:
            return

        self.demo_running = True

        self.demo_button.configure(
            text="DEMO RUNNING...",
            state="disabled"
        )

        thread = threading.Thread(
            target=self.run_demo,
            daemon=True
        )
        thread.start()

    def ui(self, callback):
        self.after(0, callback)

    def run_demo(self):

        self.ui(self.reset_demo_state)
        time.sleep(0.8)

        self.ui(
            lambda: self.hook_label.configure(
                text="UNKNOWN USER IS TRYING TO ACCESS YOUR FILES",
                text_color=RED
            )
        )

        self.ui(
            lambda: self.log(
                "Unknown authentication activity detected."
            )
        )

        time.sleep(1.7)

        self.ui(
            lambda: self.files_value.configure(
                text="147"
            )
        )

        self.ui(
            lambda: self.target_label.configure(
                text="PRIVATE_PROJECT_FILES"
            )
        )

        self.ui(
            lambda: self.log(
                "147 files secured inside private vault."
            )
        )

        time.sleep(1.5)

        self.ui(self.demo_attempt_one)
        time.sleep(2.2)

        self.ui(self.demo_attempt_two)
        time.sleep(2.2)

        self.ui(self.demo_attempt_three)
        time.sleep(1.3)

        self.ui(self.demo_lockdown)
        time.sleep(4.5)

        self.ui(
            lambda: self.hook_label.configure(
                text="3 WRONG PASSWORDS = LOCKDOWN",
                text_color=CYAN
            )
        )

        self.ui(
            lambda: self.log(
                "Demo complete."
            )
        )

        time.sleep(0.8)

        self.ui(self.finish_demo)

    def reset_demo_state(self):

        self.failed_attempts = 0
        self.lockdown_active = False

        self.attempt_value.configure(
            text="0 / 3",
            text_color=GREEN
        )

        self.files_value.configure(text="0")

        self.target_label.configure(
            text="SECURITY VAULT"
        )

        self.hook_label.configure(
            text="3 WRONG PASSWORDS = LOCKDOWN",
            text_color=CYAN
        )

        self.alert_card.configure(
            fg_color="#0B251A",
            border_color="#17623F"
        )

        self.alert_title.configure(
            text="SYSTEM ARMED",
            text_color=GREEN
        )

        self.alert_subtitle.configure(
            text="Waiting for authentication attempts"
        )

        self.progress_bar.configure(
            progress_color=GREEN
        )
        self.progress_bar.set(0)

        self.progress_text.configure(
            text="SECURITY LEVEL: SAFE",
            text_color=GREEN
        )

        self.progress_percent.configure(
            text="0%",
            text_color=GREEN
        )

        self.feed_state.configure(
            text="LIVE",
            text_color=GREEN
        )

        self.log("Viral Demo Mode started.")

    def demo_attempt_one(self):

        self.attempt_value.configure(
            text="1 / 3",
            text_color=ORANGE
        )

        self.hook_label.configure(
            text="WRONG PASSWORD #1",
            text_color=ORANGE
        )

        self.alert_card.configure(
            fg_color="#261C0C",
            border_color="#76501A"
        )

        self.alert_title.configure(
            text="ACCESS DENIED • ATTEMPT 1",
            text_color=ORANGE
        )

        self.alert_subtitle.configure(
            text="2 attempts remaining before lockdown"
        )

        self.progress_bar.configure(
            progress_color=ORANGE
        )
        self.progress_bar.set(0.33)

        self.progress_text.configure(
            text="SECURITY LEVEL: SUSPICIOUS",
            text_color=ORANGE
        )

        self.progress_percent.configure(
            text="33%",
            text_color=ORANGE
        )

        self.log(
            "Wrong password detected • Attempt 1/3."
        )

    def demo_attempt_two(self):

        self.attempt_value.configure(
            text="2 / 3",
            text_color=RED
        )

        self.hook_label.configure(
            text="WRONG PASSWORD #2",
            text_color=RED
        )

        self.alert_card.configure(
            fg_color="#2A1415",
            border_color="#6D252A"
        )

        self.alert_title.configure(
            text="ACCESS DENIED • ATTEMPT 2",
            text_color=RED
        )

        self.alert_subtitle.configure(
            text="1 attempt remaining before security lockdown"
        )

        self.progress_bar.configure(
            progress_color=RED
        )
        self.progress_bar.set(0.66)

        self.progress_text.configure(
            text="SECURITY LEVEL: HIGH RISK",
            text_color=RED
        )

        self.progress_percent.configure(
            text="66%",
            text_color=RED
        )

        self.log(
            "Repeated unauthorized access detected."
        )

        self.log(
            "Wrong password detected • Attempt 2/3."
        )

    def demo_attempt_three(self):

        self.attempt_value.configure(
            text="3 / 3",
            text_color=RED
        )

        self.hook_label.configure(
            text="FINAL WRONG PASSWORD • LOCKING FILES...",
            text_color=RED
        )

        self.alert_card.configure(
            fg_color="#3A0B12",
            border_color=RED
        )

        self.alert_title.configure(
            text="CRITICAL AUTHENTICATION FAILURE",
            text_color=RED
        )

        self.alert_subtitle.configure(
            text="Maximum failed password attempts reached"
        )

        self.progress_bar.configure(
            progress_color=RED
        )
        self.progress_bar.set(1)

        self.progress_text.configure(
            text="SECURITY LEVEL: CRITICAL",
            text_color=RED
        )

        self.progress_percent.configure(
            text="100%",
            text_color=RED
        )

        self.log(
            "Wrong password detected • Attempt 3/3."
        )

        self.log(
            "Maximum authentication failures reached."
        )

    def demo_lockdown(self):

        self.lockdown_active = True

        self.hook_label.configure(
            text="INTRUDER DETECTED • ACCESS BLOCKED",
            text_color=RED
        )

        self.alert_card.configure(
            fg_color="#3A0B12",
            border_color=RED
        )

        self.alert_title.configure(
            text="INTRUDER DETECTED",
            text_color=RED
        )

        self.alert_subtitle.configure(
            text="LOCKDOWN ACTIVE • 147 FILES PROTECTED"
        )

        self.feed_state.configure(
            text="LOCKDOWN",
            text_color=RED
        )

        self.log("INTRUDER DETECTED.")
        self.log("SECURITY LOCKDOWN ACTIVATED.")
        self.log("147 FILES PROTECTED.")
        self.log("ACCESS BLOCKED.")

        self.flash_lockdown()

    def finish_demo(self):

        self.demo_running = False

        self.demo_button.configure(
            text="REPLAY VIRAL DEMO",
            state="normal"
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app = LockdownApp()
    app.mainloop()