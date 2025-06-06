from capture import detect_motion_and_capture
from recognize import recognize_plate
import time

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
        else:
            print("[FAILURE] No plate detected.")

        time.sleep(2)  # short pause to avoid rapid repeat triggers

if __name__ == "__main__":
    main()
