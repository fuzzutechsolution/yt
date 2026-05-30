import customtkinter as ctk
import subprocess
import threading
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WiFiPasswordViewer(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("FuzzuTech WiFi Password Viewer")
        self.geometry("450x550")
        self.resizable(False, False)

        title = ctk.CTkLabel(
            self,
            text="📶 WiFi Password Viewer",
            font=("Arial", 30, "bold")
        )
        title.pack(pady=20)

        subtitle = ctk.CTkLabel(
            self,
            text="View Saved WiFi Passwords",
            font=("Arial", 16)
        )
        subtitle.pack()

        self.scan_btn = ctk.CTkButton(
            self,
            text="🔍 Scan WiFi Passwords",
            width=250,
            height=45,
            command=self.start_scan
        )
        self.scan_btn.pack(pady=20)

        self.textbox = ctk.CTkTextbox(
            self,
            width=800,
            height=380,
            font=("Consolas", 14)
        )
        self.textbox.pack(pady=10)

        footer = ctk.CTkLabel(
            self,
            text="Developed by FuzzuTech",
            font=("Arial", 12)
        )
        footer.pack(pady=10)

    def start_scan(self):
        self.scan_btn.configure(state="disabled")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", "Scanning saved WiFi profiles...\n\n")

        threading.Thread(
            target=self.scan_wifi,
            daemon=True
        ).start()

    def scan_wifi(self):

        try:

            profiles_data = subprocess.check_output(
                "netsh wlan show profiles",
                shell=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            profiles = []

            for line in profiles_data.split("\n"):
                if "All User Profile" in line:
                    profile = line.split(":")[1].strip()
                    profiles.append(profile)

            if not profiles:
                self.textbox.insert(
                    "end",
                    "No saved WiFi profiles found."
                )
                self.scan_btn.configure(state="normal")
                return

            for wifi in profiles:

                try:
                    result = subprocess.check_output(
                        f'netsh wlan show profile name="{wifi}" key=clear',
                        shell=True,
                        text=True,
                        encoding="utf-8",
                        errors="ignore"
                    )

                    password = "No Password"

                    for line in result.split("\n"):
                        if "Key Content" in line:
                            password = line.split(":")[1].strip()

                    output = (
                        f"📡 WiFi Name : {wifi}\n"
                        f"🔑 Password  : {password}\n"
                        f"{'-'*50}\n"
                    )

                    self.textbox.insert("end", output)

                except:
                    pass

        except Exception as e:
            messagebox.showerror(
                "Error",
                str(e)
            )

        self.scan_btn.configure(state="normal")


if __name__ == "__main__":
    app = WiFiPasswordViewer()
    app.mainloop()