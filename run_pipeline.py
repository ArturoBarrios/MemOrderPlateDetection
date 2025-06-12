from capture import detect_motion_and_capture
from recognize import recognize_plate
import time
import requests
import os

AUDIO_URL = os.environ.get("AUDIO_URL", "localhost:6000")

def main():
    print("🚘 Drive-thru plate reader with motion detection ready...")

    while True:
        image_path = detect_motion_and_capture()
        if not image_path:
            continue

        print(f"[INFO] Motion detected. Captured image: {image_path}")
        result = recognize_plate(image_path)
        if result:
            print(f"[SUCCESS] Plate Detected: {result['plate']} (score: {result['score']})")
            print(f"Bounding box: {result['box']}")
            try:
                url = f"http://{AUDIO_URL}/trigger-audio"
                response = requests.post(url, json=result)
                print(f"[AUDIO SERVER] Status: {response.status_code}")
                print(f"[AUDIO SERVER] Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Could not reach audio server: {e}")
            
        else:
            print("[FAILURE] No plate detected.")

        time.sleep(2)  # short pause to avoid rapid repeat triggers

if __name__ == "__main__":
    main()
