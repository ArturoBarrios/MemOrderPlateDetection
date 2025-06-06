import cv2
import os
import time
from datetime import datetime

import os
import time
import platform
import numpy as np
from datetime import datetime
import cv2

def get_camera_frame():
    system = platform.system()

    if system == "Darwin":
        cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
        if not cap.isOpened():
            raise RuntimeError("Webcam not accessible.")
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError("Failed to capture frame on macOS.")
        return frame

    elif system == "Linux":
        try:
            from picamera2 import Picamera2
            picam2 = Picamera2()
            picam2.start()
            time.sleep(1)
            frame = picam2.capture_array()
            picam2.stop()
            return frame
        except ImportError:
            raise RuntimeError("picamera2 not installed or usable.")

    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def detect_motion_and_capture(threshold=500000, delay=0.2):
    os.makedirs("images", exist_ok=True)

    try:
        prev = get_camera_frame()
        prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
        time.sleep(delay)
        curr = get_camera_frame()
        curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        return None

    diff = cv2.absdiff(prev_gray, curr_gray)
    score = diff.sum()

    if score > threshold:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join("images", f"plate_motion_{timestamp}.jpg")
        cv2.imwrite(path, curr)
        return path

    return None
