import customtkinter as ctk
import hashlib
import math
import re
import secrets
import string


# ============================================================
# APPLICATION SETTINGS
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# PASSWORD DATABASE
# ============================================================

COMMON_PASSWORDS = {
    "password",
    "password123",
    "123456",
    "12345678",
    "123456789",
    "1234567890",
    "qwerty",
    "qwerty123",
    "admin",
    "admin123",
    "letmein",
    "welcome",
    "iloveyou",
    "abc123",
    "000000",
    "111111",
}


# ============================================================
# PASSWORD ANALYSIS FUNCTIONS
# ============================================================

def calculate_entropy(password):

    charset_size = 0

    if re.search(r"[a-z]", password):
        charset_size += 26

    if re.search(r"[A-Z]", password):
        charset_size += 26

    if re.search(r"\d", password):
        charset_size += 10

    if re.search(r"[^A-Za-z0-9]", password):
        charset_size += 32

    if charset_size == 0:
        return 0.0

    return len(password) * math.log2(charset_size)


def calculate_score(password):

    if not password:
        return 0

    score = 0

    length = len(password)

    # LENGTH SCORE

    if length >= 6:
        score += 5

    if length >= 8:
        score += 10

    if length >= 12:
        score += 15

    if length >= 16:
        score += 15

    # CHARACTER DIVERSITY

    if re.search(r"[a-z]", password):
        score += 10

    if re.search(r"[A-Z]", password):
        score += 10

    if re.search(r"\d", password):
        score += 10

    if re.search(r"[^A-Za-z0-9]", password):
        score += 15

    # SECURITY PENALTIES

    lower_password = password.lower()

    if lower_password in COMMON_PASSWORDS:
        score -= 60

    if re.search(r"(.)\1\1", password):
        score -= 10

    if re.search(
        r"1234|2345|3456|4567|5678|6789|"
        r"abcd|bcde|cdef|qwerty",
        lower_password,
    ):
        score -= 15

    return max(0, min(100, score))


def calculate_crack_time(entropy):

    # Assumed offline attack speed:
    # 10 billion guesses / second.

    guesses_per_second = 10_000_000_000

    if entropy <= 0:
        return "INSTANTLY"

    # Average search requires approximately half keyspace.

    log2_seconds = entropy - 1 - math.log2(guesses_per_second)

    if log2_seconds < 0:
        return "LESS THAN 1 SECOND"

    log2_minute = math.log2(60)
    log2_hour = math.log2(3600)
    log2_day = math.log2(86400)
    log2_year = math.log2(31_536_000)

    if log2_seconds < log2_minute:
        seconds = 2 ** log2_seconds
        return f"{seconds:.1f} SECONDS"

    if log2_seconds < log2_hour:
        minutes = 2 ** (log2_seconds - log2_minute)
        return f"{minutes:.1f} MINUTES"

    if log2_seconds < log2_day:
        hours = 2 ** (log2_seconds - log2_hour)
        return f"{hours:.1f} HOURS"

    if log2_seconds < log2_year:
        days = 2 ** (log2_seconds - log2_day)
        return f"{days:.1f} DAYS"

    log2_years = log2_seconds - log2_year

    if log2_years < math.log2(1_000):
        years = 2 ** log2_years
        return f"{years:.1f} YEARS"

    if log2_years < math.log2(1_000_000):
        thousand_years = 2 ** (
            log2_years - math.log2(1_000)
        )
        return f"{thousand_years:.1f} THOUSAND YEARS"

    if log2_years < math.log2(1_000_000_000):
        million_years = 2 ** (
            log2_years - math.log2(1_000_000)
        )
        return f"{million_years:.1f} MILLION YEARS"

    billion_years = 2 ** (
        log2_years - math.log2(1_000_000_000)
    )

    if billion_years < 1_000_000:
        return f"{billion_years:.1f} BILLION YEARS"

    return "PRACTICALLY UNCRACKABLE"


def generate_password(length=18):

    # Ensure generated password contains every important category.

    password_chars = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()_+-="),
    ]

    alphabet = (
        string.ascii_lowercase
        + string.ascii_uppercase
        + string.digits
        + "!@#$%^&*()_+-="
    )

    password_chars.extend(
        secrets.choice(alphabet)
        for _ in range(length - 4)
    )

    # Cryptographically secure shuffle.

    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


# ============================================================
# MAIN APPLICATION
# ============================================================

