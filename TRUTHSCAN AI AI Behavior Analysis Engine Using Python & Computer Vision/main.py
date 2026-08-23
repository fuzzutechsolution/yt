"""
TRUTHSCAN AI — AI Behavior Analysis Simulator
===============================================
An experimental AI-style facial behavior analysis simulator.
This application analyzes visible facial and behavioral patterns.
It is an experimental simulation and cannot reliably determine
whether someone is lying.

All processing is performed locally. No data is uploaded.

Usage:
    python main.py

Dependencies:
    pip install opencv-python mediapipe customtkinter pillow numpy
"""

# ──────────────────────────────────────────────
# Dependency check
# ──────────────────────────────────────────────
import sys
import importlib

_REQUIRED = {
    "cv2": "opencv-python",
    "mediapipe": "mediapipe",
    "customtkinter": "customtkinter",
    "PIL": "pillow",
    "numpy": "numpy",
}

_missing = []
for mod, pkg in _REQUIRED.items():
    try:
        importlib.import_module(mod)
    except ImportError:
        _missing.append(pkg)

if _missing:
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║          TRUTHSCAN AI — Missing Dependencies        ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║                                                      ║")
    print("║  The following packages are required:                 ║")
    for p in _missing:
        print(f"║    • {p:<50}║")
    print("║                                                      ║")
    print("║  Install with:                                        ║")
    print("║  pip install " + " ".join(_missing))
    print("║                                                      ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "TRUTHSCAN AI — Missing Dependencies",
            "The following packages are required:\n\n"
            + "\n".join(f"  • {p}" for p in _missing)
            + "\n\nInstall with:\n  pip install " + " ".join(_missing),
        )
        root.destroy()
    except Exception:
        pass
    sys.exit(1)

# ──────────────────────────────────────────────
# Standard library
# ──────────────────────────────────────────────
import threading
import time
import math
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List

# ──────────────────────────────────────────────
# Third-party
# ──────────────────────────────────────────────
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# ══════════════════════════════════════════════
# COLOR SYSTEM
# ══════════════════════════════════════════════
class Colors:
    BG           = "#0B1220"
    BG_SEC       = "#0F172A"
    CARD         = "#111B2E"
    CARD_HOVER   = "#16233A"
    PRIMARY      = "#2563EB"
    LIGHT_BLUE   = "#38BDF8"
    GOLD         = "#F59E0B"
    DANGER       = "#DC2626"
    SUCCESS      = "#16A34A"
    WHITE        = "#F8FAFC"
    MUTED        = "#94A3B8"
    BORDER       = "#24324A"
    ORANGE       = "#EA580C"

# ══════════════════════════════════════════════
# FONTS HELPER
# ══════════════════════════════════════════════
_FONT_FAMILY = "Segoe UI"

def _font(size: int = 12, weight: str = "normal") -> tuple:
    return (_FONT_FAMILY, size, weight)

# ══════════════════════════════════════════════
# DATA CLASSES
# ══════════════════════════════════════════════
@dataclass
class FaceData:
    """Stores per-frame face observation data."""
    detected: bool = False
    bbox: Optional[Tuple[int, int, int, int]] = None
    landmarks: Optional[list] = None
    nose_tip: Optional[Tuple[float, float]] = None
    left_eye: Optional[Tuple[float, float]] = None
    right_eye: Optional[Tuple[float, float]] = None
    mouth_open_ratio: float = 0.0
    eye_aspect_ratio: float = 0.0
    head_pitch: float = 0.0
    head_yaw: float = 0.0

@dataclass
class AnalysisMetrics:
    """Rolling analysis metrics (0-100 each)."""
    facial_stability: float = 50.0
    eye_movement: float = 50.0
    expression_change: float = 50.0
    head_movement: float = 50.0
    behavioral_consistency: float = 50.0
    suspicion_score: float = 0.0
    ai_confidence: float = 0.0


# ══════════════════════════════════════════════
# BEHAVIOR ANALYZER
# ══════════════════════════════════════════════
class BehaviorAnalyzer:
    """
    Computes heuristic behavioral metrics from sequential
    face observations. Uses rolling averages and smoothing.
    """

    def __init__(self, history_len: int = 30):
        self._history_len = history_len
        self._nose_history: List[Tuple[float, float]] = []
        self._left_eye_history: List[Tuple[float, float]] = []
        self._right_eye_history: List[Tuple[float, float]] = []
        self._mouth_history: List[float] = []
        self._ear_history: List[float] = []
        self._yaw_history: List[float] = []
        self._pitch_history: List[float] = []
        self._detection_history: List[bool] = []
        self._metrics = AnalysisMetrics()
        self._smooth_factor = 0.12  # lower = smoother transitions

    def reset(self):
        self._nose_history.clear()
        self._left_eye_history.clear()
        self._right_eye_history.clear()
        self._mouth_history.clear()
        self._ear_history.clear()
        self._yaw_history.clear()
        self._pitch_history.clear()
        self._detection_history.clear()
        self._metrics = AnalysisMetrics()

    @property
    def metrics(self) -> AnalysisMetrics:
        return self._metrics

    def _append(self, lst: list, val, maxlen: int = 0):
        ml = maxlen or self._history_len
        lst.append(val)
        if len(lst) > ml:
            lst.pop(0)

    @staticmethod
    def _pt_dist(a: Tuple[float, float], b: Tuple[float, float]) -> float:
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    @staticmethod
    def _std(values: list) -> float:
        if len(values) < 2:
            return 0.0
        m = sum(values) / len(values)
        return math.sqrt(sum((v - m) ** 2 for v in values) / len(values))

    def _lerp(self, current: float, target: float) -> float:
        return current + (target - current) * self._smooth_factor

    def update(self, face: FaceData):
        self._append(self._detection_history, face.detected, 60)

        if not face.detected:
            # Slowly decay confidence when no face
            self._metrics.ai_confidence = self._lerp(self._metrics.ai_confidence, 5.0)
            return

        # Accumulate histories
        if face.nose_tip:
            self._append(self._nose_history, face.nose_tip)
        if face.left_eye:
            self._append(self._left_eye_history, face.left_eye)
        if face.right_eye:
            self._append(self._right_eye_history, face.right_eye)
        self._append(self._mouth_history, face.mouth_open_ratio)
        self._append(self._ear_history, face.eye_aspect_ratio)
        self._append(self._yaw_history, face.head_yaw)
        self._append(self._pitch_history, face.head_pitch)

        need = 5  # minimum samples before computing
        if len(self._nose_history) < need:
            return

        # ── Facial Stability (lower jitter → higher stability) ──
        nose_jitters = [
            self._pt_dist(self._nose_history[i], self._nose_history[i - 1])
            for i in range(1, len(self._nose_history))
        ]
        avg_jitter = sum(nose_jitters) / max(len(nose_jitters), 1)
        raw_stability = max(0, 100 - avg_jitter * 18)
        self._metrics.facial_stability = self._lerp(
            self._metrics.facial_stability, raw_stability
        )

        # ── Eye Movement ──
        if len(self._left_eye_history) >= need and len(self._right_eye_history) >= need:
            eye_deltas = []
            for i in range(1, min(len(self._left_eye_history), len(self._right_eye_history))):
                dl = self._pt_dist(self._left_eye_history[i], self._left_eye_history[i - 1])
                dr = self._pt_dist(self._right_eye_history[i], self._right_eye_history[i - 1])
                eye_deltas.append((dl + dr) / 2)
            avg_eye = sum(eye_deltas) / max(len(eye_deltas), 1)
            raw_eye = min(100, avg_eye * 25)
            self._metrics.eye_movement = self._lerp(self._metrics.eye_movement, raw_eye)

        # ── Expression Change (mouth variance) ──
        if len(self._mouth_history) >= need:
            mouth_std = self._std(self._mouth_history)
            raw_expr = min(100, mouth_std * 350)
            self._metrics.expression_change = self._lerp(
                self._metrics.expression_change, raw_expr
            )

        # ── Head Movement ──
        if len(self._yaw_history) >= need:
            yaw_std = self._std(self._yaw_history)
            pitch_std = self._std(self._pitch_history)
            raw_head = min(100, (yaw_std + pitch_std) * 12)
            self._metrics.head_movement = self._lerp(
                self._metrics.head_movement, raw_head
            )

        # ── Behavioral Consistency ──
        recent_n = min(15, len(self._nose_history))
        if recent_n >= 3:
            recent_jitters = nose_jitters[-recent_n:]
            recent_std = self._std(recent_jitters)
            raw_consist = max(0, 100 - recent_std * 25)
            self._metrics.behavioral_consistency = self._lerp(
                self._metrics.behavioral_consistency, raw_consist
            )

        # ── Suspicion Score (weighted heuristic) ──
        inv_stability = 100 - self._metrics.facial_stability
        raw_suspicion = (
            inv_stability * 0.15
            + self._metrics.eye_movement * 0.25
            + self._metrics.expression_change * 0.25
            + self._metrics.head_movement * 0.20
            + (100 - self._metrics.behavioral_consistency) * 0.15
        )
        raw_suspicion = max(0, min(100, raw_suspicion))
        self._metrics.suspicion_score = self._lerp(
            self._metrics.suspicion_score, raw_suspicion
        )

        # ── AI Confidence ──
        det_rate = sum(self._detection_history) / max(len(self._detection_history), 1)
        samples_factor = min(1.0, len(self._nose_history) / self._history_len)
        stability_factor = self._metrics.facial_stability / 100.0
        raw_conf = det_rate * 40 + samples_factor * 30 + stability_factor * 30
        raw_conf = max(5, min(95, raw_conf))
        self._metrics.ai_confidence = self._lerp(self._metrics.ai_confidence, raw_conf)


