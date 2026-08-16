import sys
import os
import re
import base64
import hashlib
import random
import string
import urllib.parse
import codecs
import json
import requests

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QFrame,
    QMessageBox,
    QProgressBar,
    QGroupBox,
    QScrollArea,
)


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "CRYPTBREAK AI"

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "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"
)

MODEL = "openai/gpt-4o-mini"


# ============================================================
# DEMO DATA GENERATORS
# ============================================================

def generate_base64():

    messages = [
        "Hello FuzzuTech!",
        "AI can analyze this data.",
        "Welcome to CryptBreak AI.",
        "This is a Base64 demonstration.",
        "Encryption is not the same as encoding.",
        "Python Security Lab",
        "Artificial Intelligence Demo",
        "Welcome to the tutorial!",
    ]

    text = random.choice(messages)

    encoded = base64.b64encode(
        text.encode("utf-8")
    ).decode("utf-8")

    return text, encoded


def generate_hex():

    messages = [
        "HELLO FUZZUTECH",
        "PYTHON SECURITY",
        "CRYPTBREAK AI",
        "DEMO ENCRYPTED DATA",
        "LEARN CYBERSECURITY",
        "AI SECURITY LAB",
        "WELCOME TO FUZZUTECH",
    ]

    text = random.choice(messages)

    encoded = text.encode(
        "utf-8"
    ).hex()

    return text, encoded


def generate_url():

    messages = [
        "hello fuzzutech",
        "ai security demo",
        "python encryption tutorial",
        "cryptbreak ai",
        "learn cybersecurity",
        "this is a URL encoding demo",
    ]

    text = random.choice(messages)

    encoded = urllib.parse.quote(
        text
    )

    return text, encoded


def generate_rot13():

    messages = [
        "HELLO FUZZUTECH",
        "THIS IS A SECURITY DEMO",
        "AI CAN DETECT ROT13",
        "PYTHON CYBERSECURITY",
        "CRYPTBREAK AI",
        "WELCOME TO THE LAB",
    ]

    text = random.choice(messages)

    encoded = codecs.encode(
        text,
        "rot_13"
    )

    return text, encoded


def caesar_encrypt(text, shift):

    result = []

    for char in text:

        if char.isalpha():

            base = (
                ord("A")
                if char.isupper()
                else ord("a")
            )

            result.append(
                chr(
                    (
                        ord(char)
                        - base
                        + shift
                    ) % 26
                    + base
                )
            )

        else:

            result.append(char)

    return "".join(result)


def generate_caesar():

    messages = [
        "SECRET MESSAGE",
        "HELLO FUZZUTECH",
        "AI SECURITY LAB",
        "PYTHON IS POWERFUL",
        "LEARN CYBERSECURITY",
        "CRYPTBREAK AI",
    ]

    text = random.choice(messages)

    shift = random.randint(
        1,
        25
    )

    encoded = caesar_encrypt(
        text,
        shift
    )

    return (
        text,
        encoded,
        shift
    )


def generate_sha256():

    messages = [
        "FuzzuTech",
        "CryptBreak AI",
        "Python Security",
        "AI Encryption Demo",
        "Hello World",
        "Cybersecurity",
        "OpenRouter AI",
    ]

    text = random.choice(messages)

    hashed = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    return text, hashed


def generate_md5():

    messages = [
        "FuzzuTech",
        "CryptBreak AI",
        "Python Security",
        "Hello World",
        "Cybersecurity",
    ]

    text = random.choice(messages)

    hashed = hashlib.md5(
        text.encode("utf-8")
    ).hexdigest()

    return text, hashed


def generate_sha1():

    messages = [
        "FuzzuTech",
        "CryptBreak AI",
        "Python Security",
        "Hello World",
        "Cybersecurity",
    ]

    text = random.choice(messages)

    hashed = hashlib.sha1(
        text.encode("utf-8")
    ).hexdigest()

    return text, hashed


def generate_random_ciphertext():

    alphabet = (
        string.ascii_letters
        + string.digits
        + "+/="
    )

    length = random.randint(
        48,
        96
    )

    value = "".join(
        random.choice(alphabet)
        for _ in range(length)
    )

    return (
        "Random ciphertext-like demonstration",
        value
    )


# ============================================================
# LOCAL DETECTION
# ============================================================