class PasswordScanner(ctk.CTk):

    WINDOW_WIDTH = 540
    WINDOW_HEIGHT = 960

    def __init__(self):

        super().__init__()

        self.title("Password Strength AI Scanner")

        self.geometry(
            f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}"
        )

        self.minsize(
            self.WINDOW_WIDTH,
            self.WINDOW_HEIGHT,
        )

        self.maxsize(
            self.WINDOW_WIDTH,
            self.WINDOW_HEIGHT,
        )

        self.configure(fg_color="#030712")

        self.password_visible = False

        self.scan_job = None

        self.scan_progress = 0

        self.current_password = ""

        self.create_ui()

        self.password_entry.focus_set()


    # ========================================================
    # CREATE UI
    # ========================================================

    def create_ui(self):

        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(
            self,
            height=65,
            corner_radius=0,
            fg_color="#08101f",
        )

        header.pack(fill="x")

        header.pack_propagate(False)


        ctk.CTkLabel(
            header,
            text="🛡  FUZZUTECH SECURITY LAB",
            font=ctk.CTkFont(
                size=19,
                weight="bold",
            ),
            text_color="#00d9ff",
        ).pack(
            pady=(10, 0)
        )


        ctk.CTkLabel(
            header,
            text="● AI SECURITY ENGINE ONLINE",
            font=ctk.CTkFont(
                size=9,
                weight="bold",
            ),
            text_color="#35ff8a",
        ).pack(
            pady=(0, 7)
        )


        # ====================================================
        # MAIN CONTENT
        # ====================================================

        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        container.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(12, 14),
        )


        # ====================================================
        # TITLE
        # ====================================================

        ctk.CTkLabel(
            container,
            text="PASSWORD STRENGTH",
            font=ctk.CTkFont(
                size=25,
                weight="bold",
            ),
            text_color="#ffffff",
        ).pack()


        ctk.CTkLabel(
            container,
            text="AI SCANNER",
            font=ctk.CTkFont(
                size=25,
                weight="bold",
            ),
            text_color="#00d9ff",
        ).pack()


        ctk.CTkLabel(
            container,
            text="Analyze Security • Entropy • Crack Resistance",
            font=ctk.CTkFont(size=10),
            text_color="#7f8da8",
        ).pack(
            pady=(2, 10)
        )


        # ====================================================
        # INPUT CARD
        # ====================================================

        input_card = ctk.CTkFrame(
            container,
            fg_color="#0b1425",
            corner_radius=15,
        )

        input_card.pack(
            fill="x",
            pady=(0, 10),
        )


        self.password_entry = ctk.CTkEntry(
            input_card,
            height=45,
            placeholder_text="Enter password to scan...",
            font=ctk.CTkFont(size=14),
            show="●",
            fg_color="#030712",
            border_color="#1c3557",
            border_width=2,
        )

        self.password_entry.pack(
            fill="x",
            padx=14,
            pady=(14, 7),
        )


        self.password_entry.bind(
            "<Return>",
            lambda event: self.start_scan()
        )


        button_frame = ctk.CTkFrame(
            input_card,
            fg_color="transparent",
        )

        button_frame.pack(
            fill="x",
            padx=14,
            pady=(0, 14),
        )


        button_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        button_frame.grid_columnconfigure(
            1,
            weight=2,
        )


        self.show_button = ctk.CTkButton(
            button_frame,
            text="SHOW",
            height=42,
            command=self.toggle_password,
            fg_color="#182b48",
            hover_color="#23436d",
            font=ctk.CTkFont(
                size=12,
                weight="bold",
            ),
        )

        self.show_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5),
        )


        self.scan_button = ctk.CTkButton(
            button_frame,
            text="⚡ SCAN PASSWORD",
            height=42,
            command=self.start_scan,
            fg_color="#0077ff",
            hover_color="#005bd1",
            font=ctk.CTkFont(
                size=13,
                weight="bold",
            ),
        )

        self.scan_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0),
        )


        # ====================================================
        # SCAN STATUS
        # ====================================================

        self.scan_status = ctk.CTkLabel(
            container,
            text="READY FOR SECURITY ANALYSIS",
            font=ctk.CTkFont(
                size=11,
                weight="bold",
            ),
            text_color="#00d9ff",
        )

        self.scan_status.pack(
            pady=(2, 5)
        )


        self.progress = ctk.CTkProgressBar(
            container,
            height=10,
            corner_radius=10,
            progress_color="#0077ff",
        )

        self.progress.pack(fill="x")

        self.progress.set(0)


        # ====================================================
        # MAIN RESULT CARD
        # ====================================================

        self.result_card = ctk.CTkFrame(
            container,
            height=175,
            fg_color="#0b1425",
            corner_radius=18,
            border_width=1,
            border_color="#162844",
        )

        self.result_card.pack(
            fill="x",
            pady=(11, 7),
        )

        self.result_card.pack_propagate(False)


        ctk.CTkLabel(
            self.result_card,
            text="AI SECURITY RESULT",
            font=ctk.CTkFont(
                size=11,
                weight="bold",
            ),
            text_color="#7f8da8",
        ).pack(
            pady=(15, 3)
        )


        self.strength_label = ctk.CTkLabel(
            self.result_card,
            text="WAITING",
            font=ctk.CTkFont(
                size=33,
                weight="bold",
            ),
            text_color="#ffffff",
        )

        self.strength_label.pack()


        self.score_label = ctk.CTkLabel(
            self.result_card,
            text="0 / 100",
            font=ctk.CTkFont(
                size=26,
                weight="bold",
            ),
            text_color="#ffffff",
        )

        self.score_label.pack(
            pady=(1, 0)
        )


        ctk.CTkLabel(
            self.result_card,
            text="SECURITY SCORE",
            font=ctk.CTkFont(
                size=9,
                weight="bold",
            ),
            text_color="#7f8da8",
        ).pack()


        # ====================================================
        # CRACK TIME CARD
        # ====================================================

        self.crack_card = ctk.CTkFrame(
            container,
            height=105,
            fg_color="#0b1425",
            corner_radius=15,
            border_width=1,
            border_color="#162844",
        )

        self.crack_card.pack(
            fill="x",
            pady=4,
        )

        self.crack_card.pack_propagate(False)


        ctk.CTkLabel(
            self.crack_card,
            text="ESTIMATED CRACK TIME",
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
            text_color="#7f8da8",
        ).pack(
            pady=(15, 4)
        )


        self.crack_label = ctk.CTkLabel(
            self.crack_card,
            text="--",
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
            text_color="#ffffff",
            wraplength=470,
        )

        self.crack_label.pack()


        # ====================================================
        # ENTROPY + SHA CARD
        # ====================================================

        info_card = ctk.CTkFrame(
            container,
            height=100,
            fg_color="#0b1425",
            corner_radius=15,
            border_width=1,
            border_color="#162844",
        )

        info_card.pack(
            fill="x",
            pady=4,
        )

        info_card.pack_propagate(False)


        self.entropy_label = ctk.CTkLabel(
            info_card,
            text="ENTROPY: -- bits",
            font=ctk.CTkFont(
                size=13,
                weight="bold",
            ),
            text_color="#7f8da8",
        )

        self.entropy_label.pack(
            pady=(15, 4)
        )


        self.hash_label = ctk.CTkLabel(
            info_card,
            text="SHA-256: Waiting for scan...",
            font=ctk.CTkFont(size=10),
            text_color="#7f8da8",
            wraplength=465,
        )

        self.hash_label.pack(
            padx=15
        )


        # ====================================================
        # GENERATE BUTTON
        # ====================================================

        self.generate_button = ctk.CTkButton(
            container,
            text="⚡ GENERATE SECURE PASSWORD",
            height=47,
            command=self.generate_secure_password,
            fg_color="#182b48",
            hover_color="#23436d",
            font=ctk.CTkFont(
                size=13,
                weight="bold",
            ),
        )

        self.generate_button.pack(
            fill="x",
            pady=(7, 0),
        )


        # ====================================================
        # FOOTER
        # ====================================================

        ctk.CTkLabel(
            container,
            text="FUZZUTECH • PYTHON CYBER SECURITY PROJECT",
            font=ctk.CTkFont(
                size=8,
                weight="bold",
            ),
            text_color="#40516e",
        ).pack(
            pady=(7, 0)
        )


    # ========================================================
    # TOGGLE PASSWORD
    # ========================================================

    def toggle_password(self):

        self.password_visible = not self.password_visible

        if self.password_visible:

            self.password_entry.configure(show="")

            self.show_button.configure(text="HIDE")

        else:

            self.password_entry.configure(show="●")

            self.show_button.configure(text="SHOW")


    # ========================================================
    # RESET SCAN UI
    # ========================================================

    def reset_scan_ui(self):

        self.progress.set(0)

        self.progress.configure(
            progress_color="#0077ff"
        )

        self.result_card.configure(
            border_color="#162844"
        )

        self.crack_card.configure(
            border_color="#162844"
        )

        self.score_label.configure(
            text="...",
            text_color="#ffffff",
        )

        self.strength_label.configure(
            text="SCANNING",
            text_color="#00d9ff",
        )

        self.crack_label.configure(
            text="ANALYZING...",
            text_color="#ffffff",
        )

        self.entropy_label.configure(
            text="ENTROPY: CALCULATING...",
            text_color="#7f8da8",
        )

        self.hash_label.configure(
            text="SHA-256: Generating security fingerprint...",
            text_color="#7f8da8",
        )


    # ========================================================
    # START SCAN
    # ========================================================

    def start_scan(self):

        password = self.password_entry.get()

        if not password:

            self.scan_status.configure(
                text="⚠ ENTER A PASSWORD TO START SCAN",
                text_color="#ffb020",
            )

            self.password_entry.focus_set()

            return


        # Cancel previous animation if user starts another scan.

        if self.scan_job is not None:

            self.after_cancel(self.scan_job)

            self.scan_job = None


        self.current_password = password

        self.scan_progress = 0

        self.reset_scan_ui()


        self.scan_status.configure(
            text="AI ENGINE ANALYZING PASSWORD...",
            text_color="#00d9ff",
        )


        self.scan_button.configure(
            state="disabled",
            text="SCANNING...",
        )


        self.animate_scan()


    # ========================================================
    # SCAN ANIMATION
    # ========================================================

    def animate_scan(self):

        self.scan_progress += 2

        progress_value = min(
            self.scan_progress / 100,
            1.0,
        )

        self.progress.set(progress_value)


        if self.scan_progress <= 25:

            self.scan_status.configure(
                text="CHECKING PASSWORD PATTERNS..."
            )


        elif self.scan_progress <= 50:

            self.scan_status.configure(
                text="CALCULATING SECURITY ENTROPY..."
            )


        elif self.scan_progress <= 75:

            self.scan_status.configure(
                text="ESTIMATING CRACK RESISTANCE..."
            )


        elif self.scan_progress < 100:

            self.scan_status.configure(
                text="GENERATING SECURITY REPORT..."
            )


        if self.scan_progress >= 100:

            self.scan_job = None

            self.display_result(
                self.current_password
            )

            return


        self.scan_job = self.after(
            18,
            self.animate_scan,
        )


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    def display_result(self, password):

        score = calculate_score(password)

        entropy = calculate_entropy(password)

        crack_time = calculate_crack_time(entropy)

        password_hash = hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()


        if score < 30:

            strength = "🚨 CRITICAL"

            color = "#ff304f"

            status_text = "⚠ WEAK PASSWORD DETECTED"


        elif score < 50:

            strength = "⚠ WEAK"

            color = "#ff6b35"

            status_text = "PASSWORD SECURITY IS WEAK"


        elif score < 70:

            strength = "MEDIUM"

            color = "#ffb020"

            status_text = "MODERATE PASSWORD SECURITY"


        elif score < 90:

            strength = "🛡 STRONG"

            color = "#35ff8a"

            status_text = "STRONG PASSWORD DETECTED"


        else:

            strength = "🔥 ULTRA SECURE"

            color = "#00d9ff"

            status_text = "MAXIMUM PASSWORD SECURITY"


        self.progress.set(1)

        self.progress.configure(
            progress_color=color
        )


        self.scan_status.configure(
            text=status_text,
            text_color=color,
        )


        self.strength_label.configure(
            text=strength,
            text_color=color,
        )


        self.score_label.configure(
            text=f"{score} / 100",
            text_color=color,
        )


        self.crack_label.configure(
            text=crack_time,
            text_color=color,
        )


        self.entropy_label.configure(
            text=f"ENTROPY: {entropy:.2f} bits",
            text_color=color,
        )


        # Only show a truncated hash.
        # This keeps the portrait UI clean.

        self.hash_label.configure(
            text=(
                "SHA-256: "
                + password_hash[:20]
                + "..."
                + password_hash[-12:]
            ),
        )


        self.result_card.configure(
            border_color=color
        )


        self.crack_card.configure(
            border_color=color
        )


        self.scan_button.configure(
            state="normal",
            text="⚡ SCAN PASSWORD",
        )


    # ========================================================
    # GENERATE SECURE PASSWORD
    # ========================================================

    def generate_secure_password(self):

        password = generate_password(18)

        self.password_entry.delete(
            0,
            "end"
        )

        self.password_entry.insert(
            0,
            password
        )

        self.start_scan()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app = PasswordScanner()

    app.mainloop()