# ══════════════════════════════════════════════
# MODEL DOWNLOADER
# ══════════════════════════════════════════════
_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/latest/face_landmarker.task"
)
_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".models")
_MODEL_PATH = os.path.join(_MODEL_DIR, "face_landmarker.task")


def _ensure_model() -> Optional[str]:
    """Download the MediaPipe face_landmarker model if not cached. Returns path or None."""
    if os.path.isfile(_MODEL_PATH) and os.path.getsize(_MODEL_PATH) > 100_000:
        return _MODEL_PATH
    try:
        os.makedirs(_MODEL_DIR, exist_ok=True)
        import urllib.request
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)
        if os.path.isfile(_MODEL_PATH) and os.path.getsize(_MODEL_PATH) > 100_000:
            return _MODEL_PATH
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════
# CAMERA ENGINE
# ══════════════════════════════════════════════
class CameraEngine:
    """
    Manages webcam capture and face processing in a background thread.
    Uses MediaPipe FaceLandmarker (Tasks API) when available, otherwise
    falls back to OpenCV Haar cascade face detection.
    """

    def __init__(self):
        self._cap: Optional[cv2.VideoCapture] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._frame: Optional[np.ndarray] = None
        self._face_data = FaceData()
        self._online = False

        # Try to initialize MediaPipe FaceLandmarker (Tasks API)
        self._face_landmarker = None
        self._use_mediapipe = False
        self._haar_cascade = None
        self._init_face_engine()

    def _init_face_engine(self):
        """Initialize MediaPipe FaceLandmarker or fall back to Haar cascade."""
        model_path = _ensure_model()
        if model_path:
            try:
                BaseOptions = mp.tasks.BaseOptions
                FaceLandmarker = mp.tasks.vision.FaceLandmarker
                FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
                RunningMode = mp.tasks.vision.RunningMode

                options = FaceLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=model_path),
                    running_mode=RunningMode.IMAGE,
                    num_faces=1,
                    min_face_detection_confidence=0.5,
                    min_face_presence_confidence=0.5,
                    min_tracking_confidence=0.5,
                    output_face_blendshapes=False,
                    output_facial_transformation_matrixes=False,
                )
                self._face_landmarker = FaceLandmarker.create_from_options(options)
                self._use_mediapipe = True
                return
            except Exception:
                self._face_landmarker = None

        # Fallback: OpenCV Haar cascade
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._haar_cascade = cv2.CascadeClassifier(cascade_path)
            if self._haar_cascade.empty():
                self._haar_cascade = None
        except Exception:
            self._haar_cascade = None

    @property
    def is_online(self) -> bool:
        return self._online

    def start(self) -> bool:
        if self._running:
            return True
        try:
            self._cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self._cap.isOpened():
                self._cap = cv2.VideoCapture(0)
            if not self._cap.isOpened():
                return False
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._cap.set(cv2.CAP_PROP_FPS, 30)
            self._running = True
            self._online = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            return True
        except Exception:
            return False

    def stop(self):
        self._running = False
        self._online = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    def get_frame(self) -> Optional[np.ndarray]:
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def get_face_data(self) -> FaceData:
        with self._lock:
            return FaceData(
                detected=self._face_data.detected,
                bbox=self._face_data.bbox,
                landmarks=self._face_data.landmarks,
                nose_tip=self._face_data.nose_tip,
                left_eye=self._face_data.left_eye,
                right_eye=self._face_data.right_eye,
                mouth_open_ratio=self._face_data.mouth_open_ratio,
                eye_aspect_ratio=self._face_data.eye_aspect_ratio,
                head_pitch=self._face_data.head_pitch,
                head_yaw=self._face_data.head_yaw,
            )

    # ── Processing helpers ──

    def _process_mediapipe(self, rgb: np.ndarray, h: int, w: int) -> FaceData:
        """Process a frame using MediaPipe FaceLandmarker Tasks API."""
        face = FaceData()
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self._face_landmarker.detect(mp_image)

        if result.face_landmarks and len(result.face_landmarks) > 0:
            lms = result.face_landmarks[0]  # list of NormalizedLandmark
            face.detected = True

            # Bounding box from landmarks
            xs = [l.x * w for l in lms]
            ys = [l.y * h for l in lms]
            x1, y1 = int(min(xs)), int(min(ys))
            x2, y2 = int(max(xs)), int(max(ys))
            pad = 20
            face.bbox = (
                max(0, x1 - pad),
                max(0, y1 - pad),
                min(w, x2 + pad),
                min(h, y2 + pad),
            )

            # Key landmarks (normalized)
            face.nose_tip = (lms[1].x, lms[1].y)
            face.left_eye = (lms[33].x, lms[33].y)
            face.right_eye = (lms[263].x, lms[263].y)

            # Mouth open ratio
            upper_lip = lms[13]
            lower_lip = lms[14]
            mouth_left = lms[61]
            mouth_right = lms[291]
            mouth_h = abs(upper_lip.y - lower_lip.y)
            mouth_w = abs(mouth_left.x - mouth_right.x)
            face.mouth_open_ratio = mouth_h / max(mouth_w, 0.001)

            # Eye aspect ratio
            le_top = lms[159]
            le_bot = lms[145]
            le_left = lms[33]
            le_right = lms[133]
            eye_h = abs(le_top.y - le_bot.y)
            eye_w = abs(le_left.x - le_right.x)
            face.eye_aspect_ratio = eye_h / max(eye_w, 0.001)

            # Head pose estimate
            eye_mid_x = (face.left_eye[0] + face.right_eye[0]) / 2
            eye_mid_y = (face.left_eye[1] + face.right_eye[1]) / 2
            face.head_yaw = (face.nose_tip[0] - eye_mid_x) * 100
            face.head_pitch = (face.nose_tip[1] - eye_mid_y) * 100

            # Landmark pixel coords for drawing
            face.landmarks = [(int(l.x * w), int(l.y * h)) for l in lms]

        return face

    def _process_haar(self, frame: np.ndarray, h: int, w: int) -> FaceData:
        """Fallback face detection using OpenCV Haar cascade."""
        face = FaceData()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = self._haar_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        if len(detections) > 0:
            # Take the largest face
            areas = [dw * dh for (_, _, dw, dh) in detections]
            idx = int(np.argmax(areas))
            fx, fy, fw, fh = detections[idx]
            face.detected = True
            face.bbox = (fx, fy, fx + fw, fy + fh)

            # Synthesize approximate landmark positions from bbox center
            cx = (fx + fw / 2) / w
            cy = (fy + fh / 2) / h
            face.nose_tip = (cx, cy)
            face.left_eye = (cx - fw / (6 * w), cy - fh / (6 * h))
            face.right_eye = (cx + fw / (6 * w), cy - fh / (6 * h))
            face.mouth_open_ratio = 0.15
            face.eye_aspect_ratio = 0.3
            face.head_yaw = 0.0
            face.head_pitch = 0.0

        return face

    def _capture_loop(self):
        while self._running:
            try:
                if self._cap is None or not self._cap.isOpened():
                    time.sleep(0.05)
                    continue
                ret, frame = self._cap.read()
                if not ret or frame is None:
                    time.sleep(0.02)
                    continue

                frame = cv2.flip(frame, 1)
                h, w = frame.shape[:2]

                if self._use_mediapipe and self._face_landmarker:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    face = self._process_mediapipe(rgb, h, w)
                elif self._haar_cascade is not None:
                    face = self._process_haar(frame, h, w)
                else:
                    face = FaceData()

                with self._lock:
                    self._frame = frame
                    self._face_data = face

            except Exception:
                time.sleep(0.02)
            time.sleep(0.008)  # ~30 fps cap

    def release(self):
        self.stop()
        if self._face_landmarker:
            try:
                self._face_landmarker.close()
            except Exception:
                pass


