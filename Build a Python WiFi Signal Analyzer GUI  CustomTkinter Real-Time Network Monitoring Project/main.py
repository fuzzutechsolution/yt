import customtkinter as ctk
from tkinter import messagebox, filedialog
import subprocess
import threading
import time
import re
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WiFiAnalyzer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WiFi Signal Analyzer Pro - FuzzuTech")
        self.geometry("700x650")
        self.resizable(False, False)

        self.running = True
        self.logs = []

        title = ctk.CTkLabel(self,text="📶 WiFi Signal Analyzer Pro",
                             font=("Segoe UI",28,"bold"))
        title.pack(pady=15)

        self.ssid = ctk.CTkLabel(self,text="SSID : -",font=("Segoe UI",18))
        self.ssid.pack()

        self.signal = ctk.CTkLabel(self,text="Signal : -",font=("Segoe UI",18))
        self.signal.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self,width=500)
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.status = ctk.CTkLabel(self,text="Status : Unknown",
                                   font=("Segoe UI",18,"bold"))
        self.status.pack()

        self.channel = ctk.CTkLabel(self,text="Channel : -")
        self.channel.pack()

        self.radio = ctk.CTkLabel(self,text="Radio : -")
        self.radio.pack()

        self.logbox = ctk.CTkTextbox(self,width=650,height=280)
        self.logbox.pack(pady=15)

        btnframe = ctk.CTkFrame(self)
        btnframe.pack(pady=5)

        ctk.CTkButton(btnframe,text="Export Report",
                      command=self.export).grid(row=0,column=0,padx=10)

        ctk.CTkButton(btnframe,text="Refresh Now",
                      command=self.refresh).grid(row=0,column=1,padx=10)

        self.protocol("WM_DELETE_WINDOW",self.close)

        threading.Thread(target=self.loop,daemon=True).start()

    def run_netsh(self):
        try:
            out = subprocess.check_output(
                ["netsh","wlan","show","interfaces"],
                text=True,
                encoding="utf-8",
                errors="ignore"
            )
            return out
        except Exception:
            return ""

    def parse(self,data):
        def find(pattern):
            m = re.search(pattern,data)
            return m.group(1).strip() if m else "-"
        ssid = find(r"^\s*SSID\s*:\s*(.+)$")
        signal = find(r"^\s*Signal\s*:\s*(.+)$")
        radio = find(r"^\s*Radio type\s*:\s*(.+)$")
        channel = find(r"^\s*Channel\s*:\s*(.+)$")
        return ssid,signal,radio,channel

    def refresh(self):
        data = self.run_netsh()
        if not data:
            messagebox.showerror("Error","No WiFi adapter detected or Windows only.")
            return

        ssid,signal,radio,channel = self.parse(data)

        self.ssid.configure(text=f"SSID : {ssid}")
        self.signal.configure(text=f"Signal : {signal}")
        self.radio.configure(text=f"Radio : {radio}")
        self.channel.configure(text=f"Channel : {channel}")

        value = 0
        m = re.search(r"(\d+)",signal)
        if m:
            value = int(m.group(1))

        self.progress.set(value/100)

        if value >= 80:
            status="🟢 Excellent"
        elif value >= 60:
            status="🟡 Good"
        elif value >= 40:
            status="🟠 Weak"
        else:
            status="🔴 Very Weak"

        self.status.configure(text=f"Status : {status}")

        log=f"[{datetime.now().strftime('%H:%M:%S')}] {ssid} | {signal} | {status}"
        self.logs.append(log)
        self.logbox.insert("end",log+"\n")
        self.logbox.see("end")

    def loop(self):
        while self.running:
            self.after(0,self.refresh)
            time.sleep(2)

    def export(self):
        path=filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text","*.txt")]
        )
        if not path:
            return
        with open(path,"w",encoding="utf-8") as f:
            f.write("WiFi Signal Analyzer Report\n")
            f.write("="*40+"\n")
            f.write("\n".join(self.logs))
        messagebox.showinfo("Done","Report exported successfully.")

    def close(self):
        self.running=False
        self.destroy()

if __name__=="__main__":
    app=WiFiAnalyzer()
    app.mainloop()
