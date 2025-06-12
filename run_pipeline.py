from capture import detect_motion_and_capture
from recognize import recognize_plate
import time
import requests
import os

AUDIO_URL = os.environ.get("AUDIO_URL", "http://127.0.0.1:8000").rstrip("/")
print(f"[DEBUG] AUDIO_URL is: '{AUDIO_URL}'")



def send_plate_to_backend(plate: str):
    BACKEND_URL = os.environ.get("BACKEND_GRAPHQL_URL", "http://127.0.0.1:4000/graphql")

    query = """
    query SendPlate($plate: String!) {
        plateRecorded(plateId: $plate)
    }
    """

    payload = {
        "query": query,
        "variables": {"plate": plate}
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        print(f"[BACKEND] Sent plate '{plate}' successfully.")
        print(f"[BACKEND] Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not reach backend: {e}")

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
                url = f"{AUDIO_URL}/trigger-audio"

                response = requests.post(url, json=result)
                print(f"[AUDIO SERVER] Status: {response.status_code}")
                print(f"[AUDIO SERVER] Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Could not reach audio server: {e}")
            try:
                send_plate_to_backend(result["plate"])
            except Exception as e:
                print(f"[ERROR] Failed to send plate to backend: {e}")
            
        else:            
            print("[FAILURE] No plate detected.")

        time.sleep(2)  # short pause to avoid rapid repeat triggers

if __name__ == "__main__":
    main()