# ══════════════════════════════════════════════
# METRIC CARD WIDGET
# ══════════════════════════════════════════════
class MetricCard(ctk.CTkFrame):
    """A single metric display that rearranges based on layout mode."""

    def __init__(self, master, label: str, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.CARD,
            corner_radius=10,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs,
        )
        self._value = 0.0
        self._raw_label_text = label

        self._label = ctk.CTkLabel(
            self,
            text=label.upper(),
            font=_font(10, "bold"),
            text_color=Colors.MUTED,
            anchor="w",
        )

        self._bar_frame = ctk.CTkFrame(self, fg_color="transparent", height=22)

        self._bar = ctk.CTkProgressBar(
            self._bar_frame,
            height=8,
            corner_radius=4,
            fg_color=Colors.BG,
            progress_color=Colors.PRIMARY,
            border_width=0,
        )

        self._pct = ctk.CTkLabel(
            self._bar_frame,
            text="0%",
            font=_font(11, "bold"),
            text_color=Colors.WHITE,
            width=42,
            anchor="e",
        )
        
        self.set_layout_mode("desktop")

    def set_layout_mode(self, mode: str):
        # Reset positioning
        self._label.pack_forget()
        self._bar.pack_forget()
        self._pct.pack_forget()
        self._bar_frame.pack_forget()

        if mode in ("portrait", "compact"):
            # Horizontal layout: name (left), bar (middle), pct (right)
            self._label.configure(anchor="w", width=140)
            self._label.pack(side="left", padx=(14, 10), pady=10)
            
            self._pct.pack(side="right", padx=(10, 14), pady=10)
            self._bar.pack(side="right", fill="x", expand=True, pady=16)
        else:
            # Vertical stack layout
            self._label.configure(anchor="w", width=0)
            self._label.pack(fill="x", padx=14, pady=(10, 0))
            
            self._bar_frame.pack(fill="x", padx=14, pady=(6, 10))
            self._bar_frame.pack_propagate(False)
            
            self._bar.pack(in_=self._bar_frame, side="left", fill="x", expand=True, pady=7)
            self._pct.pack(in_=self._bar_frame, side="right", padx=(8, 0))

    def set_value(self, val: float, color: Optional[str] = None):
        val = max(0, min(100, val))
        self._value = val
        self._bar.set(val / 100.0)
        self._pct.configure(text=f"{int(val)}%")
        if color:
            self._bar.configure(progress_color=color)


