import os
import re
import time
import base64
import sqlite3
import secrets
import string
import hashlib
import hmac
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import pyperclip
from cryptography.fernet import Fernet, InvalidToken


# =========================================================
# CONFIG
# =========================================================

APP_NAME = "SecureVault Pro"
DB_FILE = "securevault.db"

PBKDF2_ITERATIONS = 600_000

AUTO_LOCK_SECONDS = 180
CLIPBOARD_CLEAR_SECONDS = 20


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# =========================================================
# DATABASE
# =========================================================

class Database:

    def __init__(self):

        self.conn = sqlite3.connect(DB_FILE)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS settings(

            id INTEGER PRIMARY KEY,

            salt BLOB NOT NULL,

            verifier BLOB NOT NULL

        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS credentials(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            service BLOB NOT NULL,

            username BLOB NOT NULL,

            password BLOB NOT NULL,

            notes BLOB,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.conn.commit()


    def master_exists(self):

        row = self.conn.execute(
            "SELECT id FROM settings WHERE id=1"
        ).fetchone()

        return row is not None


    def create_master(self, salt, verifier):

        self.conn.execute(

            "INSERT INTO settings(id,salt,verifier) VALUES(1,?,?)",

            (salt, verifier)

        )

        self.conn.commit()


    def get_master(self):

        return self.conn.execute(

            "SELECT salt,verifier FROM settings WHERE id=1"

        ).fetchone()


    def add_credential(
        self,
        service,
        username,
        password,
        notes
    ):

        self.conn.execute("""

        INSERT INTO credentials(

        service,
        username,
        password,
        notes

        )

        VALUES(?,?,?,?)

        """,

        (
            service,
            username,
            password,
            notes
        ))

        self.conn.commit()


    def update_credential(
        self,
        credential_id,
        service,
        username,
        password,
        notes
    ):

        self.conn.execute("""

        UPDATE credentials

        SET

        service=?,
        username=?,
        password=?,
        notes=?

        WHERE id=?

        """,

        (
            service,
            username,
            password,
            notes,
            credential_id
        ))

        self.conn.commit()


    def delete_credential(self, credential_id):

        self.conn.execute(

            "DELETE FROM credentials WHERE id=?",

            (credential_id,)

        )

        self.conn.commit()


    def get_credentials(self):

        return self.conn.execute("""

        SELECT

        id,
        service,
        username,
        password,
        notes

        FROM credentials

        ORDER BY id DESC

        """).fetchall()


# =========================================================
# SECURITY
# =========================================================

class SecurityManager:

    @staticmethod
    def derive_key(master_password, salt):

        raw_key = hashlib.pbkdf2_hmac(

            "sha256",

            master_password.encode(),

            salt,

            PBKDF2_ITERATIONS,

            dklen=32

        )

        return base64.urlsafe_b64encode(raw_key)


    @staticmethod
    def create_verifier(key):

        return hmac.new(

            key,

            b"SECUREVAULT_MASTER_VERIFIER",

            hashlib.sha256

        ).digest()


    @staticmethod
    def verify_master(key, stored_verifier):

        new_verifier = SecurityManager.create_verifier(key)

        return hmac.compare_digest(

            new_verifier,

            stored_verifier

        )


    @staticmethod
    def password_strength(password):

        score = 0

        if len(password) >= 8:
            score += 1

        if len(password) >= 12:
            score += 1

        if re.search(r"[A-Z]", password):
            score += 1

        if re.search(r"[a-z]", password):
            score += 1

        if re.search(r"\d", password):
            score += 1

        if re.search(
            r"""[!@#$%^&*()_+\-=\[\]{};:'",.<>/?\\|`]""",
            password
        ):
            score += 1

        if score <= 2:

            return "WEAK", 0.25

        elif score <= 4:

            return "MEDIUM", 0.60

        return "STRONG", 1.0


# =========================================================
# PASSWORD MANAGER APPLICATION
# =========================================================

class SecureVault(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(APP_NAME)

        self.geometry("1180x720")

        self.minsize(1000, 650)

        self.db = Database()

        self.fernet = None

        self.selected_id = None

        self.last_activity = time.time()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        self.bind_all(
            "<Any-KeyPress>",
            self.update_activity
        )

        self.bind_all(
            "<Any-Button>",
            self.update_activity
        )

        self.after(
            1000,
            self.check_auto_lock
        )

        self.show_auth_screen()


    # =====================================================
    # HELPERS
    # =====================================================

    def clear_window(self):

        for widget in self.winfo_children():

            widget.destroy()


    def update_activity(self, event=None):

        self.last_activity = time.time()


    def encrypt(self, text):

        return self.fernet.encrypt(
            text.encode()
        )


    def decrypt(self, encrypted_data):

        return self.fernet.decrypt(
            encrypted_data
        ).decode()


    def copy_secure(self, value):

        pyperclip.copy(value)

        messagebox.showinfo(

            "Copied",

            f"Clipboard will clear in "
            f"{CLIPBOARD_CLEAR_SECONDS} seconds."

        )

        self.after(

            CLIPBOARD_CLEAR_SECONDS * 1000,

            self.clear_clipboard

        )


    def clear_clipboard(self):

        try:

            if pyperclip.paste():

                pyperclip.copy("")

        except Exception:

            pass


    # =====================================================
    # AUTHENTICATION
    # =====================================================

    def show_auth_screen(self):

        self.clear_window()

        self.fernet = None

        self.selected_id = None

        container = ctk.CTkFrame(

            self,

            width=460,

            height=530,

            corner_radius=20

        )

        container.place(

            relx=.5,

            rely=.5,

            anchor="center"

        )

        title = ctk.CTkLabel(

            container,

            text="🔐 SECUREVAULT PRO",

            font=ctk.CTkFont(

                size=30,

                weight="bold"

            )

        )

        title.pack(pady=(55, 10))


        subtitle = ctk.CTkLabel(

            container,

            text="Encrypted Password Manager",

            text_color="gray70",

            font=ctk.CTkFont(size=15)

        )

        subtitle.pack(pady=(0, 35))


        self.master_entry = ctk.CTkEntry(

            container,

            width=340,

            height=48,

            placeholder_text="Master Password",

            show="•"

        )

        self.master_entry.pack(pady=10)


        self.confirm_entry = None


        if not self.db.master_exists():

            self.confirm_entry = ctk.CTkEntry(

                container,

                width=340,

                height=48,

                placeholder_text="Confirm Master Password",

                show="•"

            )

            self.confirm_entry.pack(pady=10)


            button_text = "CREATE SECURE VAULT"

            command = self.setup_master

        else:

            button_text = "UNLOCK VAULT"

            command = self.login


        button = ctk.CTkButton(

            container,

            text=button_text,

            width=340,

            height=48,

            font=ctk.CTkFont(

                size=15,

                weight="bold"

            ),

            command=command

        )

        button.pack(pady=25)


        info = ctk.CTkLabel(

            container,

            text=(

                "AES-based authenticated encryption\n"

                "PBKDF2 key derivation • Local database"

            ),

            text_color="gray55"

        )

        info.pack()


        self.master_entry.bind(

            "<Return>",

            lambda event: command()

        )


    def setup_master(self):

        password = self.master_entry.get()

        confirm = self.confirm_entry.get()


        if len(password) < 10:

            messagebox.showwarning(

                "Weak Master Password",

                "Use at least 10 characters."

            )

            return


        if password != confirm:

            messagebox.showerror(

                "Error",

                "Passwords do not match."

            )

            return


        salt = os.urandom(16)

        key = SecurityManager.derive_key(

            password,

            salt

        )

        verifier = SecurityManager.create_verifier(key)


        self.db.create_master(

            salt,

            verifier

        )


        self.fernet = Fernet(key)


        messagebox.showinfo(

            "Vault Created",

            "Secure vault successfully created."

        )


        self.show_dashboard()


    def login(self):

        password = self.master_entry.get()


        if not password:

            return


        salt, stored_verifier = self.db.get_master()


        key = SecurityManager.derive_key(

            password,

            salt

        )


        if not SecurityManager.verify_master(

            key,

            stored_verifier

        ):

            messagebox.showerror(

                "Access Denied",

                "Incorrect Master Password"

            )

            self.master_entry.delete(0, "end")

            return


        self.fernet = Fernet(key)

        self.last_activity = time.time()

        self.show_dashboard()


    # =====================================================
    # DASHBOARD
    # =====================================================

    def show_dashboard(self):

        self.clear_window()

        self.selected_id = None


        self.grid_columnconfigure(

            1,

            weight=1

        )

        self.grid_rowconfigure(

            0,

            weight=1

        )


        # SIDEBAR

        sidebar = ctk.CTkFrame(

            self,

            width=230,

            corner_radius=0

        )

        sidebar.grid(

            row=0,

            column=0,

            sticky="nsew"

        )

        sidebar.grid_propagate(False)


        logo = ctk.CTkLabel(

            sidebar,

            text="🔐\nSECUREVAULT",

            font=ctk.CTkFont(

                size=23,

                weight="bold"

            )

        )

        logo.pack(

            pady=(40, 50)

        )


        add_button = ctk.CTkButton(

            sidebar,

            text="+ ADD CREDENTIAL",

            width=190,

            height=44,

            command=self.clear_form

        )

        add_button.pack(pady=10)


        refresh_button = ctk.CTkButton(

            sidebar,

            text="↻ REFRESH VAULT",

            width=190,

            height=44,

            command=self.load_credentials

        )

        refresh_button.pack(pady=10)


        lock_button = ctk.CTkButton(

            sidebar,

            text="🔒 LOCK VAULT",

            width=190,

            height=44,

            fg_color="#B3261E",

            hover_color="#8C1D18",

            command=self.lock_vault

        )

        lock_button.pack(

            side="bottom",

            pady=35

        )


        # MAIN CONTENT

        main = ctk.CTkFrame(

            self,

            fg_color="transparent"

        )

        main.grid(

            row=0,

            column=1,

            padx=25,

            pady=25,

            sticky="nsew"

        )

        main.grid_columnconfigure(

            0,

            weight=1

        )

        main.grid_rowconfigure(

            2,

            weight=1

        )


        header = ctk.CTkLabel(

            main,

            text="Password Security Dashboard",

            anchor="w",

            font=ctk.CTkFont(

                size=28,

                weight="bold"

            )

        )

        header.grid(

            row=0,

            column=0,

            sticky="ew",

            pady=(0, 15)

        )


        self.search_entry = ctk.CTkEntry(

            main,

            height=45,

            placeholder_text=(

                "Search decrypted service "

                "or username..."

            )

        )

        self.search_entry.grid(

            row=1,

            column=0,

            sticky="ew",

            pady=(0, 15)

        )

        self.search_entry.bind(

            "<KeyRelease>",

            lambda event: self.load_credentials()

        )


        content = ctk.CTkFrame(

            main,

            fg_color="transparent"

        )

        content.grid(

            row=2,

            column=0,

            sticky="nsew"

        )

        content.grid_columnconfigure(

            0,

            weight=2

        )

        content.grid_columnconfigure(

            1,

            weight=1

        )

        content.grid_rowconfigure(

            0,

            weight=1

        )


        # CREDENTIAL LIST

        self.list_frame = ctk.CTkScrollableFrame(

            content,

            label_text="ENCRYPTED CREDENTIALS"

        )

        self.list_frame.grid(

            row=0,

            column=0,

            padx=(0, 15),

            sticky="nsew"

        )


        # FORM PANEL

        form = ctk.CTkFrame(content)

        form.grid(

            row=0,

            column=1,

            sticky="nsew"

        )


        form_title = ctk.CTkLabel(

            form,

            text="Credential Editor",

            font=ctk.CTkFont(

                size=21,

                weight="bold"

            )

        )

        form_title.pack(

            pady=(25, 20)

        )


        self.service_entry = ctk.CTkEntry(

            form,

            width=300,

            height=42,

            placeholder_text="Service / Website"

        )

        self.service_entry.pack(pady=7)


        self.username_entry = ctk.CTkEntry(

            form,

            width=300,

            height=42,

            placeholder_text="Username / Email"

        )

        self.username_entry.pack(pady=7)


        password_row = ctk.CTkFrame(

            form,

            fg_color="transparent"

        )

        password_row.pack(pady=7)


        self.password_entry = ctk.CTkEntry(

            password_row,

            width=245,

            height=42,

            placeholder_text="Password",

            show="•"

        )

        self.password_entry.pack(

            side="left"

        )


        generate_button = ctk.CTkButton(

            password_row,

            text="⚡",

            width=48,

            height=42,

            command=self.generate_password

        )

        generate_button.pack(

            side="left",

            padx=(7, 0)

        )


        self.strength_label = ctk.CTkLabel(

            form,

            text="PASSWORD STRENGTH: --"

        )

        self.strength_label.pack(

            pady=(10, 3)

        )


        self.strength_bar = ctk.CTkProgressBar(

            form,

            width=300

        )

        self.strength_bar.set(0)

        self.strength_bar.pack()


        self.password_entry.bind(

            "<KeyRelease>",

            self.update_strength

        )


        self.notes_box = ctk.CTkTextbox(

            form,

            width=300,

            height=100

        )

        self.notes_box.pack(

            pady=15

        )

        self.notes_box.insert(

            "1.0",

            "Notes"

        )


        save_button = ctk.CTkButton(

            form,

            text="SAVE ENCRYPTED CREDENTIAL",

            width=300,

            height=45,

            command=self.save_credential

        )

        save_button.pack(pady=7)


        update_button = ctk.CTkButton(

            form,

            text="UPDATE CREDENTIAL",

            width=300,

            height=45,

            command=self.update_credential

        )

        update_button.pack(pady=7)


        delete_button = ctk.CTkButton(

            form,

            text="DELETE SELECTED",

            width=300,

            height=45,

            fg_color="#B3261E",

            hover_color="#8C1D18",

            command=self.delete_credential

        )

        delete_button.pack(pady=7)


        self.load_credentials()


    # =====================================================
    # PASSWORD GENERATOR
    # =====================================================

    def generate_password(self):

        alphabet = (

            string.ascii_letters

            + string.digits

            + "!@#$%^&*()-_=+"

        )


        while True:

            password = "".join(

                secrets.choice(alphabet)

                for _ in range(18)

            )


            if (

                re.search(r"[A-Z]", password)

                and re.search(r"[a-z]", password)

                and re.search(r"\d", password)

                and re.search(

                    r"[!@#$%^&*()\-_=+]",

                    password

                )

            ):

                break


        self.password_entry.delete(

            0,

            "end"

        )

        self.password_entry.insert(

            0,

            password

        )

        self.update_strength()


    def update_strength(self, event=None):

        password = self.password_entry.get()

        level, progress = SecurityManager.password_strength(

            password

        )

        self.strength_label.configure(

            text=f"PASSWORD STRENGTH: {level}"

        )

        self.strength_bar.set(progress)


    # =====================================================
    # CREDENTIAL OPERATIONS
    # =====================================================

    def clear_form(self):

        self.selected_id = None


        self.service_entry.delete(0, "end")

        self.username_entry.delete(0, "end")

        self.password_entry.delete(0, "end")

        self.notes_box.delete("1.0", "end")

        self.update_strength()


    def save_credential(self):

        service = self.service_entry.get().strip()

        username = self.username_entry.get().strip()

        password = self.password_entry.get()

        notes = self.notes_box.get(

            "1.0",

            "end"

        ).strip()


        if not service or not password:

            messagebox.showwarning(

                "Missing Data",

                "Service and password are required."

            )

            return


        self.db.add_credential(

            self.encrypt(service),

            self.encrypt(username),

            self.encrypt(password),

            self.encrypt(notes)

        )


        self.clear_form()

        self.load_credentials()


        messagebox.showinfo(

            "Encrypted",

            "Credential encrypted and stored."

        )


    def load_credentials(self):

        for widget in self.list_frame.winfo_children():

            widget.destroy()


        query = self.search_entry.get().lower().strip()


        for row in self.db.get_credentials():

            credential_id = row[0]


            try:

                service = self.decrypt(row[1])

                username = self.decrypt(row[2])

                password = self.decrypt(row[3])

                notes = self.decrypt(row[4])


            except InvalidToken:

                continue


            if query:

                searchable = (

                    service

                    + " "

                    + username

                ).lower()


                if query not in searchable:

                    continue


            card = ctk.CTkFrame(

                self.list_frame

            )

            card.pack(

                fill="x",

                padx=8,

                pady=6

            )


            info_frame = ctk.CTkFrame(

                card,

                fg_color="transparent"

            )

            info_frame.pack(

                side="left",

                fill="x",

                expand=True,

                padx=15,

                pady=12

            )


            service_label = ctk.CTkLabel(

                info_frame,

                text=service,

                anchor="w",

                font=ctk.CTkFont(

                    size=17,

                    weight="bold"

                )

            )

            service_label.pack(

                fill="x"

            )


            username_label = ctk.CTkLabel(

                info_frame,

                text=username,

                anchor="w",

                text_color="gray70"

            )

            username_label.pack(

                fill="x"

            )


            copy_user = ctk.CTkButton(

                card,

                text="USER",

                width=60,

                command=lambda value=username:

                self.copy_secure(value)

            )

            copy_user.pack(

                side="left",

                padx=3

            )


            copy_pass = ctk.CTkButton(

                card,

                text="PASS",

                width=60,

                command=lambda value=password:

                self.copy_secure(value)

            )

            copy_pass.pack(

                side="left",

                padx=3

            )


            edit_button = ctk.CTkButton(

                card,

                text="EDIT",

                width=60,

                command=lambda cid=credential_id,

                s=service,

                u=username,

                p=password,

                n=notes:

                self.select_credential(

                    cid,

                    s,

                    u,

                    p,

                    n

                )

            )

            edit_button.pack(

                side="left",

                padx=(3, 10)

            )


    def select_credential(

        self,

        credential_id,

        service,

        username,

        password,

        notes

    ):

        self.selected_id = credential_id


        self.service_entry.delete(0, "end")

        self.service_entry.insert(0, service)


        self.username_entry.delete(0, "end")

        self.username_entry.insert(0, username)


        self.password_entry.delete(0, "end")

        self.password_entry.insert(0, password)


        self.notes_box.delete("1.0", "end")

        self.notes_box.insert("1.0", notes)


        self.update_strength()


    def update_credential(self):

        if self.selected_id is None:

            messagebox.showwarning(

                "No Selection",

                "Select a credential first."

            )

            return


        service = self.service_entry.get().strip()

        username = self.username_entry.get().strip()

        password = self.password_entry.get()

        notes = self.notes_box.get(

            "1.0",

            "end"

        ).strip()


        if not service or not password:

            messagebox.showwarning(

                "Missing Data",

                "Service and password are required."

            )

            return


        self.db.update_credential(

            self.selected_id,

            self.encrypt(service),

            self.encrypt(username),

            self.encrypt(password),

            self.encrypt(notes)

        )


        self.clear_form()

        self.load_credentials()


        messagebox.showinfo(

            "Updated",

            "Encrypted credential updated."

        )


    def delete_credential(self):

        if self.selected_id is None:

            messagebox.showwarning(

                "No Selection",

                "Select a credential first."

            )

            return


        confirm = messagebox.askyesno(

            "Delete Credential",

            "Permanently delete selected credential?"

        )


        if confirm:

            self.db.delete_credential(

                self.selected_id

            )

            self.clear_form()

            self.load_credentials()


    # =====================================================
    # AUTO LOCK
    # =====================================================

    def check_auto_lock(self):

        if (

            self.fernet is not None

            and time.time() - self.last_activity

            >= AUTO_LOCK_SECONDS

        ):

            self.lock_vault()


        self.after(

            1000,

            self.check_auto_lock

        )


    def lock_vault(self):

        self.clear_clipboard()

        self.fernet = None

        self.selected_id = None

        self.show_auth_screen()


    # =====================================================
    # CLOSE
    # =====================================================

    def close_app(self):

        self.clear_clipboard()

        self.db.conn.close()

        self.destroy()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app = SecureVault()

    app.mainloop()