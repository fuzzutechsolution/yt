import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import random
from collections import Counter, defaultdict
from datetime import datetime


# ============================================================
# AI NEXT MOVE PREDICTOR
# FuzzuTech Project
# Single-file CustomTkinter Application
# ============================================================

APP_NAME = "AI NEXT MOVE PREDICTOR"
VERSION = "1.0"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class BehaviorEngine:
    """
    Lightweight behavioral-pattern prediction engine.

    It learns transition probabilities from the actions entered
    by the user and predicts the most likely next action.

    This is a simulation/demo of behavioral prediction,
    not genuine mind reading.
    """

    ACTIONS = [
        "Click",
        "Scroll",
        "Move Mouse",
        "Type",
        "Pause",
        "Go Back",
        "Open Menu",
        "Search",
    ]

    def __init__(self):
        self.reset()

    def reset(self):
        self.transitions = defaultdict(Counter)
        self.action_counts = Counter()
        self.sequence = []

        self.default_patterns = {
            "Click": {
                "Scroll": 0.26,
                "Move Mouse": 0.18,
                "Type": 0.16,
                "Pause": 0.12,
                "Open Menu": 0.10,
                "Go Back": 0.06,
                "Search": 0.08,
                "Click": 0.04,
            },
            "Scroll": {
                "Scroll": 0.30,
                "Move Mouse": 0.19,
                "Click": 0.18,
                "Pause": 0.12,
                "Type": 0.08,
                "Go Back": 0.06,
                "Search": 0.04,
                "Open Menu": 0.03,
            },
            "Move Mouse": {
                "Click": 0.24,
                "Scroll": 0.22,
                "Move Mouse": 0.20,
                "Pause": 0.14,
                "Type": 0.08,
                "Open Menu": 0.05,
                "Search": 0.04,
                "Go Back": 0.03,
            },
            "Type": {
                "Type": 0.34,
                "Click": 0.21,
                "Pause": 0.15,
                "Search": 0.12,
                "Move Mouse": 0.07,
                "Scroll": 0.05,
                "Go Back": 0.04,
                "Open Menu": 0.02,
            },
            "Pause": {
                "Click": 0.24,
                "Move Mouse": 0.19,
                "Scroll": 0.16,
                "Type": 0.13,
                "Search": 0.10,
                "Open Menu": 0.08,
                "Go Back": 0.06,
                "Pause": 0.04,
            },
            "Go Back": {
                "Scroll": 0.24,
                "Click": 0.18,
                "Move Mouse": 0.17,
                "Search": 0.15,
                "Pause": 0.10,
                "Open Menu": 0.08,
                "Type": 0.05,
                "Go Back": 0.03,
            },
            "Open Menu": {
                "Click": 0.28,
                "Move Mouse": 0.18,
                "Pause": 0.15,
                "Scroll": 0.13,
                "Search": 0.11,
                "Type": 0.07,
                "Go Back": 0.05,
                "Open Menu": 0.03,
            },
            "Search": {
                "Type": 0.31,
                "Click": 0.20,
                "Pause": 0.14,
                "Scroll": 0.12,
                "Move Mouse": 0.10,
                "Search": 0.06,
                "Open Menu": 0.04,
                "Go Back": 0.03,
            },
        }

    def add_action(self, action):
        if action not in self.ACTIONS:
            return

        if self.sequence:
            previous = self.sequence[-1]
            self.transitions[previous][action] += 1

        self.action_counts[action] += 1
        self.sequence.append(action)

        if len(self.sequence) > 100:
            self.sequence.pop(0)

    def predict(self, mode="Balanced"):
        if not self.sequence:
            return self._default_prediction()

        current = self.sequence[-1]

        learned = self.transitions.get(current, Counter())

        scores = {}

        for action in self.ACTIONS:
            learned_score = learned.get(action, 0)

            if learned:
                total = sum(learned.values())
                learned_probability = learned_score / total if total else 0
            else:
                learned_probability = 0

            default_probability = self.default_patterns.get(
                current, {}
            ).get(action, 1 / len(self.ACTIONS))

            frequency_total = sum(self.action_counts.values())

            frequency_probability = (
                self.action_counts.get(action, 0) / frequency_total
                if frequency_total
                else 0
            )

            if mode == "Pattern":
                score = (
                    learned_probability * 0.70
                    + default_probability * 0.30
                )

            elif mode == "Frequency":
                score = (
                    frequency_probability * 0.60
                    + default_probability * 0.40
                )

            else:
                score = (
                    learned_probability * 0.50
                    + default_probability * 0.35
                    + frequency_probability * 0.15
                )

            scores[action] = score

        # If insufficient learning data exists, use defaults.
        if not learned:
            scores = self.default_patterns.get(
                current,
                {a: 1 / len(self.ACTIONS) for a in self.ACTIONS}
            ).copy()

        # Normalize
        total_score = sum(scores.values())

        if total_score:
            scores = {
                action: value / total_score
                for action, value in scores.items()
            }

        ranked = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True
        )

        predicted_action, probability = ranked[0]

        # Make demo confidence visually meaningful.
        sample_factor = min(
            1.0,
            0.45 + (len(self.sequence) / 30)
        )

        confidence = probability * sample_factor

        if len(self.sequence) < 3:
            confidence = min(confidence, 0.56)

        return {
            "action": predicted_action,
            "confidence": confidence,
            "ranking": ranked[:5],
        }

    def _default_prediction(self):
        action = random.choice(self.ACTIONS)

        return {
            "action": action,
            "confidence": random.uniform(0.18, 0.32),
            "ranking": [(action, 0.25)],
        }


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} • {VERSION}")
        self.geometry("1250x780")
        self.minsize(900, 650)

        self.engine = BehaviorEngine()

        self.prediction_history = []
        self.demo_running = False
        self.demo_job = None

        self.mode = "Balanced"

        self.font_title = ctk.CTkFont(
            family="Arial",
            size=30,
            weight="bold"
        )

        self.font_heading = ctk.CTkFont(
            family="Arial",
            size=19,
            weight="bold"
        )

        self.font_body = ctk.CTkFont(
            family="Arial",
            size=14
        )

        self.font_small = ctk.CTkFont(
            family="Arial",
            size=12
        )

        self.font_big_number = ctk.CTkFont(
            family="Arial",
            size=34,
            weight="bold"
        )

        self.configure(fg_color="#080B12")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ========================================================
    # SIDEBAR
    # ========================================================

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color="#0D111A"
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        logo_frame.pack(
            fill="x",
            padx=22,
            pady=(25, 20)
        )

        ctk.CTkLabel(
            logo_frame,
            text="◉",
            font=ctk.CTkFont(size=35, weight="bold"),
            text_color="#4DA3FF"
        ).pack(side="left")

        title_box = ctk.CTkFrame(
            logo_frame,
            fg_color="transparent"
        )
        title_box.pack(side="left", padx=10)

        ctk.CTkLabel(
            title_box,
            text="FUZZUTECH",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="AI LAB",
            font=ctk.CTkFont(size=10),
            text_color="#68758A"
        ).pack(anchor="w")

        self.nav_buttons = {}

        nav_items = [
            ("⌂", "Dashboard"),
            ("◈", "Predictor"),
            ("◷", "History"),
            ("▣", "Analytics"),
        ]

        for icon, name in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {name}",
                anchor="w",
                height=45,
                corner_radius=10,
                fg_color="#151B26" if name == "Dashboard"
                else "transparent",
                hover_color="#192332",
                font=self.font_body,
                command=lambda n=name: self.navigate(n)
            )

            btn.pack(
                fill="x",
                padx=14,
                pady=4
            )

            self.nav_buttons[name] = btn

        ctk.CTkLabel(
            self.sidebar,
            text="ENGINE",
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            ),
            text_color="#5F6B7A"
        ).pack(
            anchor="w",
            padx=22,
            pady=(30, 8)
        )

        self.mode_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=[
                "Balanced",
                "Pattern",
                "Frequency"
            ],
            command=self.change_mode,
            height=40,
            corner_radius=10
        )

        self.mode_menu.set("Balanced")

        self.mode_menu.pack(
            fill="x",
            padx=14,
            pady=5
        )

        ctk.CTkLabel(
            self.sidebar,
            text="Prediction Mode",
            font=self.font_small,
            text_color="#788596"
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        bottom = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        bottom.pack(
            side="bottom",
            fill="x",
            padx=14,
            pady=18
        )

        ctk.CTkButton(
            bottom,
            text="↻  Reset Engine",
            height=40,
            fg_color="#151B26",
            hover_color="#222C3A",
            command=self.reset_engine
        ).pack(fill="x", pady=4)

        ctk.CTkButton(
            bottom,
            text="⇩  Export CSV",
            height=40,
            fg_color="#151B26",
            hover_color="#222C3A",
            command=self.export_csv
        ).pack(fill="x", pady=4)

        ctk.CTkLabel(
            bottom,
            text="v1.0 • Behavioral AI Demo",
            text_color="#4F5A6A",
            font=ctk.CTkFont(size=10)
        ).pack(pady=(12, 0))

    # ========================================================
    # MAIN AREA
    # ========================================================

    def create_main_area(self):

        self.main = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#080B12"
        )

        self.main.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(2, weight=1)

        # HEADER
        header = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(28, 12)
        )

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="AI Next Move Predictor",
            font=self.font_title
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            header,
            text="Behavioral pattern analysis • Real-time prediction engine",
            font=self.font_small,
            text_color="#778397"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=(4, 0)
        )

        self.status_badge = ctk.CTkLabel(
            header,
            text="●  ENGINE ONLINE",
            width=150,
            height=32,
            corner_radius=16,
            fg_color="#11291E",
            text_color="#63D391",
            font=ctk.CTkFont(size=11, weight="bold")
        )

        self.status_badge.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(20, 0)
        )

        # STATS
        stats = ctk.CTkFrame(
            self.main,
            fg_color="transparent"
        )

        stats.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=8
        )

        for i in range(4):
            stats.grid_columnconfigure(i, weight=1)

        self.total_value = self.create_stat_card(
            stats,
            0,
            "TOTAL ACTIONS",
            "0",
            "Observed behavior"
        )

        self.predictions_value = self.create_stat_card(
            stats,
            1,
            "PREDICTIONS",
            "0",
            "Generated predictions"
        )

        self.confidence_value = self.create_stat_card(
            stats,
            2,
            "AVG CONFIDENCE",
            "0%",
            "Prediction strength"
        )

        self.pattern_value = self.create_stat_card(
            stats,
            3,
            "TOP PATTERN",
            "—",
            "Most observed action"
        )

        # CONTENT
        self.content = ctk.CTkScrollableFrame(
            self.main,
            fg_color="transparent"
        )

        self.content.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(5, 20)
        )

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)

        self.create_predictor_card()
        self.create_prediction_card()
        self.create_history_card()
        self.create_analytics_card()

    # ========================================================
    # STAT CARD
    # ========================================================

    def create_stat_card(
        self,
        parent,
        column,
        title,
        value,
        subtitle
    ):

        card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color="#101620"
        )

        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=5
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            ),
            text_color="#687589"
        ).pack(
            anchor="w",
            padx=16,
            pady=(14, 2)
        )

        label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        )

        label.pack(
            anchor="w",
            padx=16
        )

        ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=10),
            text_color="#596678"
        ).pack(
            anchor="w",
            padx=16,
            pady=(0, 14)
        )

        return label

    # ========================================================
    # PREDICTOR INPUT CARD
    # ========================================================

    def create_predictor_card(self):

        card = ctk.CTkFrame(
            self.content,
            corner_radius=16,
            fg_color="#101620"
        )

        card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=7,
            pady=7
        )

        ctk.CTkLabel(
            card,
            text="Behavior Input",
            font=self.font_heading
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 3)
        )

        ctk.CTkLabel(
            card,
            text="Record what the user is doing",
            font=self.font_small,
            text_color="#718095"
        ).pack(
            anchor="w",
            padx=20
        )

        buttons_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        buttons_frame.pack(
            fill="x",
            padx=14,
            pady=15
        )

        for i in range(2):
            buttons_frame.grid_columnconfigure(i, weight=1)

        for index, action in enumerate(BehaviorEngine.ACTIONS):

            btn = ctk.CTkButton(
                buttons_frame,
                text=action,
                height=38,
                corner_radius=9,
                fg_color="#171F2B",
                hover_color="#243247",
                command=lambda a=action: self.record_action(a)
            )

            btn.grid(
                row=index // 2,
                column=index % 2,
                sticky="ew",
                padx=5,
                pady=4
            )

        demo_frame = ctk.CTkFrame(
            card,
            fg_color="#0B1018",
            corner_radius=10
        )

        demo_frame.pack(
            fill="x",
            padx=20,
            pady=(3, 20)
        )

        self.demo_button = ctk.CTkButton(
            demo_frame,
            text="▶  Run AI Simulation",
            height=42,
            corner_radius=9,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            command=self.toggle_demo
        )

        self.demo_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8,
            pady=8
        )

        ctk.CTkButton(
            demo_frame,
            text="Random Action",
            height=42,
            corner_radius=9,
            fg_color="#171F2B",
            hover_color="#243247",
            command=self.random_action
        ).pack(
            side="right",
            padx=8,
            pady=8
        )

    # ========================================================
    # PREDICTION CARD
    # ========================================================

    def create_prediction_card(self):

        card = ctk.CTkFrame(
            self.content,
            corner_radius=16,
            fg_color="#101620"
        )

        card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=7,
            pady=7
        )

        ctk.CTkLabel(
            card,
            text="Prediction",
            font=self.font_heading
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 3)
        )

        ctk.CTkLabel(
            card,
            text="Most probable next action",
            font=self.font_small,
            text_color="#718095"
        ).pack(
            anchor="w",
            padx=20
        )

        prediction_box = ctk.CTkFrame(
            card,
            fg_color="#0B1018",
            corner_radius=12
        )

        prediction_box.pack(
            fill="x",
            padx=20,
            pady=18
        )

        self.prediction_action = ctk.CTkLabel(
            prediction_box,
            text="WAITING",
            font=ctk.CTkFont(
                size=27,
                weight="bold"
            )
        )

        self.prediction_action.pack(
            pady=(20, 2)
        )

        self.prediction_subtitle = ctk.CTkLabel(
            prediction_box,
            text="Record behavior to generate a prediction",
            font=self.font_small,
            text_color="#687589"
        )

        self.prediction_subtitle.pack(
            pady=(0, 18)
        )

        self.confidence_bar = ctk.CTkProgressBar(
            card,
            height=9,
            corner_radius=5
        )

        self.confidence_bar.pack(
            fill="x",
            padx=20
        )

        self.confidence_bar.set(0)

        confidence_row = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        confidence_row.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            confidence_row,
            text="Confidence",
            font=self.font_small,
            text_color="#687589"
        ).pack(side="left")

        self.confidence_label = ctk.CTkLabel(
            confidence_row,
            text="0%",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            )
        )

        self.confidence_label.pack(side="right")

        self.ranking_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        self.ranking_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

    # ========================================================
    # HISTORY CARD
    # ========================================================

    def create_history_card(self):

        card = ctk.CTkFrame(
            self.content,
            corner_radius=16,
            fg_color="#101620"
        )

        card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=7,
            pady=7
        )

        ctk.CTkLabel(
            card,
            text="Behavior Timeline",
            font=self.font_heading
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 3)
        )

        ctk.CTkLabel(
            card,
            text="Latest observed actions",
            font=self.font_small,
            text_color="#718095"
        ).pack(
            anchor="w",
            padx=20
        )

        self.history_text = ctk.CTkTextbox(
            card,
            height=220,
            corner_radius=10,
            fg_color="#0B1018",
            border_width=0,
            font=ctk.CTkFont(
                family="Consolas",
                size=12
            )
        )

        self.history_text.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        self.history_text.insert(
            "1.0",
            "No behavior recorded yet.\n\n"
            "Use the action buttons above or run the simulation."
        )

        self.history_text.configure(
            state="disabled"
        )

    # ========================================================
    # ANALYTICS
    # ========================================================

    def create_analytics_card(self):

        card = ctk.CTkFrame(
            self.content,
            corner_radius=16,
            fg_color="#101620"
        )

        card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=7,
            pady=7
        )

        ctk.CTkLabel(
            card,
            text="Pattern Analytics",
            font=self.font_heading
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 3)
        )

        ctk.CTkLabel(
            card,
            text="Observed behavior distribution",
            font=self.font_small,
            text_color="#718095"
        ).pack(
            anchor="w",
            padx=20
        )

        self.analytics_frame = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )

        self.analytics_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        self.update_analytics()

    # ========================================================
    # ACTION RECORDING
    # ========================================================

    def record_action(self, action):

        self.engine.add_action(action)

        self.prediction_history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "action": action
        })

        if len(self.prediction_history) > 200:
            self.prediction_history.pop(0)

        self.generate_prediction()

        self.update_dashboard()

    def random_action(self):

        action = random.choice(
            BehaviorEngine.ACTIONS
        )

        self.record_action(action)

    # ========================================================
    # PREDICTION
    # ========================================================

    def generate_prediction(self):

        result = self.engine.predict(
            self.mode
        )

        action = result["action"]
        confidence = result["confidence"]

        percentage = round(
            confidence * 100
        )

        self.prediction_action.configure(
            text=action.upper()
        )

        self.prediction_subtitle.configure(
            text=f"Predicted from {len(self.engine.sequence)} observed actions"
        )

        self.confidence_bar.set(
            min(confidence, 1)
        )

        self.confidence_label.configure(
            text=f"{percentage}%"
        )

        # Ranking
        for widget in self.ranking_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.ranking_frame,
            text="ALTERNATIVE PREDICTIONS",
            font=ctk.CTkFont(
                size=10,
                weight="bold"
            ),
            text_color="#687589"
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        for rank, (name, score) in enumerate(
            result["ranking"][:4],
            start=1
        ):

            row = ctk.CTkFrame(
                self.ranking_frame,
                fg_color="#151C27",
                corner_radius=7
            )

            row.pack(
                fill="x",
                pady=3
            )

            ctk.CTkLabel(
                row,
                text=f"{rank}.  {name}",
                anchor="w",
                font=ctk.CTkFont(size=11)
            ).pack(
                side="left",
                padx=10,
                pady=7
            )

            ctk.CTkLabel(
                row,
                text=f"{round(score * 100)}%",
                font=ctk.CTkFont(
                    size=11,
                    weight="bold"
                ),
                text_color="#8CA7C7"
            ).pack(
                side="right",
                padx=10
            )

    # ========================================================
    # DEMO SIMULATION
    # ========================================================

    def toggle_demo(self):

        if self.demo_running:
            self.stop_demo()
        else:
            self.start_demo()

    def start_demo(self):

        self.demo_running = True

        self.demo_button.configure(
            text="■  Stop Simulation",
            fg_color="#9F2F3A",
            hover_color="#7F2430"
        )

        self.status_badge.configure(
            text="●  SIMULATION ACTIVE",
            fg_color="#2B2111",
            text_color="#F2C66D"
        )

        self.run_demo_step()

    def run_demo_step(self):

        if not self.demo_running:
            return

        if not self.engine.sequence:
            action = random.choice(
                BehaviorEngine.ACTIONS
            )
        else:

            current = self.engine.sequence[-1]

            pattern = self.engine.default_patterns.get(
                current,
                {}
            )

            if pattern:
                actions = list(pattern.keys())
                weights = list(pattern.values())

                action = random.choices(
                    actions,
                    weights=weights,
                    k=1
                )[0]
            else:
                action = random.choice(
                    BehaviorEngine.ACTIONS
                )

        self.record_action(action)

        self.demo_job = self.after(
            900,
            self.run_demo_step
        )

    def stop_demo(self):

        self.demo_running = False

        if self.demo_job:
            try:
                self.after_cancel(
                    self.demo_job
                )
            except Exception:
                pass

            self.demo_job = None

        self.demo_button.configure(
            text="▶  Run AI Simulation",
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        )

        self.status_badge.configure(
            text="●  ENGINE ONLINE",
            fg_color="#11291E",
            text_color="#63D391"
        )

    # ========================================================
    # DASHBOARD UPDATE
    # ========================================================

    def update_dashboard(self):

        total = len(
            self.engine.sequence
        )

        self.total_value.configure(
            text=str(total)
        )

        self.predictions_value.configure(
            text=str(len(self.prediction_history))
        )

        if self.prediction_history:

            confidences = []

            for _ in self.prediction_history:
                result = self.engine.predict(
                    self.mode
                )

                confidences.append(
                    result["confidence"]
                )

            avg = sum(confidences) / len(confidences)

            self.confidence_value.configure(
                text=f"{round(avg * 100)}%"
            )

        counts = self.engine.action_counts

        if counts:
            top = counts.most_common(1)[0][0]

            self.pattern_value.configure(
                text=top
            )
        else:
            self.pattern_value.configure(
                text="—"
            )

        self.update_history()
        self.update_analytics()

    # ========================================================
    # HISTORY
    # ========================================================

    def update_history(self):

        self.history_text.configure(
            state="normal"
        )

        self.history_text.delete(
            "1.0",
            "end"
        )

        if not self.prediction_history:

            self.history_text.insert(
                "1.0",
                "No behavior recorded yet.\n\n"
                "Use the action buttons above or run the simulation."
            )

        else:

            recent = self.prediction_history[-20:]

            for index, item in enumerate(
                reversed(recent),
                start=1
            ):

                self.history_text.insert(
                    "end",
                    f"{item['time']}   "
                    f"→   {item['action']}\n"
                )

        self.history_text.configure(
            state="disabled"
        )

    # ========================================================
    # ANALYTICS
    # ========================================================

    def update_analytics(self):

        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        counts = self.engine.action_counts

        if not counts:

            ctk.CTkLabel(
                self.analytics_frame,
                text="Waiting for behavioral data...",
                text_color="#647184",
                font=self.font_small
            ).pack(
                pady=30
            )

            return

        total = sum(counts.values())

        for action, count in counts.most_common():

            percentage = (
                count / total
            ) if total else 0

            row = ctk.CTkFrame(
                self.analytics_frame,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                pady=5
            )

            top = ctk.CTkFrame(
                row,
                fg_color="transparent"
            )

            top.pack(fill="x")

            ctk.CTkLabel(
                top,
                text=action,
                font=ctk.CTkFont(
                    size=11,
                    weight="bold"
                )
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=f"{count}  •  {round(percentage * 100)}%",
                font=ctk.CTkFont(
                    size=10
                ),
                text_color="#718095"
            ).pack(side="right")

            bar = ctk.CTkProgressBar(
                row,
                height=7,
                corner_radius=4
            )

            bar.pack(
                fill="x",
                pady=(4, 0)
            )

            bar.set(
                percentage
            )

    # ========================================================
    # MODE
    # ========================================================

    def change_mode(self, mode):

        self.mode = mode

        if self.engine.sequence:
            self.generate_prediction()

    # ========================================================
    # NAVIGATION
    # ========================================================

    def navigate(self, page):

        for name, btn in self.nav_buttons.items():

            if name == page:

                btn.configure(
                    fg_color="#151B26"
                )

            else:

                btn.configure(
                    fg_color="transparent"
                )

        # This is a single-page dashboard.
        # Navigation buttons act as quick scroll shortcuts.

        if page == "Dashboard":
            self.content._parent_canvas.yview_moveto(0)

        elif page == "Predictor":
            self.content._parent_canvas.yview_moveto(0)

        elif page == "History":
            self.content._parent_canvas.yview_moveto(0.48)

        elif page == "Analytics":
            self.content._parent_canvas.yview_moveto(0.75)

    # ========================================================
    # RESET
    # ========================================================

    def reset_engine(self):

        answer = messagebox.askyesno(
            "Reset AI Engine",
            "Clear all observed behavior and prediction history?"
        )

        if not answer:
            return

        self.stop_demo()

        self.engine.reset()

        self.prediction_history.clear()

        self.prediction_action.configure(
            text="WAITING"
        )

        self.prediction_subtitle.configure(
            text="Record behavior to generate a prediction"
        )

        self.confidence_bar.set(0)

        self.confidence_label.configure(
            text="0%"
        )

        self.update_dashboard()

    # ========================================================
    # EXPORT
    # ========================================================

    def export_csv(self):

        if not self.prediction_history:

            messagebox.showinfo(
                "Nothing to Export",
                "Record some behavior first."
            )

            return

        path = filedialog.asksaveasfilename(
            title="Export Prediction History",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )

        if not path:
            return

        try:

            with open(
                path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Timestamp",
                    "Observed Action"
                ])

                for item in self.prediction_history:

                    writer.writerow([
                        item["time"],
                        item["action"]
                    ])

            messagebox.showinfo(
                "Export Complete",
                "Behavior history exported successfully."
            )

        except Exception as error:

            messagebox.showerror(
                "Export Error",
                str(error)
            )

    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(self):

        self.stop_demo()

        self.destroy()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = App()

    app.mainloop()