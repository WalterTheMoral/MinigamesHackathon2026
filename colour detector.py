import cv2 as cv
import numpy as np
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

def get_color_name(h, s, v):

    # לא צבעוני / לא מספיק מידע
    if v < 40:
        return "Other"
    if s < 50:
        return "Other"

    # 🔴 Red (שני טווחים בגלל HSV wrap)
    if (0 <= h <= 10) or (170 <= h <= 179):
        return "bed"

    # 🟡 Yellow
    elif (20 <= h <= 35) and (s > 150):
        return "yellow"

    # 🟢 Green
    elif 36 <= h <= 85:
        return "green"

    # 🔵 Blue
    elif 86 <= h <= 130:
        return "blue"

    # כל השאר
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
    
def colour_detector(colour):
    starting_time = time.time()
    cap = cv.VideoCapture(get_camera())
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        h, w, _ = frame.shape

        # 🔥 מרכז הפריים
        cx, cy = w // 2, h // 2

        # אפשר גם "אזור קטן" במקום פיקסל 
        offset = 60
        region = hsv[cy-offset:cy+offset, cx-offset:cx+offset]

        # ממוצע כדי לייצב רעש
        h_mean = int(np.mean(region[:, :, 0]))
        s_mean = int(np.mean(region[:, :, 1]))
        v_mean = int(np.mean(region[:, :, 2]))

        colour_ditected = get_color_name(h_mean, s_mean, v_mean)

        # ציור
        cv.circle(frame, (cx, cy), offset, (0, 0, 0), 2)
        cv.putText(frame, colour_ditected, (cx - offset // 2, cy),
                    cv.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv.putText(frame, f"Target: {colour}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 0.8, color_to_bgr(colour), 2)

        cv.putText(frame, f"Time: {time.time() - starting_time:.2f}s", (w - 180, 30), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)


        cv.imshow("Center Color Detection", frame)

        if cv.waitKey(1) & 0xFF == ord(' '):
            break

        #print(f"{h_mean=}, {s_mean=}, {v_mean=}, Detected: {colour_ditected}")
        if(colour == colour_ditected):
            return time.time() - starting_time


    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    print(colour_detector(""))