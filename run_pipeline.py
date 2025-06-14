from capture import detect_motion_and_capture
from recognize import recognize_plate
import time
import requests
import os
import json

AUDIO_URL = os.environ.get("AUDIO_URL", "http://127.0.0.1:8000").rstrip("/")
print(f"[DEBUG] AUDIO_URL is: '{AUDIO_URL}'")



def send_plate_to_backend(plate: str, image_path: str):
    BACKEND_URL = os.environ.get("BACKEND_GRAPHQL_URL")

    query = """
    mutation SendPlate($plate: String!, $image: Upload!) {
        plateRecorded(plate: $plate, image: $image)
    }
    """

    operations = {
        "query": query,
        "variables": {"plate": plate, "image": None}
    }

    map_data = {
        "0": ["variables.image"]
    }

    try:
        with open(image_path, 'rb') as f:
            files = {
                'operations': (None, json.dumps(operations), 'application/json'),
                'map': (None, json.dumps(map_data), 'application/json'),
                '0': (os.path.basename(image_path), f, 'image/jpeg'),
            }

            response = requests.post(BACKEND_URL, files=files)
            print(f"[BACKEND] Raw response: {response.text}")
            response.raise_for_status()
            print(f"[BACKEND] Sent plate '{plate}' successfully.")
            print(f"[BACKEND] Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Could not reach backend: {e}")
    except FileNotFoundError:
        print(f"[ERROR] Image file not found at {image_path}")

def main():
    print("🚘 Drive-thru plate reader with motion detection ready...")

    while True:
        image_path = detect_motion_and_capture()
        if not image_path:
            continue

        print(f"[INFO] Motion detected. Captured image: {image_path}")
        result = recognize_plate(image_path)
        if result or os.environ.get("ENVIRONMENT")=='DEVELOPMENT' :            
            if(os.environ.get("ENVIRONMENT")=='STAGING'): 
                print(f"[SUCCESS] Plate Detected: {result['plate']} (score: {result['score']})")
                print(f"Bounding box: {result['box']}")
            try:
                url = f"{AUDIO_URL}/trigger-audio"
                print("url: ", url)
                print("environment: ",  os.environ.get("ENVIRONMENT"))                
                if( os.environ.get("ENVIRONMENT")=='DEVELOPMENT'):
                    plate = 'ABC123'
                    image_path = "images/test-image.jpg"
                else: 
                    plate = result['plate']                    
                response = requests.post(url, json={"plate": plate})
                print(f"[AUDIO SERVER] Status: {response.status_code}")
                print(f"[AUDIO SERVER] Response: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Could not reach audio server: {e}")
            try:
                send_plate_to_backend(plate, image_path)
            except Exception as e:
                print(f"[ERROR] Failed to send plate to backend: {e}")
            
        else:            
            print("[FAILURE] No plate detected.")

        time.sleep(2)  # short pause to avoid rapid repeat triggers

if __name__ == "__main__":
    main()
