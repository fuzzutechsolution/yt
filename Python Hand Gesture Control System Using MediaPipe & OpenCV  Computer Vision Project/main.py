import customtkinter as ctk
import cv2
import math
import threading
import time
import os
import sys

from PIL import Image
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


# ============================================================
# MEDIAPIPE SAFE IMPORT
# ============================================================

try:
    # Method 1: Standard MediaPipe import
    import mediapipe as mp

    if hasattr(mp, "solutions"):
        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils

    else:
        raise ImportError("mediapipe.solutions not available")

except Exception:
    try:
        # Method 2: Direct Legacy Import
        from mediapipe.python.solutions import hands as mp_hands
        from mediapipe.python.solutions import drawing_utils as mp_drawing

    except Exception as error:

        print("\n" + "=" * 60)
        print("MEDIAPIPE IMPORT ERROR")
        print("=" * 60)
        print(error)

        print("\nPossible fixes:")
        print("1. Check project folder for mediapipe.py")
        print("2. Delete __pycache__ folder")
        print("3. Reinstall MediaPipe:")
        print()
        print("python -m pip uninstall mediapipe -y")
        print("python -m pip install mediapipe==0.10.21")
        print()

        sys.exit()


# ============================================================
# CUSTOMTKINTER CONFIGURATION
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# MAIN APPLICATION
# ============================================================