def is_hex(text):

    clean = text.strip().replace(
        " ",
        ""
    )

    if len(clean) <= 1:
        return False

    if len(clean) % 2 != 0:
        return False

    return bool(
        re.fullmatch(
            r"[0-9a-fA-F]+",
            clean
        )
    )


def decode_hex(text):

    try:

        clean = text.strip().replace(
            " ",
            ""
        )

        return bytes.fromhex(
            clean
        ).decode(
            "utf-8",
            errors="replace"
        )

    except Exception:

        return None


def is_base64(text):

    clean = re.sub(
        r"\s+",
        "",
        text
    )

    if len(clean) < 4:
        return False

    if not re.fullmatch(
        r"[A-Za-z0-9+/=_-]+",
        clean
    ):
        return False

    try:

        padded = (
            clean
            + "=" * (-len(clean) % 4)
        )

        base64.urlsafe_b64decode(
            padded
        )

        return True

    except Exception:

        return False


def decode_base64(text):

    try:

        clean = re.sub(
            r"\s+",
            "",
            text
        )

        padded = (
            clean
            + "=" * (-len(clean) % 4)
        )

        decoded = (
            base64.urlsafe_b64decode(
                padded
            )
        )

        return decoded.decode(
            "utf-8",
            errors="replace"
        )

    except Exception:

        return None


def detect_hash(text):

    value = text.strip()

    patterns = {

        "MD5":
            r"^[a-fA-F0-9]{32}$",

        "SHA-1":
            r"^[a-fA-F0-9]{40}$",

        "SHA-256":
            r"^[a-fA-F0-9]{64}$",

        "SHA-512":
            r"^[a-fA-F0-9]{128}$",

    }

    for name, pattern in patterns.items():

        if re.fullmatch(
            pattern,
            value
        ):
            return name

    return None


def local_analyze(data):

    results = []

    # --------------------------------------------------------
    # HEX
    # --------------------------------------------------------

    if is_hex(data):

        decoded = decode_hex(
            data
        )

        if decoded:

            results.append(
                (
                    "HEX",
                    95,
                    decoded
                )
            )

    # --------------------------------------------------------
    # BASE64
    # --------------------------------------------------------

    if is_base64(data):

        decoded = decode_base64(
            data
        )

        if decoded:

            results.append(
                (
                    "BASE64",
                    90,
                    decoded
                )
            )

    # --------------------------------------------------------
    # URL ENCODING
    # --------------------------------------------------------

    if "%" in data:

        decoded = urllib.parse.unquote(
            data
        )

        if decoded != data:

            results.append(
                (
                    "URL ENCODING",
                    90,
                    decoded
                )
            )

    # --------------------------------------------------------
    # HASH
    # --------------------------------------------------------

    hash_type = detect_hash(
        data
    )

    if hash_type:

        results.append(
            (
                f"HASH / {hash_type}",
                98,
                "Hash detected - not directly decryptable."
            )
        )

    # --------------------------------------------------------
    # ROT13
    # --------------------------------------------------------

    try:

        rot = codecs.decode(
            data,
            "rot_13"
        )

        if rot != data:

            results.append(
                (
                    "ROT13",
                    60,
                    rot
                )
            )

    except Exception:

        pass

    return results


# ============================================================
# AI WORKER
# ============================================================

