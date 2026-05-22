import os

import json

import datetime

import time

import psutil

import win32gui

import win32process

import win32api

import threading

import queue

import customtkinter as ctk

import sys

from tkinter import messagebox



# ====================================================================

# LOGGER LOGIC

# ====================================================================

LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)



def get_today_log_path():

    """Returns the JSON file path for today's logs."""

    today_str = datetime.date.today().strftime("%Y-%m-%d")

    return os.path.join(LOG_DIR, f"{today_str}.json")



def load_logs():

    """Loads existing logs for today, or returns an empty dictionary."""

    path = get_today_log_path()

    if os.path.exists(path):

        try:

            with open(path, "r", encoding="utf-8") as f:

                return json.load(f)

        except Exception as e:

            print(f"Error loading logs: {e}")

            return {}

    return {}



def save_logs(data):

    """Saves the tracking data to today's JSON log file."""

    path = get_today_log_path()

    try:

        with open(path, "w", encoding="utf-8") as f:

            json.dump(data, f, indent=4)

    except Exception as e:

        print(f"Error saving logs: {e}")





# ====================================================================

# TRACKER LOGIC

# ====================================================================

IDLE_THRESHOLD = 60  # seconds



class UsageTracker:

    def __init__(self):

        # Load any existing data for today

        self.app_data = load_logs()

        

        # State variables

        self.active_window = "Unknown"

        self.active_app = "Unknown"

        self.current_app_time = 0

        self.total_screen_time = sum(app.get("time", 0) for app in self.app_data.values())

        self.total_idle_time = 0

        

        self.is_idle = False

        self.running = False

        

        # Thread safety

        self.lock = threading.Lock()

        self.alert_queue = queue.Queue()

        

        # Focus alert tracking variables

        self.last_app = None

        self.current_session_time = 0



    def get_active_window_info(self):

        """Retrieves the foreground window title and process name."""

        try:

            hwnd = win32gui.GetForegroundWindow()

            if not hwnd:

                return "Unknown", "Unknown"

                

            title = win32gui.GetWindowText(hwnd)

            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            if pid > 0:

                process = psutil.Process(pid)

                app_name = process.name()

                return title, app_name

        except Exception:

            pass

        return "Unknown", "Unknown"



    def get_idle_time(self):

        """Calculates how long the system has been idle (no keyboard/mouse input)."""

        try:

            last_input = win32api.GetLastInputInfo()

            current_tick = win32api.GetTickCount()

            return (current_tick - last_input) / 1000.0

        except Exception:

            return 0



    def track(self):

        """Main tracking loop running on a background thread."""

        self.running = True

        last_time = time.time()

        

        while self.running:

            current_time = time.time()

            elapsed = current_time - last_time

            last_time = current_time



            idle_time = self.get_idle_time()

            

            with self.lock:

                if idle_time > IDLE_THRESHOLD:

                    self.is_idle = True

                    self.active_window = "SYSTEM IDLE"

                    self.total_idle_time += elapsed

                else:

                    self.is_idle = False

                    win_title, app_name = self.get_active_window_info()

                    self.active_window = win_title

                    self.active_app = app_name

                    

                    if not app_name:

                        app_name = "Unknown"

                        

                    if app_name not in self.app_data:

                        self.app_data[app_name] = {"time": 0, "title": win_title}

                    else:

                        self.app_data[app_name]["title"] = win_title

                    

                    self.app_data[app_name]["time"] += elapsed

                    self.total_screen_time += elapsed

                    self.current_app_time = self.app_data[app_name]["time"]

                    

                    if self.last_app == app_name:

                        self.current_session_time += elapsed

                    else:

                        self.last_app = app_name

                        self.current_session_time = 0

                        

            if self.current_session_time >= 2700:

                self.alert_queue.put(self.active_app)

                self.current_session_time = 0 

                

            if int(current_time) % 10 == 0:

                with self.lock:

                    save_logs(self.app_data)

            

            time.sleep(1)

            

    def stop(self):

        self.running = False

        with self.lock:

            save_logs(self.app_data)

        

    def get_ui_data(self):

        with self.lock:

            sorted_apps = sorted(self.app_data.items(), key=lambda x: x[1]["time"], reverse=True)

            top_5 = sorted_apps[:5]

            

            return {

                "active_window": self.active_window,

                "active_app": self.active_app,

                "current_app_time": self.current_app_time,

                "total_screen_time": self.total_screen_time,

                "total_idle_time": self.total_idle_time,

                "is_idle": self.is_idle,

                "top_5": top_5

            }