class HandVolumeController(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.title("AI Hand Gesture Volume Controller")

        self.geometry("540x900")

        self.minsize(500, 820)

        self.configure(fg_color="#050B14")


        # ----------------------------------------------------
        # CAMERA VARIABLES
        # ----------------------------------------------------

        self.running = False

        self.cap = None

        self.camera_thread = None


        # ----------------------------------------------------
        # GESTURE VARIABLES
        # ----------------------------------------------------

        self.last_mute_time = 0

        self.is_muted = False

        self.current_volume = 0


        # Volume smoothing

        self.smoothed_volume = 0

        self.smoothing_factor = 0.20


        # ----------------------------------------------------
        # MEDIAPIPE
        # ----------------------------------------------------

        self.hands = mp_hands.Hands(

            static_image_mode=False,

            max_num_hands=1,

            model_complexity=1,

            min_detection_confidence=0.65,

            min_tracking_confidence=0.65

        )


        # ----------------------------------------------------
        # WINDOWS AUDIO
        # ----------------------------------------------------

        try:

            self.volume = self.setup_audio()

            volume_range = self.volume.GetVolumeRange()

            self.min_volume = volume_range[0]

            self.max_volume = volume_range[1]


            # Get current Windows volume

            current_scalar = (
                self.volume.GetMasterVolumeLevelScalar()
            )

            self.current_volume = int(
                current_scalar * 100
            )

            self.smoothed_volume = (
                self.current_volume
            )


        except Exception as error:

            print("Windows Audio Error:", error)

            self.volume = None

            self.min_volume = -65.25

            self.max_volume = 0.0


        # ----------------------------------------------------
        # CREATE UI
        # ----------------------------------------------------

        self.create_ui()


        # Initial volume UI

        self.update_volume_ui(
            self.current_volume
        )


        # Close protocol

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )


    # ========================================================
    # AUDIO SETUP
    # ========================================================

    def setup_audio(self):

        device = AudioUtilities.GetSpeakers()


        interface = device.Activate(

            IAudioEndpointVolume._iid_,

            CLSCTX_ALL,

            None

        )


        volume = cast(

            interface,

            POINTER(IAudioEndpointVolume)

        )


        return volume


    # ========================================================
    # CREATE UI
    # ========================================================

    def create_ui(self):

        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(

            self,

            height=100,

            corner_radius=0,

            fg_color="#08111F"

        )

        header.pack(

            fill="x"

        )


        title = ctk.CTkLabel(

            header,

            text="AI HAND GESTURE",

            font=ctk.CTkFont(

                size=27,

                weight="bold"

            ),

            text_color="white"

        )

        title.pack(

            pady=(17, 0)

        )


        subtitle = ctk.CTkLabel(

            header,

            text="VOLUME CONTROLLER",

            font=ctk.CTkFont(

                size=15,

                weight="bold"

            ),

            text_color="#00A8FF"

        )

        subtitle.pack()


        # ====================================================
        # CAMERA CARD
        # ====================================================

        self.camera_card = ctk.CTkFrame(

            self,

            corner_radius=18,

            fg_color="#08111F",

            border_width=1,

            border_color="#18334F"

        )


        self.camera_card.pack(

            fill="both",

            expand=True,

            padx=18,

            pady=18

        )


        self.camera_label = ctk.CTkLabel(

            self.camera_card,

            text="CAMERA OFF",

            font=ctk.CTkFont(

                size=24,

                weight="bold"

            ),

            text_color="#536B82"

        )


        self.camera_label.pack(

            fill="both",

            expand=True,

            padx=10,

            pady=10

        )


        # ====================================================
        # STATUS LABEL
        # ====================================================

        self.status_label = ctk.CTkLabel(

            self,

            text="● SYSTEM READY",

            font=ctk.CTkFont(

                size=14,

                weight="bold"

            ),

            text_color="#2ECC71"

        )


        self.status_label.pack(

            pady=(0, 8)

        )


        # ====================================================
        # VOLUME CARD
        # ====================================================

        volume_card = ctk.CTkFrame(

            self,

            corner_radius=18,

            fg_color="#08111F",

            border_width=1,

            border_color="#18334F"

        )


        volume_card.pack(

            fill="x",

            padx=18,

            pady=(0, 12)

        )


        volume_title = ctk.CTkLabel(

            volume_card,

            text="SYSTEM VOLUME",

            font=ctk.CTkFont(

                size=13,

                weight="bold"

            ),

            text_color="#8CA6BD"

        )


        volume_title.pack(

            pady=(14, 0)

        )


        self.volume_percentage = ctk.CTkLabel(

            volume_card,

            text="0%",

            font=ctk.CTkFont(

                size=42,

                weight="bold"

            ),

            text_color="#00A8FF"

        )


        self.volume_percentage.pack()


        self.volume_bar = ctk.CTkProgressBar(

            volume_card,

            height=14,

            corner_radius=10,

            progress_color="#00A8FF",

            fg_color="#15283B"

        )


        self.volume_bar.pack(

            fill="x",

            padx=28,

            pady=(3, 18)

        )


        self.volume_bar.set(0)


        # ====================================================
        # GESTURE STATUS
        # ====================================================

        self.gesture_label = ctk.CTkLabel(

            self,

            text="GESTURE: WAITING",

            font=ctk.CTkFont(

                size=14,

                weight="bold"

            ),

            text_color="#AFC4D6"

        )


        self.gesture_label.pack(

            pady=4

        )


        # ====================================================
        # BUTTONS
        # ====================================================

        button_frame = ctk.CTkFrame(

            self,

            fg_color="transparent"

        )


        button_frame.pack(

            fill="x",

            padx=18,

            pady=(8, 18)

        )


        self.start_button = ctk.CTkButton(

            button_frame,

            text="START CAMERA",

            height=48,

            corner_radius=12,

            font=ctk.CTkFont(

                size=15,

                weight="bold"

            ),

            fg_color="#0078D7",

            hover_color="#005FA8",

            command=self.start_camera

        )


        self.start_button.pack(

            side="left",

            expand=True,

            fill="x",

            padx=(0, 5)

        )


        self.stop_button = ctk.CTkButton(

            button_frame,

            text="STOP CAMERA",

            height=48,

            corner_radius=12,

            font=ctk.CTkFont(

                size=15,

                weight="bold"

            ),

            fg_color="#C0392B",

            hover_color="#922B21",

            command=self.stop_camera

        )


        self.stop_button.pack(

            side="left",

            expand=True,

            fill="x",

            padx=(5, 0)

        )


    # ========================================================
    # START CAMERA
    # ========================================================

    def start_camera(self):

        if self.running:

            return


        # Windows DirectShow camera backend

        self.cap = cv2.VideoCapture(

            0,

            cv2.CAP_DSHOW

        )


        if not self.cap.isOpened():

            self.status_label.configure(

                text="● CAMERA ERROR",

                text_color="#E74C3C"

            )

            return


        # Camera resolution

        self.cap.set(

            cv2.CAP_PROP_FRAME_WIDTH,

            640

        )


        self.cap.set(

            cv2.CAP_PROP_FRAME_HEIGHT,

            480

        )


        self.running = True


        self.status_label.configure(

            text="● AI TRACKING ACTIVE",

            text_color="#2ECC71"

        )


        self.start_button.configure(

            state="disabled"

        )


        self.camera_thread = threading.Thread(

            target=self.camera_loop,

            daemon=True

        )


        self.camera_thread.start()


    # ========================================================
    # CAMERA LOOP
    # ========================================================

    def camera_loop(self):

        while self.running:

            success, frame = self.cap.read()


            if not success:

                time.sleep(0.01)

                continue


            # ------------------------------------------------
            # MIRROR CAMERA
            # ------------------------------------------------

            frame = cv2.flip(

                frame,

                1

            )


            # ------------------------------------------------
            # RGB CONVERSION
            # ------------------------------------------------

            rgb_frame = cv2.cvtColor(

                frame,

                cv2.COLOR_BGR2RGB

            )


            # Improve MediaPipe performance

            rgb_frame.flags.writeable = False


            results = self.hands.process(

                rgb_frame

            )


            rgb_frame.flags.writeable = True


            gesture_text = "NO HAND DETECTED"


            # ------------------------------------------------
            # HAND DETECTED
            # ------------------------------------------------

            if results.multi_hand_landmarks:

                hand_landmarks = (

                    results.multi_hand_landmarks[0]

                )


                # --------------------------------------------
                # DRAW HAND LANDMARKS
                # --------------------------------------------

                mp_drawing.draw_landmarks(

                    frame,

                    hand_landmarks,

                    mp_hands.HAND_CONNECTIONS

                )


                height, width, _ = frame.shape


                # --------------------------------------------
                # GET LANDMARKS
                # --------------------------------------------

                thumb = (

                    hand_landmarks.landmark[4]

                )


                index = (

                    hand_landmarks.landmark[8]

                )


                wrist = (

                    hand_landmarks.landmark[0]

                )


                middle_mcp = (

                    hand_landmarks.landmark[9]

                )


                # --------------------------------------------
                # PIXEL COORDINATES
                # --------------------------------------------

                thumb_x = int(

                    thumb.x * width

                )


                thumb_y = int(

                    thumb.y * height

                )


                index_x = int(

                    index.x * width

                )


                index_y = int(

                    index.y * height

                )


                wrist_x = int(

                    wrist.x * width

                )


                wrist_y = int(

                    wrist.y * height

                )


                middle_x = int(

                    middle_mcp.x * width

                )


                middle_y = int(

                    middle_mcp.y * height

                )


                # --------------------------------------------
                # DRAW CONTROL POINTS
                # --------------------------------------------

                cv2.circle(

                    frame,

                    (thumb_x, thumb_y),

                    10,

                    (0, 200, 255),

                    -1

                )


                cv2.circle(

                    frame,

                    (index_x, index_y),

                    10,

                    (0, 200, 255),

                    -1

                )


                # --------------------------------------------
                # DRAW LINE
                # --------------------------------------------

                cv2.line(

                    frame,

                    (thumb_x, thumb_y),

                    (index_x, index_y),

                    (255, 255, 255),

                    3

                )


                center_x = (

                    thumb_x + index_x

                ) // 2


                center_y = (

                    thumb_y + index_y

                ) // 2


                cv2.circle(

                    frame,

                    (center_x, center_y),

                    7,

                    (0, 255, 0),

                    -1

                )


                # --------------------------------------------
                # FINGER DISTANCE
                # --------------------------------------------

                finger_distance = math.hypot(

                    index_x - thumb_x,

                    index_y - thumb_y

                )


                # --------------------------------------------
                # HAND SIZE
                # --------------------------------------------

                hand_size = math.hypot(

                    middle_x - wrist_x,

                    middle_y - wrist_y

                )


                # Avoid division by zero

                if hand_size < 1:

                    hand_size = 1


                # --------------------------------------------
                # NORMALIZED DISTANCE
                # --------------------------------------------

                normalized_distance = (

                    finger_distance / hand_size

                )


                # =================================================
                # PINCH GESTURE
                # =================================================

                if normalized_distance < 0.25:

                    gesture_text = (

                        "PINCH → MUTE / UNMUTE"

                    )


                    current_time = time.time()


                    if (

                        current_time

                        - self.last_mute_time

                        > 1.5

                    ):


                        self.is_muted = (

                            not self.is_muted

                        )


                        if self.volume:

                            self.volume.SetMute(

                                self.is_muted,

                                None

                            )


                        self.last_mute_time = (

                            current_time

                        )


                        if self.is_muted:

                            self.after(

                                0,

                                self.update_gesture_ui,

                                "GESTURE: MUTED"

                            )

                        else:

                            self.after(

                                0,

                                self.update_gesture_ui,

                                "GESTURE: UNMUTED"

                            )


                # =================================================
                # VOLUME CONTROL
                # =================================================

                else:

                    gesture_text = (

                        "MOVE FINGERS → CONTROL VOLUME"

                    )


                    # Normalized range

                    min_distance = 0.30

                    max_distance = 1.80


                    normalized_distance = max(

                        min_distance,

                        min(

                            normalized_distance,

                            max_distance

                        )

                    )


                    raw_volume = (

                        (

                            normalized_distance

                            - min_distance

                        )

                        /

                        (

                            max_distance

                            - min_distance

                        )

                        * 100

                    )


                    # --------------------------------------------
                    # VOLUME SMOOTHING
                    # --------------------------------------------

                    self.smoothed_volume = (

                        self.smoothing_factor

                        * raw_volume

                        +

                        (

                            1

                            - self.smoothing_factor

                        )

                        * self.smoothed_volume

                    )


                    volume_percent = int(

                        self.smoothed_volume

                    )


                    volume_percent = max(

                        0,

                        min(

                            volume_percent,

                            100

                        )

                    )


                    self.current_volume = (

                        volume_percent

                    )


                    # --------------------------------------------
                    # SET WINDOWS VOLUME
                    # --------------------------------------------

                    if self.volume:

                        self.volume.SetMasterVolumeLevelScalar(

                            volume_percent / 100,

                            None

                        )


                    # --------------------------------------------
                    # UPDATE UI
                    # --------------------------------------------

                    self.after(

                        0,

                        self.update_volume_ui,

                        volume_percent

                    )


                    # --------------------------------------------
                    # CAMERA TEXT
                    # --------------------------------------------

                    cv2.putText(

                        frame,

                        f"VOLUME: {volume_percent}%",

                        (20, 45),

                        cv2.FONT_HERSHEY_SIMPLEX,

                        1,

                        (0, 200, 255),

                        2,

                        cv2.LINE_AA

                    )


            # ------------------------------------------------
            # UPDATE GESTURE UI
            # ------------------------------------------------

            self.after(

                0,

                self.update_gesture_ui,

                f"GESTURE: {gesture_text}"

            )


            # ------------------------------------------------
            # FPS
            # ------------------------------------------------

            cv2.putText(

                frame,

                "AI HAND TRACKING",

                (20, frame.shape[0] - 20),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.7,

                (0, 255, 0),

                2,

                cv2.LINE_AA

            )


            # ------------------------------------------------
            # CONVERT CAMERA FRAME
            # ------------------------------------------------

            display_frame = cv2.cvtColor(

                frame,

                cv2.COLOR_BGR2RGB

            )


            pil_image = Image.fromarray(

                display_frame

            )


            # Maintain aspect ratio

            pil_image.thumbnail(

                (480, 460),

                Image.Resampling.LANCZOS

            )


            ctk_image = ctk.CTkImage(

                light_image=pil_image,

                dark_image=pil_image,

                size=pil_image.size

            )


            # ------------------------------------------------
            # UPDATE CAMERA
            # ------------------------------------------------

            self.after(

                0,

                self.update_camera,

                ctk_image

            )


            time.sleep(0.01)


    # ========================================================
    # UPDATE CAMERA
    # ========================================================

    def update_camera(self, image):

        if not self.running:

            return


        self.camera_label.configure(

            image=image,

            text=""

        )


        # Prevent garbage collection

        self.camera_label.image = image


    # ========================================================
    # UPDATE VOLUME UI
    # ========================================================

    def update_volume_ui(

        self,

        volume_percent

    ):

        volume_percent = max(

            0,

            min(

                int(volume_percent),

                100

            )

        )


        self.volume_percentage.configure(

            text=f"{volume_percent}%"

        )


        self.volume_bar.set(

            volume_percent / 100

        )


    # ========================================================
    # UPDATE GESTURE UI
    # ========================================================

    def update_gesture_ui(

        self,

        text

    ):

        self.gesture_label.configure(

            text=text

        )


    # ========================================================
    # STOP CAMERA
    # ========================================================

    def stop_camera(self):

        self.running = False


        if self.cap is not None:

            try:

                self.cap.release()

            except Exception:

                pass


            self.cap = None


        self.camera_label.configure(

            image=None,

            text="CAMERA OFF"

        )


        self.camera_label.image = None


        self.status_label.configure(

            text="● SYSTEM READY",

            text_color="#2ECC71"

        )


        self.gesture_label.configure(

            text="GESTURE: WAITING"

        )


        self.start_button.configure(

            state="normal"

        )


    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_app(self):

        self.running = False


        if self.cap is not None:

            try:

                self.cap.release()

            except Exception:

                pass


        try:

            self.hands.close()

        except Exception:

            pass


        self.destroy()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app = HandVolumeController()

    app.mainloop()