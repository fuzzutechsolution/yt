import os
import shutil
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

EXTENSIONS = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".ico", ".svg"],
    "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Music": [".mp3", ".wav", ".aac", ".flac", ".ogg"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Programs": [".exe", ".msi"],
    "Code": [".py", ".cpp", ".c", ".java", ".html", ".css", ".js", ".php", ".json", ".xml"],
    "Fonts": [".ttf", ".otf"],
}

IGNORE_FILES = ["desktop.ini", "Thumbs.db", ".DS_Store"]


class OrganizerApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Python Auto File Organizer")
        self.geometry("850x650")

        self.folder = ""

        title = ctk.CTkLabel(
            self,
            text="📂 Python Auto File Organizer",
            font=("Arial", 26, "bold")
        )
        title.pack(pady=15)

        self.path_var = ctk.StringVar()

        path_frame = ctk.CTkFrame(self)
        path_frame.pack(fill="x", padx=20)

        self.entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.path_var,
            height=40
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        browse_btn = ctk.CTkButton(
            path_frame,
            text="Browse Folder",
            command=self.browse
        )
        browse_btn.pack(side="right", padx=10)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0)

        self.status = ctk.CTkLabel(
            self,
            text="Moved: 0 | Skipped: 0 | Errors: 0"
        )
        self.status.pack()

        self.organize_btn = ctk.CTkButton(
            self,
            text="🚀 ORGANIZE NOW",
            height=45,
            command=self.start
        )
        self.organize_btn.pack(pady=15)

        self.log = ScrolledText(
            self,
            height=20,
            bg="#202020",
            fg="white",
            insertbackground="white"
        )
        self.log.pack(fill="both", expand=True, padx=20, pady=15)

    def browse(self):
        folder = filedialog.askdirectory()

        if folder:
            self.folder = folder
            self.path_var.set(folder)

    def start(self):

        if not self.folder:
            self.log.insert("end", "Select folder first.\n")
            return

        threading.Thread(target=self.organize, daemon=True).start()

    def organize(self):

        files = [
            f for f in os.listdir(self.folder)
            if os.path.isfile(os.path.join(self.folder, f))
        ]

        total = len(files)

        moved = 0
        skipped = 0
        errors = 0

        if total == 0:
            self.log.insert("end", "Folder is empty.\n")
            return

        for i, file in enumerate(files):

            if file in IGNORE_FILES:
                skipped += 1
                continue

            try:

                ext = Path(file).suffix.lower()

                folder_name = "Others"

                for category, extensions in EXTENSIONS.items():
                    if ext in extensions:
                        folder_name = category
                        break

                destination_folder = os.path.join(self.folder, folder_name)

                os.makedirs(destination_folder, exist_ok=True)

                src = os.path.join(self.folder, file)

                dst = os.path.join(destination_folder, file)

                if os.path.exists(dst):

                    name = Path(file).stem
                    extension = Path(file).suffix

                    counter = 1

                    while True:

                        new_name = f"{name} ({counter}){extension}"

                        new_path = os.path.join(destination_folder, new_name)

                        if not os.path.exists(new_path):
                            dst = new_path
                            break

                        counter += 1

                shutil.move(src, dst)

                moved += 1

                self.log.insert(
                    "end",
                    f"✔ {file}  ➜  {folder_name}\n"
                )

            except Exception as e:

                errors += 1

                self.log.insert(
                    "end",
                    f"❌ {file} : {e}\n"
                )

            self.progress.set((i + 1) / total)

            self.status.configure(
                text=f"Moved: {moved} | Skipped: {skipped} | Errors: {errors}"
            )

            self.update_idletasks()

        self.log.insert(
            "end",
            "\n🎉 Organization Complete!\n"
        )


if __name__ == "__main__":
    app = OrganizerApp()
    app.mainloop()