import customtkinter as ctk
from tkinter import filedialog
import hashlib
import os
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FileIntegrityMonitor:

    def __init__(self, root):
        self.root = root
        self.root.title("Python File Integrity Monitor")
        self.root.geometry("900x600")

        self.files = {}
        self.running = False

        title = ctk.CTkLabel(
            root,
            text="🛡 File Integrity Monitor",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=20)

        btn_frame = ctk.CTkFrame(root)
        btn_frame.pack(fill="x", padx=20)

        ctk.CTkButton(
            btn_frame,
            text="Add File",
            command=self.add_file
        ).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="Start Monitoring",
            command=self.start_monitor
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Stop",
            fg_color="red",
            command=self.stop_monitor
        ).pack(side="left", padx=10)

        self.log = ctk.CTkTextbox(root)
        self.log.pack(fill="both", expand=True, padx=20, pady=20)

    def write(self, msg):
        self.log.insert("end", msg + "\n")
        self.log.see("end")

    def hash_file(self, path):
        sha = hashlib.sha256()

        try:
            with open(path, "rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    sha.update(chunk)

            return sha.hexdigest()

        except:
            return None

    def add_file(self):
        filename = filedialog.askopenfilename()

        if filename:
            h = self.hash_file(filename)

            if h:
                self.files[filename] = h
                self.write(f"Added: {filename}")

    def monitor(self):

        while self.running:

            for file in list(self.files.keys()):

                if not os.path.exists(file):
                    self.write(f"❌ Deleted : {file}")
                    continue

                new_hash = self.hash_file(file)

                if new_hash != self.files[file]:
                    self.write(f"⚠ Modified : {file}")
                    self.files[file] = new_hash

            time.sleep(2)

    def start_monitor(self):

        if self.running:
            return

        self.running = True

        threading.Thread(
            target=self.monitor,
            daemon=True
        ).start()

        self.write("Monitoring Started...")

    def stop_monitor(self):
        self.running = False
        self.write("Monitoring Stopped.")

root = ctk.CTk()
FileIntegrityMonitor(root)
root.mainloop()