# ====================================================================

# UI LOGIC

# ====================================================================

BG_COLOR = "#0D0D11"

PANEL_COLOR = "#1A1A24"

CYAN = "#00FFFF"

PURPLE = "#B026FF"

RED = "#FF003C"

GREEN = "#00FF66"

TEXT_COLOR = "#FFFFFF"



ctk.set_appearance_mode("dark")



class FuzzuSentinelUI(ctk.CTk):

    def __init__(self, tracker):

        super().__init__()

        self.tracker = tracker

        self.start_time = time.time()

        

        self.title("Fuzzu PC Sentinel – Advanced Usage Monitor 2026")

        self.geometry("850x650")

        self.configure(fg_color=BG_COLOR)

        

        self.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(1, weight=1)

        

        self.setup_ui()

        self.update_ui()

        

    def setup_ui(self):

        self.header = ctk.CTkLabel(self, text="FUZZU PC SENTINEL", font=("Courier New", 36, "bold"), text_color=CYAN)

        self.header.grid(row=0, column=0, columnspan=2, pady=(25, 5))

        

        self.sub_header = ctk.CTkLabel(self, text="[ ADVANCED USAGE MONITOR 2026 ]", font=("Courier New", 14), text_color=PURPLE)

        self.sub_header.grid(row=1, column=0, columnspan=2, pady=(0, 25))

        

        self.clock_var = ctk.StringVar(value="00:00:00")

        self.clock_label = ctk.CTkLabel(self, textvariable=self.clock_var, font=("Courier New", 28, "bold"), text_color=TEXT_COLOR)

        self.clock_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))

        

        self.active_panel = ctk.CTkFrame(self, fg_color=PANEL_COLOR, border_width=2, border_color=CYAN, corner_radius=10)

        self.active_panel.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

        

        ctk.CTkLabel(self.active_panel, text="LIVE ACTIVE WINDOW", font=("Courier New", 16, "bold"), text_color=CYAN).pack(pady=(15, 5))

        

        self.active_win_var = ctk.StringVar(value="Initializing Sensors...")

        self.active_win_label = ctk.CTkLabel(self.active_panel, textvariable=self.active_win_var, font=("Courier New", 14), text_color=TEXT_COLOR, wraplength=350)

        self.active_win_label.pack(pady=10, padx=15)

        

        self.idle_var = ctk.StringVar(value="STATUS: ACTIVE")

        self.idle_label = ctk.CTkLabel(self.active_panel, textvariable=self.idle_var, font=("Courier New", 16, "bold"), text_color=GREEN)

        self.idle_label.pack(pady=(10, 15))



        self.time_panel = ctk.CTkFrame(self, fg_color=PANEL_COLOR, border_width=2, border_color=PURPLE, corner_radius=10)

        self.time_panel.grid(row=3, column=1, padx=20, pady=10, sticky="nsew")

        

        ctk.CTkLabel(self.time_panel, text="TIME ANALYTICS", font=("Courier New", 16, "bold"), text_color=PURPLE).pack(pady=(15, 5))

        

        self.app_time_var = ctk.StringVar(value="Current App: 00:00:00")

        ctk.CTkLabel(self.time_panel, textvariable=self.app_time_var, font=("Courier New", 14), text_color=TEXT_COLOR).pack(pady=8)

        

        self.total_time_var = ctk.StringVar(value="Active Today: 00:00:00")

        ctk.CTkLabel(self.time_panel, textvariable=self.total_time_var, font=("Courier New", 14), text_color=TEXT_COLOR).pack(pady=8)

        

        self.idle_time_var = ctk.StringVar(value="Idle Today: 00:00:00")

        ctk.CTkLabel(self.time_panel, textvariable=self.idle_time_var, font=("Courier New", 14), text_color=TEXT_COLOR).pack(pady=8)

        

        self.session_time_var = ctk.StringVar(value="Live Session: 00:00:00")

        ctk.CTkLabel(self.time_panel, textvariable=self.session_time_var, font=("Courier New", 14), text_color=TEXT_COLOR).pack(pady=8)



        self.top_panel = ctk.CTkFrame(self, fg_color=PANEL_COLOR, border_width=2, border_color=CYAN, corner_radius=10)

        self.top_panel.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        

        ctk.CTkLabel(self.top_panel, text="TOP 5 TARGETS (TODAY)", font=("Courier New", 16, "bold"), text_color=CYAN).pack(pady=(15, 5))

        

        self.top_apps_labels = []

        for _ in range(5):

            lbl = ctk.CTkLabel(self.top_panel, text="", font=("Courier New", 14), text_color=TEXT_COLOR)

            lbl.pack(pady=4)

            self.top_apps_labels.append(lbl)



    def format_time(self, seconds):

        m, s = divmod(int(seconds), 60)

        h, m = divmod(m, 60)

        return f"{h:02d}:{m:02d}:{s:02d}"



    def update_ui(self):

        while not self.tracker.alert_queue.empty():

            app = self.tracker.alert_queue.get()

            self.show_focus_alert(app)

            

        current_time_str = time.strftime("%H:%M:%S")

        self.clock_var.set(f"SYS.TIME // {current_time_str}")

        

        data = self.tracker.get_ui_data()

        

        if data["is_idle"]:

            self.active_win_var.set("[ SYSTEM STANDBY ]")

            self.idle_var.set("STATUS: IDLE")

            self.idle_label.configure(text_color=RED)

            self.active_panel.configure(border_color=RED)

        else:

            self.active_win_var.set(f"App: [{data['active_app']}]\nTitle: {data['active_window']}")

            self.idle_var.set("STATUS: ACTIVE")

            self.idle_label.configure(text_color=GREEN)

            self.active_panel.configure(border_color=CYAN)

            

        self.app_time_var.set(f"Current App: {self.format_time(data['current_app_time'])}")

        self.total_time_var.set(f"Active Today: {self.format_time(data['total_screen_time'])}")

        self.idle_time_var.set(f"Idle Today: {self.format_time(data['total_idle_time'])}")

        

        session_time = time.time() - self.start_time

        self.session_time_var.set(f"Live Session: {self.format_time(session_time)}")

        

        top_5 = data["top_5"]

        for i, lbl in enumerate(self.top_apps_labels):

            if i < len(top_5):

                app_name, app_info = top_5[i]

                time_str = self.format_time(app_info["time"])

                lbl.configure(text=f"{(i+1):02d}. {app_name:<20} | {time_str}")

            else:

                lbl.configure(text="")

                

        self.after(1000, self.update_ui)

        

    def show_focus_alert(self, app_name):

        self.attributes('-topmost', 1)

        messagebox.showwarning("FOCUS ALERT ⚠️", f"⚠ Bro 45 minutes ho gaye. Focus karo.\n\n(Distracting App: {app_name})")

        self.attributes('-topmost', 0)



# ====================================================================

# MAIN BLOCK

# ====================================================================

def main():

    tracker = UsageTracker()

    

    t = threading.Thread(target=tracker.track, daemon=True)

    t.start()

    

    app = FuzzuSentinelUI(tracker)

    

    def on_closing():

        tracker.stop()

        app.destroy()

        

    app.protocol("WM_DELETE_WINDOW", on_closing)

    app.mainloop()



if __name__ == "__main__":

    main()