class AIWorker(QThread):

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(
        self,
        data,
        local_results
    ):

        super().__init__()

        self.data = data
        self.local_results = local_results

    def run(self):

        try:

            if not API_KEY:

                raise Exception(
                    "OPENROUTER_API_KEY is missing."
                )

            prompt = f"""
You are CRYPTBREAK AI,
a defensive cryptography and
data-analysis assistant.

Analyze this user-provided data:

{self.data}

Local detections:

{json.dumps(
    self.local_results,
    indent=2
)}

Determine whether it appears to be:

- Encoding
- Hash
- Obfuscation
- Weak toy cipher
- Modern encryption
- Unknown

Important rules:

1. Do not claim that AES, RSA,
   ChaCha20 or properly implemented
   modern encryption can be magically
   decrypted without the required key.

2. Hashes are not encryption.

3. Safely explain what can and
   cannot be decoded.

4. If it is an encoding format,
   provide the decoded result.

5. If it is a hash, explain that
   hashes are one-way functions.

6. Keep the explanation suitable
   for a cybersecurity tutorial.

Return ONLY valid JSON:

{{
    "type": "detected type",
    "confidence": 0,
    "status": "Decoded / Hash / Encryption / Unknown",
    "result": "result if available",
    "explanation": "short explanation",
    "security_note": "short security note"
}}
"""

            headers = {

                "Authorization":
                    f"Bearer {API_KEY}",

                "Content-Type":
                    "application/json",

                "HTTP-Referer":
                    "https://fuzzutech.example",

                "X-Title":
                    "CRYPTBREAK AI"
            }

            payload = {

                "model": MODEL,

                "messages": [

                    {
                        "role": "system",
                        "content":
                            "You are a defensive "
                            "cryptography analyzer. "
                            "Return valid JSON only."
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ],

                "temperature": 0.1
            }

            response = requests.post(

                OPENROUTER_URL,

                headers=headers,

                json=payload,

                timeout=45
            )

            response.raise_for_status()

            result = response.json()

            content = (
                result["choices"][0]
                ["message"]["content"]
                .strip()
            )

            # Remove Markdown JSON fences
            content = re.sub(
                r"^```json\s*",
                "",
                content,
                flags=re.IGNORECASE
            )

            content = re.sub(
                r"\s*```$",
                "",
                content
            )

            parsed = json.loads(
                content
            )

            self.finished.emit(
                parsed
            )

        except Exception as e:

            self.error.emit(
                str(e)
            )


# ============================================================
# MAIN WINDOW
# ============================================================

class CryptBreakAI(QMainWindow):

    def __init__(self):

        super().__init__()

        self.worker = None

        self.setWindowTitle(
            APP_NAME
        )

        # ----------------------------------------------------
        # PORTRAIT WINDOW
        # ----------------------------------------------------
        #
        # 720 x 900 gives a compact portrait
        # recording window while the internal
        # scroll area handles the remaining content.
        #
        self.setFixedSize(
            720,
            900
        )

        self.build_ui()

        self.apply_classic_theme()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # SCROLL AREA
        # ----------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.setCentralWidget(
            scroll
        )

        # ----------------------------------------------------
        # SCROLLABLE CONTENT
        # ----------------------------------------------------

        central = QWidget()

        scroll.setWidget(
            central
        )

        root = QVBoxLayout(
            central
        )

        root.setContentsMargins(
            20,
            16,
            20,
            25
        )

        root.setSpacing(
            11
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = QFrame()

        header.setObjectName(
            "header"
        )

        header_layout = QVBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        title = QLabel(
            "CRYPTBREAK AI"
        )

        title.setObjectName(
            "mainTitle"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        header_layout.addWidget(
            title
        )

        subtitle = QLabel(
            "AI Encryption & Data Analyzer"
        )

        subtitle.setObjectName(
            "subtitle"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        header_layout.addWidget(
            subtitle
        )

        self.status = QLabel()

        self.status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        if API_KEY:

            self.status.setText(
                "● API CONNECTED"
            )

            self.status.setObjectName(
                "ready"
            )

        else:

            self.status.setText(
                "● API KEY NOT SET"
            )

            self.status.setObjectName(
                "error"
            )

        header_layout.addWidget(
            self.status
        )

        root.addWidget(
            header
        )

        # ====================================================
        # DEMO DATA GENERATOR
        # ====================================================

        demo_group = QGroupBox(
            "DEMO DATA GENERATOR"
        )

        demo_layout = QVBoxLayout(
            demo_group
        )

        demo_layout.setContentsMargins(
            10,
            12,
            10,
            10
        )

        self.demo_combo = QComboBox()

        self.demo_combo.addItems([
            "Base64",
            "Hex",
            "URL Encoding",
            "ROT13",
            "Caesar Cipher",
            "MD5 Hash",
            "SHA-1 Hash",
            "SHA-256 Hash",
            "Random Ciphertext",
        ])

        demo_layout.addWidget(
            self.demo_combo
        )

        generate_layout = QHBoxLayout()

        generate_layout.setSpacing(
            7
        )

        self.generate_button = QPushButton(
            "⚡ GENERATE"
        )

        self.generate_button.clicked.connect(
            self.generate_demo
        )

        generate_layout.addWidget(
            self.generate_button
        )

        self.generate_analyze_button = QPushButton(
            "⚡ GENERATE + ANALYZE"
        )

        self.generate_analyze_button.clicked.connect(
            self.generate_and_analyze
        )

        generate_layout.addWidget(
            self.generate_analyze_button
        )

        demo_layout.addLayout(
            generate_layout
        )

        root.addWidget(
            demo_group
        )

        # ====================================================
        # INPUT DATA
        # ====================================================

        input_group = QGroupBox(
            "INPUT DATA"
        )

        input_layout = QVBoxLayout(
            input_group
        )

        input_layout.setContentsMargins(
            10,
            12,
            10,
            10
        )

        self.input_box = QTextEdit()

        self.input_box.setPlaceholderText(
            "Generated or encrypted data..."
        )

        self.input_box.setMinimumHeight(
            120
        )

        self.input_box.setMaximumHeight(
            150
        )

        input_layout.addWidget(
            self.input_box
        )

        root.addWidget(
            input_group
        )

        # ====================================================
        # ANALYZE BUTTON
        # ====================================================

        self.analyze_button = QPushButton(
            "🔍  ANALYZE WITH AI"
        )

        self.analyze_button.setObjectName(
            "analyze"
        )

        self.analyze_button.clicked.connect(
            self.start_analysis
        )

        self.analyze_button.setMinimumHeight(
            44
        )

        root.addWidget(
            self.analyze_button
        )

        # ====================================================
        # AI ANALYSIS
        # ====================================================

        result_group = QGroupBox(
            "AI ANALYSIS"
        )

        result_layout = QVBoxLayout(
            result_group
        )

        result_layout.setContentsMargins(
            10,
            12,
            10,
            10
        )

        self.result_box = QTextEdit()

        self.result_box.setReadOnly(
            True
        )

        # Internal result scrollbar
        self.result_box.setMinimumHeight(
            360
        )

        self.result_box.setMaximumHeight(
            470
        )

        self.result_box.setPlainText(
            "Generate demo data or enter "
            "your own data."
        )

        result_layout.addWidget(
            self.result_box
        )

        root.addWidget(
            result_group
        )

        # ====================================================
        # PROGRESS
        # ====================================================

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            0
        )

        self.progress.setTextVisible(
            False
        )

        self.progress.setFixedHeight(
            5
        )

        self.progress.hide()

        root.addWidget(
            self.progress
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer = QLabel(
            "Educational Security Lab  •  "
            "Encoding ≠ Encryption ≠ Hashing"
        )

        footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        footer.setObjectName(
            "footer"
        )

        root.addWidget(
            footer
        )

    # ========================================================
    # CLASSIC WINDOWS THEME
    # ========================================================

    def apply_classic_theme(self):

        self.setStyleSheet("""

        /* ================================================
           MAIN WINDOW
           ================================================ */

        QMainWindow {
            background: #F0F0F0;
        }

        QWidget {
            font-family: "Segoe UI";
            font-size: 13px;
            color: #202020;
        }


        /* ================================================
           HEADER
           ================================================ */

        QFrame#header {
            background: #FFFFFF;
            border: 1px solid #B8B8B8;
            border-radius: 6px;
        }

        QLabel#mainTitle {
            font-size: 28px;
            font-weight: bold;
            color: #1E1E1E;
        }

        QLabel#subtitle {
            color: #666666;
            font-size: 12px;
        }

        QLabel#ready {
            color: #087F23;
            font-weight: bold;
        }

        QLabel#error {
            color: #B00020;
            font-weight: bold;
        }


        /* ================================================
           GROUP BOX
           ================================================ */

        QGroupBox {
            background: #FFFFFF;
            border: 1px solid #B5B5B5;
            border-radius: 5px;
            margin-top: 10px;
            padding: 8px;
            font-weight: bold;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            background: #FFFFFF;
        }


        /* ================================================
           TEXT EDIT
           ================================================ */

        QTextEdit {
            background: #FFFFFF;
            border: 1px solid #999999;
            border-radius: 3px;
            padding: 8px;
            color: #202020;
            selection-background-color: #316AC5;
            selection-color: #FFFFFF;
            font-family: "Consolas";
            font-size: 12px;
        }

        QTextEdit:focus {
            border: 1px solid #316AC5;
        }


        /* ================================================
           COMBO BOX
           ================================================ */

        QComboBox {
            background: #FFFFFF;
            border: 1px solid #999999;
            border-radius: 3px;
            padding: 7px;
            min-height: 20px;
        }

        QComboBox:hover {
            border: 1px solid #777777;
        }

        QComboBox::drop-down {
            border-left: 1px solid #AAAAAA;
            width: 25px;
        }


        /* ================================================
           BUTTONS
           ================================================ */

        QPushButton {
            background: #E7E7E7;
            border: 1px solid #888888;
            border-radius: 3px;
            padding: 8px;
            font-weight: bold;
            min-height: 20px;
        }

        QPushButton:hover {
            background: #F5F5F5;
        }

        QPushButton:pressed {
            background: #D5D5D5;
        }

        QPushButton:disabled {
            color: #888888;
            background: #DDDDDD;
            border-color: #AAAAAA;
        }


        /* ================================================
           MAIN ANALYZE BUTTON
           ================================================ */

        QPushButton#analyze {
            background: #316AC5;
            color: #FFFFFF;
            border: 1px solid #24549A;
            padding: 10px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#analyze:hover {
            background: #3F7AD8;
        }

        QPushButton#analyze:pressed {
            background: #2859A5;
        }


        /* ================================================
           PROGRESS BAR
           ================================================ */

        QProgressBar {
            height: 5px;
            border: 1px solid #AAAAAA;
            background: #FFFFFF;
            border-radius: 2px;
        }

        QProgressBar::chunk {
            background: #316AC5;
            border-radius: 2px;
        }


        /* ================================================
           SCROLLBAR
           ================================================ */

        QScrollBar:vertical {
            background: #E5E5E5;
            width: 14px;
            margin: 0px;
            border: 1px solid #C0C0C0;
        }

        QScrollBar::handle:vertical {
            background: #B5B5B5;
            min-height: 35px;
            border: 1px solid #999999;
        }

        QScrollBar::handle:vertical:hover {
            background: #999999;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            background: #E5E5E5;
            height: 15px;
            border: 1px solid #C0C0C0;
        }

        QScrollBar:horizontal {
            background: #E5E5E5;
            height: 14px;
        }

        QScrollBar::handle:horizontal {
            background: #B5B5B5;
            min-width: 35px;
        }


        /* ================================================
           FOOTER
           ================================================ */

        QLabel#footer {
            color: #777777;
            font-size: 11px;
        }

        """)

    # ========================================================
    # GENERATE DEMO
    # ========================================================

    def generate_demo(self):

        choice = (
            self.demo_combo.currentText()
        )

        original = ""
        encrypted = ""

        extra = ""

        # ----------------------------------------------------
        # BASE64
        # ----------------------------------------------------

        if choice == "Base64":

            original, encrypted = (
                generate_base64()
            )

        # ----------------------------------------------------
        # HEX
        # ----------------------------------------------------

        elif choice == "Hex":

            original, encrypted = (
                generate_hex()
            )

        # ----------------------------------------------------
        # URL
        # ----------------------------------------------------

        elif choice == "URL Encoding":

            original, encrypted = (
                generate_url()
            )

        # ----------------------------------------------------
        # ROT13
        # ----------------------------------------------------

        elif choice == "ROT13":

            original, encrypted = (
                generate_rot13()
            )

        # ----------------------------------------------------
        # CAESAR
        # ----------------------------------------------------

        elif choice == "Caesar Cipher":

            original, encrypted, shift = (
                generate_caesar()
            )

            extra = (
                f"\nSHIFT USED:\n{shift}\n"
            )

        # ----------------------------------------------------
        # MD5
        # ----------------------------------------------------

        elif choice == "MD5 Hash":

            original, encrypted = (
                generate_md5()
            )

        # ----------------------------------------------------
        # SHA1
        # ----------------------------------------------------

        elif choice == "SHA-1 Hash":

            original, encrypted = (
                generate_sha1()
            )

        # ----------------------------------------------------
        # SHA256
        # ----------------------------------------------------

        elif choice == "SHA-256 Hash":

            original, encrypted = (
                generate_sha256()
            )

        # ----------------------------------------------------
        # RANDOM
        # ----------------------------------------------------

        elif choice == "Random Ciphertext":

            original, encrypted = (
                generate_random_ciphertext()
            )

        # ----------------------------------------------------
        # SHOW DATA
        # ----------------------------------------------------

        self.input_box.setPlainText(
            encrypted
        )

        self.result_box.setPlainText(

            "DEMO GENERATED\n"
            "==============================\n\n"

            f"TYPE:\n"
            f"{choice}\n\n"

            "ORIGINAL DATA:\n"
            f"{original}\n\n"

            "GENERATED DATA:\n"
            f"{encrypted}\n"

            f"{extra}\n"

            "==============================\n"
            "Click ANALYZE WITH AI."
        )

    # ========================================================
    # GENERATE + ANALYZE
    # ========================================================

    def generate_and_analyze(self):

        self.generate_demo()

        self.start_analysis()

    # ========================================================
    # START ANALYSIS
    # ========================================================

    def start_analysis(self):

        data = (
            self.input_box
            .toPlainText()
            .strip()
        )

        if not data:

            QMessageBox.warning(
                self,
                "No Data",
                "Generate or enter some data first."
            )

            return

        if not API_KEY:

            QMessageBox.warning(
                self,
                "API Key Missing",
                "Set OPENROUTER_API_KEY first."
            )

            return

        # Disable buttons
        self.analyze_button.setEnabled(
            False
        )

        self.generate_button.setEnabled(
            False
        )

        self.generate_analyze_button.setEnabled(
            False
        )

        self.progress.show()

        self.result_box.setPlainText(
            "CRYPTBREAK AI\n"
            "==============================\n\n"
            "ANALYZING DATA...\n\n"
            "✓ Running local detection\n"
            "✓ Identifying data pattern\n"
            "✓ Sending analysis to AI\n\n"
            "Please wait..."
        )

        # Local analysis
        local_results = local_analyze(
            data
        )

        # AI Worker
        self.worker = AIWorker(
            data,
            local_results
        )

        self.worker.finished.connect(
            lambda result:
                self.show_result(
                    result,
                    local_results
                )
        )

        self.worker.error.connect(
            self.show_error
        )

        self.worker.start()

    # ========================================================
    # SHOW RESULT
    # ========================================================

    def show_result(
        self,
        result,
        local_results
    ):

        detected = result.get(
            "type",
            "Unknown"
        )

        confidence = result.get(
            "confidence",
            0
        )

        status = result.get(
            "status",
            "Unknown"
        )

        output = result.get(
            "result",
            "N/A"
        )

        explanation = result.get(
            "explanation",
            "N/A"
        )

        security = result.get(
            "security_note",
            "N/A"
        )

        text = (
            "╔══════════════════════════════╗\n"
            "        CRYPTBREAK AI\n"
            "╚══════════════════════════════╝\n\n"

            "DETECTED TYPE\n"
            f"{detected}\n\n"

            "CONFIDENCE\n"
            f"{confidence}%\n\n"

            "STATUS\n"
            f"{status}\n\n"

            "──────────────────────────────\n\n"

            "RESULT\n"
            f"{output}\n\n"

            "──────────────────────────────\n\n"

            "EXPLANATION\n"
            f"{explanation}\n\n"

            "──────────────────────────────\n\n"

            "SECURITY NOTE\n"
            f"{security}\n\n"

            "──────────────────────────────\n\n"

            "LOCAL DETECTIONS\n"
        )

        if not local_results:

            text += (
                "\n• No local pattern detected."
            )

        else:

            for item in local_results:

                text += (
                    f"\n• {item[0]}"
                    f" — {item[1]}%"
                )

                if item[2]:

                    preview = str(
                        item[2]
                    )

                    if len(preview) > 250:

                        preview = (
                            preview[:250]
                            + "..."
                        )

                    text += (
                        f"\n  → {preview}"
                    )

        self.result_box.setPlainText(
            text
        )

        # Scroll result to top
        scrollbar = (
            self.result_box
            .verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.minimum()
        )

        self.finish_analysis()

    # ========================================================
    # ERROR
    # ========================================================

    def show_error(
        self,
        error
    ):

        self.result_box.setPlainText(
            "❌ ANALYSIS ERROR\n"
            "==============================\n\n"
            f"{error}\n\n"
            "Check your API key, internet "
            "connection and OpenRouter model."
        )

        self.finish_analysis()

    # ========================================================
    # FINISH
    # ========================================================

    def finish_analysis(self):

        self.progress.hide()

        self.analyze_button.setEnabled(
            True
        )

        self.generate_button.setEnabled(
            True
        )

        self.generate_analyze_button.setEnabled(
            True
        )


# ============================================================
# APPLICATION START
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        APP_NAME
    )

    app.setFont(
        QFont(
            "Segoe UI",
            10
        )
    )

    window = CryptBreakAI()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()