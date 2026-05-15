import numpy as np
import cv2 as cv
from FaceMeshModule import FaceMeshGenerator
from utils import DrawingUtils
from Scenes import Game
import pygame

import time


def get_camera():

    for i in range(5):

        cap = cv.VideoCapture(i, cv.CAP_DSHOW)

        if cap.isOpened():

            ret, frame = cap.read()

            if ret:
                print("Using camera", i)
                return i

        cap.release()

    raise Exception("No working camera found")


class BlinkCounterScene(Game):

    def __init__(self, screen):

        super().__init__(screen)

        # -----------------------------
        # CAMERA
        # -----------------------------
        self.cap = cv.VideoCapture(get_camera())

        self.cap.set(cv.CAP_PROP_FPS, 120)

        # -----------------------------
        # FACEMESH
        # -----------------------------
        self.generator = FaceMeshGenerator()

        # -----------------------------
        # EYES
        # -----------------------------
        self.RIGHT_EYE = [
            33, 7, 163, 144, 145, 153,
            154, 155, 133, 173, 157,
            158, 159, 160, 161, 246
        ]

        self.LEFT_EYE = [
            362, 382, 381, 380, 374,
            373, 390, 249, 263, 466,
            388, 387, 386, 385, 384, 398
        ]

        self.RIGHT_EYE_EAR = [
            33, 159, 158,
            133, 153, 145
        ]

        self.LEFT_EYE_EAR = [
            362, 380, 374,
            263, 386, 385
        ]

        # -----------------------------
        # BLINK SETTINGS
        # -----------------------------
        self.ear_threshold = 0.3
        self.consec_frames = 1

        self.blink_counter = 0
        self.frame_counter = 0

        # -----------------------------
        # COLORS
        # -----------------------------
        self.GREEN_COLOR = (86, 241, 13)
        self.RED_COLOR = (30, 46, 209)

        # -----------------------------
        # TIMER
        # -----------------------------
        self.start_time = time.time()

        self.duration = 15

    def eye_aspect_ratio(
        self,
        eye_landmarks,
        landmarks
    ):

        A = np.linalg.norm(
            np.array(landmarks[eye_landmarks[1]])
            - np.array(landmarks[eye_landmarks[5]])
        )

        B = np.linalg.norm(
            np.array(landmarks[eye_landmarks[2]])
            - np.array(landmarks[eye_landmarks[4]])
        )

        C = np.linalg.norm(
            np.array(landmarks[eye_landmarks[0]])
            - np.array(landmarks[eye_landmarks[3]])
        )

        return (A + B) / (2.0 * C)

    def update_blink_count(self, ear):

        if ear < self.ear_threshold:

            self.frame_counter += 1

        else:

            if self.frame_counter >= self.consec_frames:
                self.blink_counter += 1

            self.frame_counter = 0

    def set_colors(self, ear):

        if ear < self.ear_threshold:
            return self.RED_COLOR

        return self.GREEN_COLOR

    def draw_eye_landmarks(
        self,
        frame,
        landmarks,
        eye_landmarks,
        color
    ):

        for loc in eye_landmarks:

            cv.circle(
                frame,
                landmarks[loc],
                4,
                color,
                cv.FILLED
            )

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:
                pass

    def draw(self):

        ret, frame = self.cap.read()

        if not ret:
            return

        frame, face_landmarks = self.generator.create_face_mesh(
            frame,
            draw=False
        )

        if len(face_landmarks) > 0:

            right_ear = self.eye_aspect_ratio(
                self.RIGHT_EYE_EAR,
                face_landmarks
            )

            left_ear = self.eye_aspect_ratio(
                self.LEFT_EYE_EAR,
                face_landmarks
            )

            ear = (right_ear + left_ear) / 2.0

            self.update_blink_count(ear)

            color = self.set_colors(ear)

            self.draw_eye_landmarks(
                frame,
                face_landmarks,
                self.RIGHT_EYE,
                color
            )

            self.draw_eye_landmarks(
                frame,
                face_landmarks,
                self.LEFT_EYE,
                color
            )

            DrawingUtils.draw_text_with_bg(
                frame,
                f"Blinks: {self.blink_counter}",
                (0, 60),
                font_scale=2,
                thickness=3,
                bg_color=color,
                text_color=(0, 0, 0)
            )

        # TIMER
        elapsed = time.time() - self.start_time

        remaining = max(
            0,
            self.duration - elapsed
        )

        cv.putText(
            frame,
            f"Time: {remaining:.1f}",
            (20, 120),
            cv.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        resized_frame = cv.resize(
            frame,
            (1280, 720)
        )

        cv.imshow(
            "Blink Counter",
            resized_frame
        )

        cv.waitKey(1)

        # END GAME
        if elapsed >= self.duration:

            self.return_state = (
                self.blink_counter,
                True
            )

    def __del__(self):

        if hasattr(self, "cap"):
            self.cap.release()

        cv.destroyAllWindows()