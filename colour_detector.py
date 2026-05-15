import cv2 as cv
import numpy as np
import time
import pygame

from Scenes import Game


def get_camera():
    for i in range(5):
        cap = cv.VideoCapture(i, cv.CAP_DSHOW)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("Using camera", i)
                return i

        cap.release()


def get_color_name(h, s, v):

    if v < 40:
        return "other"

    if s < 50:
        return "other"

    if (0 <= h <= 10) or (170 <= h <= 179):
        return "red"

    elif (20 <= h <= 35) and (s > 150):
        return "yellow"

    elif 36 <= h <= 85:
        return "green"

    elif 86 <= h <= 130:
        return "blue"

    else:
        return "other"


def color_to_bgr(color_name):

    if color_name == "red":
        return (0, 0, 255)

    elif color_name == "yellow":
        return (0, 255, 255)

    elif color_name == "green":
        return (0, 255, 0)

    elif color_name == "blue":
        return (255, 0, 0)

    else:
        return (255, 255, 255)


class ColourDetectorScene(Game):

    def __init__(self, screen, target_colour):
        super().__init__(screen)

        self.target_colour = target_colour

        self.cap = cv.VideoCapture(get_camera())
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        self.starting_time = time.time()

        self.finished = False

        self.font = pygame.font.SysFont("Arial", 60)

    def handle_events(self, events):

        for event in events:

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.return_state = ("quit", False)

    def draw(self):

        ret, frame = self.cap.read()

        if not ret:
            return

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        h, w, _ = frame.shape

        cx, cy = w // 2, h // 2

        offset = 60

        region = hsv[
            cy-offset:cy+offset,
            cx-offset:cx+offset
        ]

        h_mean = int(np.mean(region[:, :, 0]))
        s_mean = int(np.mean(region[:, :, 1]))
        v_mean = int(np.mean(region[:, :, 2]))

        detected_colour = get_color_name(
            h_mean,
            s_mean,
            v_mean
        )

        # ציור
        cv.circle(frame, (cx, cy), offset, (0, 0, 0), 2)

        cv.putText(
            frame,
            detected_colour,
            (cx - offset // 2, cy),
            cv.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv.putText(
            frame,
            f"Target: {self.target_colour}",
            (10, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.8,
            color_to_bgr(self.target_colour),
            2
        )

        elapsed = time.time() - self.starting_time

        cv.putText(
            frame,
            f"Time: {elapsed:.2f}s",
            (w - 180, 30),
            cv.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 0),
            2
        )

        cv.imshow(
            "Center Color Detection",
            frame
        )

        cv.waitKey(1)

        # הצלחה
        if detected_colour == self.target_colour:

            self.finished = True

            self.return_state = (
                elapsed,
                False
            )

    def __del__(self):

        if hasattr(self, "cap"):
            self.cap.release()

        cv.destroyAllWindows()