# ══════════════════════════════════════════════
# SUSPICION GAUGE WIDGET
# ══════════════════════════════════════════════
class SuspicionGauge(ctk.CTkFrame):
    """Custom canvas-based indicator that switches to horizontal or arc dynamically."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._value = 0.0
        self._color = Colors.MUTED
        self._status_text = "AWAITING"

        self.canvas = tk.Canvas(
            self,
            bg=Colors.CARD,
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw())

    def set_value(self, val: float, color: str, status: str):
        self._value = val
        self._color = color
        self._status_text = status
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return

        if w < 180 or h < 120:
            self._draw_horizontal(w, h)
        else:
            self._draw_circular(w, h)

    def _draw_circular(self, w, h):
        cx, cy = w / 2, h / 2
        r = min(w, h) * 0.4
        thickness = min(w, h) * 0.08

        # Background track arc
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=225, extent=-270,
            style="arc", width=thickness,
            outline=Colors.BORDER,
        )

        # Active colored arc
        extent = -270 * (self._value / 100.0)
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=225, extent=extent,
            style="arc", width=thickness,
            outline=self._color,
        )

        # Autoscale text sizes
        val_size = max(16, int(min(w, h) * 0.12))
        lbl_size = max(8, int(min(w, h) * 0.06))

        self.canvas.create_text(
            cx, cy - 5,
            text=f"{int(self._value)}%",
            fill=Colors.WHITE,
            font=_font(val_size, "bold"),
        )
        self.canvas.create_text(
            cx, cy + 20,
            text=self._status_text.upper(),
            fill=self._color,
            font=_font(lbl_size, "bold"),
        )

    def _draw_horizontal(self, w, h):
        padding_x = 10
        cy = h / 2
        bar_w = w - 2 * padding_x
        bar_h = 8

        # Background track
        self.canvas.create_rectangle(
            padding_x, cy - bar_h / 2,
            padding_x + bar_w, cy + bar_h / 2,
            fill=Colors.BG, outline=Colors.BORDER,
            width=1,
        )

        # Active fill
        fill_w = bar_w * (self._value / 100.0)
        if fill_w > 0:
            self.canvas.create_rectangle(
                padding_x, cy - bar_h / 2,
                padding_x + fill_w, cy + bar_h / 2,
                fill=self._color, outline="",
                width=0,
            )

        # Gauge Status labels
        self.canvas.create_text(
            padding_x, cy - 12,
            text=f"SUSPICION: {int(self._value)}% ({self._status_text})",
            fill=Colors.WHITE,
            font=_font(9, "bold"),
            anchor="w",
        )


# ══════════════════════════════════════════════
# RESULT CARD WIDGET
# ══════════════════════════════════════════════
class ResultCard(ctk.CTkFrame):
    """ suspicious behavior result viewer, adapting layout style. """

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Colors.CARD,
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs,
        )

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=12, pady=12)

        self.gauge = SuspicionGauge(self.container)

        self.info_frame = ctk.CTkFrame(self.container, fg_color="transparent")

        self._desc = ctk.CTkLabel(
            self.info_frame,
            text="Start analysis to begin.",
            font=_font(11),
            text_color=Colors.MUTED,
            wraplength=220,
            anchor="w",
            justify="left",
        )

        self._conf_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self._conf_label = ctk.CTkLabel(
            self._conf_frame,
            text="AI CONFIDENCE:",
            font=_font(9, "bold"),
            text_color=Colors.MUTED,
        )
        self._conf_value = ctk.CTkLabel(
            self._conf_frame,
            text="—",
            font=_font(14, "bold"),
            text_color=Colors.LIGHT_BLUE,
        )

        self._disclaimer = ctk.CTkLabel(
            self.info_frame,
            text="⚠ Experimental estimate — not a reliable lie detector.",
            font=_font(9),
            text_color=Colors.MUTED,
            wraplength=220,
            anchor="w",
            justify="left",
        )

        self.set_layout_mode("desktop")

    def set_layout_mode(self, mode: str):
        # Unpack elements
        self.gauge.pack_forget()
        self.info_frame.pack_forget()
        self._desc.pack_forget()
        self._conf_frame.pack_forget()
        self._conf_label.pack_forget()
        self._conf_value.pack_forget()
        self._disclaimer.pack_forget()

        if mode in ("portrait", "compact"):
            # Side-by-side layout
            self.gauge.pack(side="left", fill="both", expand=True, padx=(0, 10))
            self.gauge.configure(width=140, height=140)

            self.info_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

            self._desc.pack(anchor="w", pady=(5, 5))
            self._desc.configure(wraplength=200, justify="left")
            
            self._conf_frame.pack(anchor="w", fill="x", pady=2)
            self._conf_label.pack(side="left")
            self._conf_value.pack(side="left", padx=5)
            
            self._disclaimer.pack(anchor="w", pady=(5, 5))
            self._disclaimer.configure(wraplength=200, justify="left")
        else:
            # Vertical stack layout
            self.gauge.pack(side="top", fill="both", expand=True, pady=(5, 10))
            self.gauge.configure(width=180, height=180)

            self.info_frame.pack(side="top", fill="x")

            self._desc.pack(anchor="center", pady=(5, 5))
            self._desc.configure(wraplength=240, justify="center")

            self._conf_frame.pack(anchor="center", pady=4)
            self._conf_label.pack(side="top")
            self._conf_value.pack(side="top", pady=1)

            self._disclaimer.pack(anchor="center", pady=(8, 5))
            self._disclaimer.configure(wraplength=240, justify="center")

    def update_result(self, suspicion: float, confidence: float, active: bool):
        if not active:
            self.gauge.set_value(0.0, Colors.MUTED, "AWAITING")
            self._conf_value.configure(text="—")
            self._desc.configure(text="Start analysis to begin.")
            return

        s = int(suspicion)
        if s < 30:
            color = Colors.SUCCESS
            label = "LOW SUSPICION"
            desc = "Behavioral signals appear normal."
        elif s < 60:
            color = Colors.GOLD
            label = "MODERATE"
            desc = "Some behavioral variation detected."
        elif s < 80:
            color = Colors.ORANGE
            label = "ELEVATED"
            desc = "Behavioral signals appear unusual."
        else:
            color = Colors.DANGER
            label = "HIGH SUSPICION"
            desc = "Significant behavioral variation detected."

        self.gauge.set_value(suspicion, color, label)
        self._conf_value.configure(text=f"{int(confidence)}%")
        self._desc.configure(text=desc)

    def set_demo_result(self, suspicion: int, confidence: int, desc: str):
        self.gauge.set_value(suspicion, Colors.DANGER, "HIGH SUSPICION")
        self._conf_value.configure(text=f"{confidence}%")
        self._desc.configure(text=desc)


# ══════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════
class TruthScanApp:
    """Main application controller with responsive layouts."""

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("TRUTHSCAN AI — AI Behavior Analysis Engine")
        self.root.configure(fg_color=Colors.BG)
        
        # Responsive sizing restrictions
        self.root.minsize(520, 700)

        # Center window coordinates
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = 1200, 800
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Core State
        self._camera = CameraEngine()
        self._analyzer = BehaviorAnalyzer()
        self._analysis_active = False
        self._analysis_paused = False
        self._camera_online = False
        self._scan_y = 0.0
        self._demo_active = False
        self._demo_step = 0
        self._demo_timer_id = None
        self._face_detected = False
        self._closing = False
        self._startup_done = False
        self._resize_timer_id = None
        self._current_mode = ""

        # Build initial Splash screen
        self._build_splash()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(2200, self._finish_splash)

    # ──────────────────────────────────────────
    # SPLASH SCREEN
    # ──────────────────────────────────────────
    def _build_splash(self):
        self._splash = ctk.CTkFrame(self.root, fg_color=Colors.BG)
        self._splash.place(relx=0, rely=0, relwidth=1, relheight=1)

        ctk.CTkLabel(
            self._splash,
            text="◉  TRUTHSCAN AI",
            font=_font(32, "bold"),
            text_color=Colors.WHITE,
        ).place(relx=0.5, rely=0.38, anchor="center")

        ctk.CTkLabel(
            self._splash,
            text="Initializing AI Analysis Engine...",
            font=_font(13),
            text_color=Colors.MUTED,
        ).place(relx=0.5, rely=0.48, anchor="center")

        self._splash_bar = ctk.CTkProgressBar(
            self._splash,
            width=300,
            height=4,
            corner_radius=2,
            fg_color=Colors.BG_SEC,
            progress_color=Colors.PRIMARY,
        )
        self._splash_bar.place(relx=0.5, rely=0.55, anchor="center")
        self._splash_bar.set(0)
        self._animate_splash(0)

    def _animate_splash(self, step: int):
        if self._closing or step > 20 or not self._splash.winfo_exists():
            return
        try:
            self._splash_bar.set(min(step / 20, 1.0))
        except Exception:
            return
        self.root.after(100, self._animate_splash, step + 1)

    def _finish_splash(self):
        if self._closing:
            return
        self._splash.destroy()
        
        # Build Dashboard parts
        self._build_components()
        
        # Monitor Resizes
        self.root.bind("<Configure>", self._on_resize_event)
        
        self._startup_done = True
        self._handle_responsive_resize()
        self._tick_ui()

    # ──────────────────────────────────────────
    # COMPONENTS INITIALIZATION
    # ──────────────────────────────────────────
    def _build_components(self):
        # ── Parent structure ──
        self._header = ctk.CTkFrame(self.root, fg_color=Colors.BG_SEC, height=52, corner_radius=0)
        self._header.pack(fill="x", side="top")
        self._header.pack_propagate(False)

        # Header inner compartments
        self._header_title_frame = ctk.CTkFrame(self._header, fg_color="transparent")
        ctk.CTkLabel(
            self._header_title_frame,
            text="◉  TRUTHSCAN AI",
            font=_font(16, "bold"),
            text_color=Colors.WHITE,
        ).pack(side="left")
        ctk.CTkLabel(
            self._header_title_frame,
            text="AI BEHAVIOR ANALYSIS ENGINE",
            font=_font(9),
            text_color=Colors.MUTED,
        ).pack(side="left", padx=10)

        self._header_status_frame = ctk.CTkFrame(self._header, fg_color="transparent")
        
        self._info_btn = ctk.CTkButton(
            self._header_status_frame,
            text="ⓘ",
            width=32,
            height=28,
            corner_radius=6,
            font=_font(14),
            fg_color="transparent",
            hover_color=Colors.CARD_HOVER,
            text_color=Colors.MUTED,
            command=self._show_info,
        )
        self._info_btn.pack(side="right", padx=(10, 0))

        ctk.CTkLabel(
            self._header_status_frame,
            text="Experimental AI",
            font=_font(10),
            text_color=Colors.MUTED,
        ).pack(side="right", padx=10)

        self._local_label = ctk.CTkLabel(
            self._header_status_frame,
            text="🔒 LOCAL PROCESSING",
            font=_font(9),
            text_color=Colors.SUCCESS,
        )
        self._local_label.pack(side="right", padx=10)

        self._cam_status_label = ctk.CTkLabel(
            self._header_status_frame,
            text="● CAMERA OFFLINE",
            font=_font(10, "bold"),
            text_color=Colors.DANGER,
        )
        self._cam_status_label.pack(side="right", padx=10)

        # Footer Frame
        self._footer = ctk.CTkFrame(self.root, fg_color=Colors.BG_SEC, height=32, corner_radius=0)
        self._footer.pack(fill="x", side="bottom")
        self._footer.pack_propagate(False)

        self._footer_lbl = ctk.CTkLabel(
            self._footer,
            text="🔒 100% LOCAL PROCESSING   •   YOUR PRIVACY IS SECURE",
            font=_font(9, "bold"),
            text_color=Colors.MUTED,
        )
        self._footer_lbl.pack(expand=True)

        # Main viewport frame
        self._main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        self._main_content.pack(fill="both", expand=True)

        # Layout containers
        self._desktop_container = ctk.CTkFrame(self._main_content, fg_color="transparent")
        self._right_panel = ctk.CTkFrame(self._main_content, fg_color="transparent")
        self._scroll_container = ctk.CTkScrollableFrame(self._main_content, fg_color="transparent")

        # Functional viewport panels
        # 1. Camera Panel
        self._cam_panel = ctk.CTkFrame(
            self._main_content,
            fg_color=Colors.CARD,
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER,
        )

        cam_header = ctk.CTkFrame(self._cam_panel, fg_color="transparent", height=36)
        cam_header.pack(fill="x", padx=16, pady=(12, 0))
        cam_header.pack_propagate(False)

        ctk.CTkLabel(
            cam_header,
            text="LIVE FEED",
            font=_font(11, "bold"),
            text_color=Colors.MUTED,
        ).pack(side="left")

        self._face_status = ctk.CTkLabel(
            cam_header,
            text="",
            font=_font(10),
            text_color=Colors.MUTED,
        )
        self._face_status.pack(side="right")

        self._cam_canvas = tk.Canvas(
            self._cam_panel,
            bg=Colors.BG,
            highlightthickness=0,
            cursor="crosshair",
        )
        self._cam_canvas.pack(fill="both", expand=True, padx=16, pady=(8, 12))
        self._cam_image_id = None
        self._cam_photo = None

        # Camera offline empty state
        self._cam_offline_frame = ctk.CTkFrame(self._cam_panel, fg_color=Colors.BG, corner_radius=12)
        self._cam_offline_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        ctk.CTkLabel(
            self._cam_offline_frame,
            text="◉",
            font=_font(48, "bold"),
            text_color=Colors.PRIMARY,
        ).pack(pady=(40, 5))

        ctk.CTkLabel(
            self._cam_offline_frame,
            text="CAMERA OFFLINE",
            font=_font(16, "bold"),
            text_color=Colors.WHITE,
        ).pack(pady=2)

        ctk.CTkLabel(
            self._cam_offline_frame,
            text="Tap 'START CAMERA' below to begin setup.",
            font=_font(11),
            text_color=Colors.MUTED,
        ).pack(pady=(0, 20))

        self._btn_start_cam_inline = ctk.CTkButton(
            self._cam_offline_frame,
            text="▶  START CAMERA",
            fg_color=Colors.PRIMARY,
            hover_color="#1d4ed8",
            corner_radius=8,
            font=_font(12, "bold"),
            command=self._start_camera,
        )
        self._btn_start_cam_inline.pack(pady=5)

        self._cam_offline_status_lbl = ctk.CTkLabel(
            self._cam_offline_frame,
            text="",
            font=_font(10),
            text_color=Colors.MUTED,
        )
        self._cam_offline_status_lbl.pack(pady=10)

        # 2. Metrics panel
        self._metrics_panel = ctk.CTkFrame(self._main_content, fg_color="transparent")
        
        metrics_title_frame = ctk.CTkFrame(self._metrics_panel, fg_color="transparent", height=30)
        metrics_title_frame.pack(fill="x", pady=(0, 6))
        metrics_title_frame.pack_propagate(False)
        ctk.CTkLabel(
            metrics_title_frame,
            text="BEHAVIORAL METRICS",
            font=_font(11, "bold"),
            text_color=Colors.MUTED,
        ).pack(side="left")

        self._scan_status_label = ctk.CTkLabel(
            metrics_title_frame,
            text="",
            font=_font(9),
            text_color=Colors.LIGHT_BLUE,
        )
        self._scan_status_label.pack(side="right")

        self._metric_stability = MetricCard(self._metrics_panel, "Facial Stability")
        self._metric_stability.pack(fill="x", pady=(0, 5))

        self._metric_eye = MetricCard(self._metrics_panel, "Eye Movement")
        self._metric_eye.pack(fill="x", pady=(0, 5))

        self._metric_expr = MetricCard(self._metrics_panel, "Expression Change")
        self._metric_expr.pack(fill="x", pady=(0, 5))

        self._metric_head = MetricCard(self._metrics_panel, "Head Movement")
        self._metric_head.pack(fill="x", pady=(0, 5))

        self._metric_consist = MetricCard(self._metrics_panel, "Behavioral Consistency")
        self._metric_consist.pack(fill="x", pady=(0, 0))

        # 3. Result card
        self._result_card = ResultCard(self._main_content)

        # 4. Controls layout
        self._controls_panel = ctk.CTkFrame(
            self._main_content,
            fg_color=Colors.BG_SEC,
            corner_radius=10,
            border_width=1,
            border_color=Colors.BORDER,
        )

        btn_style = dict(
            height=44,
            corner_radius=8,
            font=_font(11, "bold"),
            border_width=1,
        )

        self._btn_camera = ctk.CTkButton(
            self._controls_panel,
            text="▶  START CAMERA",
            fg_color=Colors.PRIMARY,
            hover_color="#1d4ed8",
            border_color=Colors.PRIMARY,
            command=self._toggle_camera,
            **btn_style,
        )

        self._btn_analysis = ctk.CTkButton(
            self._controls_panel,
            text="◉  START ANALYSIS",
            fg_color=Colors.CARD,
            hover_color=Colors.CARD_HOVER,
            border_color=Colors.BORDER,
            text_color=Colors.WHITE,
            command=self._toggle_analysis,
            state="disabled",
            **btn_style,
        )

        self._btn_pause = ctk.CTkButton(
            self._controls_panel,
            text="⏸  PAUSE",
            fg_color=Colors.CARD,
            hover_color=Colors.CARD_HOVER,
            border_color=Colors.BORDER,
            text_color=Colors.WHITE,
            command=self._toggle_pause,
            state="disabled",
            **btn_style,
        )

        self._btn_reset = ctk.CTkButton(
            self._controls_panel,
            text="↻  RESET",
            fg_color=Colors.CARD,
            hover_color=Colors.CARD_HOVER,
            border_color=Colors.BORDER,
            text_color=Colors.WHITE,
            command=self._reset,
            **btn_style,
        )

        self._btn_capture = ctk.CTkButton(
            self._controls_panel,
            text="📷  CAPTURE",
            fg_color=Colors.CARD,
            hover_color=Colors.CARD_HOVER,
            border_color=Colors.BORDER,
            text_color=Colors.WHITE,
            command=self._capture_result,
            **btn_style,
        )

        self._btn_demo = ctk.CTkButton(
            self._controls_panel,
            text="▶  DEMO MODE",
            fg_color=Colors.GOLD,
            hover_color="#d97706",
            border_color=Colors.GOLD,
            text_color=Colors.BG,
            command=self._start_demo,
            **btn_style,
        )

    # ──────────────────────────────────────────
    # RESPONSIVE RESPONSIVENESS AND BREAKPOINTS
    # ──────────────────────────────────────────
    def _on_resize_event(self, event):
        if event.widget != self.root:
            return
        if self._resize_timer_id:
            self.root.after_cancel(self._resize_timer_id)
        self._resize_timer_id = self.root.after(150, self._handle_responsive_resize)

    def _handle_responsive_resize(self):
        self._resize_timer_id = None
        if self._closing:
            return

        w = self.root.winfo_width()
        h = self.root.winfo_height()
        aspect = w / h if h > 0 else 1.0

        # Breakpoints logic
        if w >= 1100 and aspect >= 1.25:
            new_mode = "desktop"
        elif w >= 800 or (0.95 <= aspect <= 1.25):
            new_mode = "compact"
        else:
            new_mode = "portrait"

        if new_mode != self._current_mode:
            self._current_mode = new_mode
            self._apply_layout(new_mode)

    def _apply_layout(self, mode: str):
        # 1. Unpack all panels
        self._cam_panel.pack_forget()
        self._cam_panel.grid_forget()
        self._metrics_panel.pack_forget()
        self._metrics_panel.grid_forget()
        self._result_card.pack_forget()
        self._result_card.grid_forget()
        self._controls_panel.pack_forget()
        self._controls_panel.grid_forget()

        self._desktop_container.pack_forget()
        self._right_panel.pack_forget()
        self._right_panel.grid_forget()
        self._scroll_container.pack_forget()

        # 2. Config updates based on layouts
        self._relayout_header(mode)
        self._relayout_footer(mode)
        self._layout_controls(mode)

        for card in [
            self._metric_stability,
            self._metric_eye,
            self._metric_expr,
            self._metric_head,
            self._metric_consist,
        ]:
            card.set_layout_mode(mode)
            
        self._result_card.set_layout_mode(mode)

        # 3. Apply modes
        if mode == "desktop":
            self._desktop_container.pack(fill="both", expand=True, padx=16, pady=12)

            self._cam_panel.grid(in_=self._desktop_container, row=0, column=0, sticky="nsew", padx=(0, 8))
            self._cam_panel.configure(height=0)  # Expand dynamically

            self._right_panel.grid(in_=self._desktop_container, row=0, column=1, sticky="nsew", padx=(8, 0))
            self._metrics_panel.pack(in_=self._right_panel, fill="both", expand=True, pady=(0, 6))
            self._result_card.pack(in_=self._right_panel, fill="x", pady=(6, 0))

            self._controls_panel.grid(in_=self._desktop_container, row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0))

            self._desktop_container.grid_columnconfigure(0, weight=63)
            self._desktop_container.grid_columnconfigure(1, weight=37)
            self._desktop_container.grid_rowconfigure(0, weight=1)
            self._desktop_container.grid_rowconfigure(1, weight=0)

        elif mode == "compact":
            self._scroll_container.pack(fill="both", expand=True, padx=14, pady=10)

            self._cam_panel.pack(in_=self._scroll_container, fill="x", pady=(0, 6))
            self._cam_panel.configure(height=350)

            self._metrics_panel.pack(in_=self._scroll_container, fill="x", pady=6)
            self._result_card.pack(in_=self._scroll_container, fill="x", pady=6)
            self._controls_panel.pack(in_=self._scroll_container, fill="x", pady=(6, 0))

        else:  # portrait mode
            self._scroll_container.pack(fill="both", expand=True, padx=10, pady=8)

            self._cam_panel.pack(in_=self._scroll_container, fill="x", pady=(0, 5))
            self._cam_panel.configure(height=280)

            self._metrics_panel.pack(in_=self._scroll_container, fill="x", pady=5)
            self._result_card.pack(in_=self._scroll_container, fill="x", pady=5)
            self._controls_panel.pack(in_=self._scroll_container, fill="x", pady=(5, 0))

        self.root.update_idletasks()

    def _relayout_header(self, mode: str):
        self._header_title_frame.pack_forget()
        self._header_status_frame.pack_forget()

        if mode == "desktop":
            self._header.configure(height=52)
            self._header_title_frame.pack(side="left", padx=20, fill="y")
            self._header_status_frame.pack(side="right", padx=20, fill="y")
        else:
            self._header.configure(height=80)
            self._header_title_frame.pack(side="top", fill="x", padx=12, pady=(6, 0))
            self._header_status_frame.pack(side="top", fill="x", padx=12, pady=(4, 6))

    def _relayout_footer(self, mode: str):
        self._footer_lbl.pack_forget()
        if mode == "desktop":
            self._footer.configure(height=32)
            self._footer_lbl.pack(side="left", padx=20, expand=True)
        else:
            self._footer.configure(height=38)
            self._footer_lbl.pack(side="top", pady=8, expand=True)

    def _layout_controls(self, mode: str):
        for btn in [
            self._btn_camera,
            self._btn_analysis,
            self._btn_pause,
            self._btn_reset,
            self._btn_demo,
            self._btn_capture,
        ]:
            btn.pack_forget()
            btn.grid_forget()

        if mode == "desktop":
            # Horizontal line of buttons
            self._btn_camera.pack(side="left", padx=5, pady=6, expand=True, fill="x")
            self._btn_analysis.pack(side="left", padx=5, pady=6, expand=True, fill="x")
            self._btn_pause.pack(side="left", padx=5, pady=6, expand=True, fill="x")
            self._btn_reset.pack(side="left", padx=5, pady=6, expand=True, fill="x")
            self._btn_demo.pack(side="right", padx=5, pady=6, expand=True, fill="x")
            self._btn_capture.pack(side="right", padx=5, pady=6, expand=True, fill="x")
        else:
            # 3x2 Grid for compact/portrait
            self._btn_camera.grid(row=0, column=0, padx=4, pady=4, sticky="ew")
            self._btn_analysis.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
            self._btn_pause.grid(row=1, column=0, padx=4, pady=4, sticky="ew")
            self._btn_reset.grid(row=1, column=1, padx=4, pady=4, sticky="ew")
            self._btn_capture.grid(row=2, column=0, padx=4, pady=4, sticky="ew")
            self._btn_demo.grid(row=2, column=1, padx=4, pady=4, sticky="ew")

            self._controls_panel.grid_columnconfigure(0, weight=1)
            self._controls_panel.grid_columnconfigure(1, weight=1)

    # ── CAMERA UTILITY ──
    def _get_camera_display_size(self, cw: int, ch: int) -> Tuple[int, int]:
        if cw <= 10 or ch <= 10:
            return 640, 480
        img_ratio = 640 / 480
        canvas_ratio = cw / ch
        if img_ratio > canvas_ratio:
            new_w = cw
            new_h = int(cw / img_ratio)
        else:
            new_h = ch
            new_w = int(ch * img_ratio)
        return new_w, new_h

    # ──────────────────────────────────────────
    # INFO POPUP
    # ──────────────────────────────────────────
    def _show_info(self):
        messagebox.showinfo(
            "TRUTHSCAN AI — Information",
            "This application analyzes visible facial and behavioral patterns.\n\n"
            "It is an experimental simulation and cannot reliably determine "
            "whether someone is lying.\n\n"
            "All processing is performed locally on your device.\n"
            "No data is uploaded or transmitted.",
        )

    # ──────────────────────────────────────────
    # CAMERA CONTROL
    # ──────────────────────────────────────────
    def _toggle_camera(self):
        if self._camera_online:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        self._btn_camera.configure(text="⏳  CONNECTING...", state="disabled")
        self._btn_start_cam_inline.configure(text="⏳  CONNECTING...", state="disabled")
        self._cam_offline_status_lbl.configure(text="SEARCHING FOR CAMERA...")
        self.root.update_idletasks()

        def _try_start():
            ok = self._camera.start()
            self.root.after(0, lambda: self._on_camera_started(ok))

        threading.Thread(target=_try_start, daemon=True).start()

    def _on_camera_started(self, success: bool):
        if success:
            self._camera_online = True
            self._btn_camera.configure(text="⏹  STOP CAMERA", state="normal")
            self._btn_start_cam_inline.configure(text="▶  START CAMERA", state="normal")
            self._cam_status_label.configure(
                text="● CAMERA ONLINE", text_color=Colors.SUCCESS
            )
            self._btn_analysis.configure(state="normal")
            self._cam_offline_frame.place_forget()
        else:
            self._btn_camera.configure(text="▶  START CAMERA", state="normal")
            self._btn_start_cam_inline.configure(text="▶  START CAMERA", state="normal")
            self._cam_offline_status_lbl.configure(text="")
            self._cam_status_label.configure(
                text="● CAMERA UNAVAILABLE", text_color=Colors.DANGER
            )
            messagebox.showwarning(
                "Camera Unavailable",
                "Could not access the webcam.\n"
                "Please check that your camera is connected and not in use.",
            )

    def _stop_camera(self):
        self._analysis_active = False
        self._analysis_paused = False
        self._camera.stop()
        self._camera_online = False
        self._btn_camera.configure(text="▶  START CAMERA")
        self._cam_status_label.configure(
            text="● CAMERA OFFLINE", text_color=Colors.DANGER
        )
        self._btn_analysis.configure(
            text="◉  START ANALYSIS",
            state="disabled",
            fg_color=Colors.CARD,
            border_color=Colors.BORDER,
        )
        self._btn_pause.configure(state="disabled", text="⏸  PAUSE")
        self._face_status.configure(text="")
        self._scan_status_label.configure(text="")
        
        # Show Offline Frame and Status Label
        self._cam_offline_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._cam_offline_status_lbl.configure(text="")
        
        self._cam_canvas.delete("all")

    # ──────────────────────────────────────────
    # ANALYSIS CONTROL
    # ──────────────────────────────────────────
    def _toggle_analysis(self):
        if self._analysis_active:
            self._analysis_active = False
            self._analysis_paused = False
            self._btn_analysis.configure(
                text="◉  START ANALYSIS",
                fg_color=Colors.CARD,
                border_color=Colors.BORDER,
            )
            self._btn_pause.configure(state="disabled", text="⏸  PAUSE")
            self._scan_status_label.configure(text="")
        else:
            self._analysis_active = True
            self._analysis_paused = False
            self._analyzer.reset()
            self._btn_analysis.configure(
                text="◉  ANALYSIS ACTIVE",
                fg_color=Colors.PRIMARY,
                border_color=Colors.PRIMARY,
            )
            self._btn_pause.configure(state="normal", text="⏸  PAUSE")

    def _toggle_pause(self):
        if self._analysis_paused:
            self._analysis_paused = False
            self._btn_pause.configure(text="⏸  PAUSE")
            self._btn_analysis.configure(text="◉  ANALYSIS ACTIVE")
            self._scan_status_label.configure(text="ANALYZING BEHAVIOR...", text_color=Colors.LIGHT_BLUE)
        else:
            self._analysis_paused = True
            self._btn_pause.configure(text="▶  RESUME")
            self._btn_analysis.configure(text="◉  PAUSED")
            self._scan_status_label.configure(text="PAUSED", text_color=Colors.GOLD)

    def _reset(self):
        self._analysis_active = False
        self._analysis_paused = False
        self._analyzer.reset()
        self._demo_active = False
        self._demo_step = 0
        if self._demo_overlay:
            self._demo_overlay.destroy()
            self._demo_overlay = None
        self._btn_analysis.configure(
            text="◉  START ANALYSIS",
            fg_color=Colors.CARD,
            border_color=Colors.BORDER,
            state="normal" if self._camera_online else "disabled",
        )
        self._btn_pause.configure(state="disabled", text="⏸  PAUSE")
        self._btn_demo.configure(state="normal")
        self._scan_status_label.configure(text="")
        self._metric_stability.set_value(0)
        self._metric_eye.set_value(0)
        self._metric_expr.set_value(0)
        self._metric_head.set_value(0)
        self._metric_consist.set_value(0)
        self._result_card.update_result(0, 0, False)

    # ──────────────────────────────────────────
    # CAPTURE
    # ──────────────────────────────────────────
    def _capture_result(self):
        try:
            cap_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures")
            os.makedirs(cap_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(cap_dir, f"truthscan_result_{ts}.png")

            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            w = self.root.winfo_width()
            h = self.root.winfo_height()

            img = Image.new("RGB", (w, h))
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            except ImportError:
                draw = ImageDraw.Draw(img)
                draw.rectangle([0, 0, w, h], fill="#0B1220")
                draw.text((w // 2 - 80, h // 2), "TRUTHSCAN AI — Capture", fill="#F8FAFC")

            img.save(path, "PNG")
            messagebox.showinfo(
                "Capture Saved",
                f"Result saved to:\n{path}",
            )
        except Exception as e:
            messagebox.showerror("Capture Error", f"Could not save screenshot:\n{e}")

    # ──────────────────────────────────────────
    # DEMO MODE
    # ──────────────────────────────────────────
    def _start_demo(self):
        if self._demo_active:
            return
        self._demo_active = True
        self._demo_step = 0
        self._btn_demo.configure(state="disabled")

        is_port = self._current_mode in ("portrait", "compact")
        title_pady = (10, 5) if is_port else (30, 10)
        q_pady = (5, 2) if is_port else (10, 4)
        q_font = 13 if is_port else 16
        r_font = 16 if is_port else 20

        self._demo_overlay = ctk.CTkFrame(
            self._cam_panel,
            fg_color=Colors.BG,
            corner_radius=12,
            border_width=1,
            border_color=Colors.PRIMARY,
        )
        self._demo_overlay.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.90)

        self._demo_title = ctk.CTkLabel(
            self._demo_overlay,
            text="◉  DEMO MODE",
            font=_font(12 if is_port else 14, "bold"),
            text_color=Colors.LIGHT_BLUE,
        )
        self._demo_title.pack(pady=title_pady)

        self._demo_q_label = ctk.CTkLabel(
            self._demo_overlay,
            text="QUESTION:",
            font=_font(9 if is_port else 11),
            text_color=Colors.MUTED,
        )
        self._demo_q_label.pack(pady=q_pady)

        self._demo_question = ctk.CTkLabel(
            self._demo_overlay,
            text="",
            font=_font(q_font, "bold"),
            text_color=Colors.WHITE,
            wraplength=320 if is_port else 380,
        )
        self._demo_question.pack(pady=(0, 8 if is_port else 16))

        self._demo_r_label = ctk.CTkLabel(
            self._demo_overlay,
            text="USER RESPONSE:",
            font=_font(9 if is_port else 11),
            text_color=Colors.MUTED,
        )
        self._demo_r_label.pack(pady=(2, 2))

        self._demo_response = ctk.CTkLabel(
            self._demo_overlay,
            text="",
            font=_font(r_font, "bold"),
            text_color=Colors.WHITE,
        )
        self._demo_response.pack(pady=(0, 8 if is_port else 16))

        self._demo_progress = ctk.CTkLabel(
            self._demo_overlay,
            text="",
            font=_font(10 if is_port else 12),
            text_color=Colors.LIGHT_BLUE,
        )
        self._demo_progress.pack(pady=(4, 2))

        self._demo_warning = ctk.CTkLabel(
            self._demo_overlay,
            text="",
            font=_font(9 if is_port else 10),
            text_color=Colors.GOLD,
        )
        self._demo_warning.pack(pady=(4, 5))

        self._run_demo_step()

    def _run_demo_step(self):
        if self._closing or not self._demo_active:
            return

        step = self._demo_step

        if step == 0:
            self._demo_q_label.configure(text="QUESTION:")
            self._demo_question.configure(text='"Did you take the last piece of cake?"')
            self._demo_step = 1
            self.root.after(1800, self._run_demo_step)

        elif step == 1:
            self._demo_r_label.configure(text="USER RESPONSE:")
            self._demo_response.configure(text='"No."')
            self._demo_step = 2
            self.root.after(1500, self._run_demo_step)

        elif step == 2:
            self._demo_progress.configure(text="ANALYZING BEHAVIOR...")
            self._scan_status_label.configure(text="◉ DEMO ANALYSIS...", text_color=Colors.GOLD)
            self._demo_step = 3
            self._demo_anim_tick = 0
            self._animate_demo_metrics()

        elif step == 3:
            self._demo_progress.configure(text="ANALYSIS COMPLETE")
            self._result_card.set_demo_result(82, 43, "Behavioral signals appear unusual.")
            self._demo_warning.configure(text="⚠  AI CAN BE WRONG.")
            self._scan_status_label.configure(text="DEMO COMPLETE", text_color=Colors.GOLD)

    def _animate_demo_metrics(self):
        if self._closing or not self._demo_active:
            return
        t = self._demo_anim_tick
        if t >= 30:
            self._demo_step = 3
            self._run_demo_step()
            return

        progress = t / 30.0
        ease = progress * progress * (3 - 2 * progress)

        self._metric_stability.set_value(72 * ease, Colors.PRIMARY)
        self._metric_eye.set_value(65 * ease, Colors.LIGHT_BLUE)
        self._metric_expr.set_value(78 * ease, Colors.GOLD)
        self._metric_head.set_value(58 * ease, Colors.PRIMARY)
        self._metric_consist.set_value(45 * ease, Colors.ORANGE)

        susp = 82 * ease
        conf = 43 * ease
        self._result_card.update_result(susp, conf, True)

        self._demo_anim_tick += 1
        self.root.after(100, self._animate_demo_metrics)

    # ──────────────────────────────────────────
    # UI TICK (main loop update)
    # ──────────────────────────────────────────
    def _tick_ui(self):
        if self._closing:
            return

        try:
            self._update_camera_display()
            self._update_metrics_display()
        except Exception:
            pass

        self.root.after(33, self._tick_ui)

    def _update_camera_display(self):
        if not self._camera_online:
            return

        frame = self._camera.get_frame()
        if frame is None:
            return

        face = self._camera.get_face_data()
        self._face_detected = face.detected

        # Face status
        if face.detected:
            self._face_status.configure(text="● FACE DETECTED", text_color=Colors.SUCCESS)
        else:
            self._face_status.configure(text="○ SEARCHING FOR FACE", text_color=Colors.GOLD)

        # Run analysis
        if self._analysis_active and not self._analysis_paused and not self._demo_active:
            self._analyzer.update(face)
            self._scan_status_label.configure(text="ANALYZING BEHAVIOR...", text_color=Colors.LIGHT_BLUE)

        # Draw overlays
        display = frame.copy()
        h, w = display.shape[:2]

        if face.detected and face.bbox:
            x1, y1, x2, y2 = face.bbox
            cv2.rectangle(display, (x1, y1), (x2, y2), (235, 99, 37), 2)
            cl = 18
            color = (235, 99, 37)
            cv2.line(display, (x1, y1), (x1 + cl, y1), color, 2)
            cv2.line(display, (x1, y1), (x1, y1 + cl), color, 2)
            cv2.line(display, (x2, y1), (x2 - cl, y1), color, 2)
            cv2.line(display, (x2, y1), (x2, y1 + cl), color, 2)
            cv2.line(display, (x1, y2), (x1 + cl, y2), color, 2)
            cv2.line(display, (x1, y2), (x1, y2 - cl), color, 2)
            cv2.line(display, (x2, y2), (x2 - cl, y2), color, 2)
            cv2.line(display, (x2, y2), (x2, y2 - cl), color, 2)

            if face.landmarks:
                key_indices = [
                    1, 33, 263, 61, 291, 13, 14,
                    10, 152, 234, 454,
                    159, 145, 386, 374,
                ]
                for idx in key_indices:
                    if idx < len(face.landmarks):
                        px, py = face.landmarks[idx]
                        cv2.circle(display, (px, py), 2, (248, 189, 56), -1)

        # Scanning line overlay
        if self._analysis_active and not self._analysis_paused and not self._demo_active:
            self._scan_y += 3.5
            if self._scan_y > h:
                self._scan_y = 0
            sy = int(self._scan_y)
            overlay = display.copy()
            cv2.line(overlay, (0, sy), (w, sy), (235, 99, 37), 2)
            for offset in range(1, 15):
                alpha = max(0, 1.0 - offset / 15.0) * 0.15
                line_y = sy + offset
                if 0 <= line_y < h:
                    cv2.line(overlay, (0, line_y), (w, line_y), (235, 99, 37), 1)
                line_y = sy - offset
                if 0 <= line_y < h:
                    cv2.line(overlay, (0, line_y), (w, line_y), (235, 99, 37), 1)
            cv2.addWeighted(overlay, 0.4, display, 0.6, 0, display)

        # Image processing & display sizing
        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)

        cw = self._cam_canvas.winfo_width()
        ch = self._cam_canvas.winfo_height()
        if cw > 10 and ch > 10:
            new_w, new_h = self._get_camera_display_size(cw, ch)
            pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)

        self._cam_photo = ImageTk.PhotoImage(pil_img)
        self._cam_canvas.delete("all")
        self._cam_canvas.create_image(
            cw // 2, ch // 2, image=self._cam_photo, anchor="center"
        )

    def _update_metrics_display(self):
        if self._demo_active:
            return

        m = self._analyzer.metrics

        if self._analysis_active and not self._analysis_paused:
            def _bar_color(val, invert=False):
                v = (100 - val) if invert else val
                if v < 30:
                    return Colors.SUCCESS
                elif v < 60:
                    return Colors.GOLD
                elif v < 80:
                    return Colors.ORANGE
                else:
                    return Colors.DANGER

            self._metric_stability.set_value(m.facial_stability, _bar_color(m.facial_stability, invert=True))
            self._metric_eye.set_value(m.eye_movement, _bar_color(m.eye_movement))
            self._metric_expr.set_value(m.expression_change, _bar_color(m.expression_change))
            self._metric_head.set_value(m.head_movement, _bar_color(m.head_movement))
            self._metric_consist.set_value(m.behavioral_consistency, _bar_color(m.behavioral_consistency, invert=True))
            self._result_card.update_result(m.suspicion_score, m.ai_confidence, True)
        elif not self._analysis_active:
            self._result_card.update_result(0, 0, False)

    # ──────────────────────────────────────────
    # CLOSE
    # ──────────────────────────────────────────
    def _on_close(self):
        self._closing = True
        self._analysis_active = False
        try:
            self._camera.release()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    # ──────────────────────────────────────────
    # RUN
    # ──────────────────────────────────────────
    def run(self):
        self.root.mainloop()


# ══════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = TruthScanApp()
    app.run()
