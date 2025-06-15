import requests
import os
from dotenv import load_dotenv
import cv2

load_dotenv()

API_KEY = os.getenv("PLATE_RECOGNIZER_API_KEY")

def recognize_plate(image_path: str):
    # Resize image to prevent API 413 error
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    max_width = 800
    if width > max_width:
        scale = max_width / width
        new_height = int(height * scale)
        image = cv2.resize(image, (max_width, new_height))
        cv2.imwrite(image_path, image)

    # Upload resized image
    with open(image_path, "rb") as image_file:
        response = requests.post(
            "https://api.platerecognizer.com/v1/plate-reader/",
            files={"upload": image_file},
            headers={"Authorization": f"Token {API_KEY}"}
        )

    if response.status_code not in [200, 201]:
        raise Exception(f"Plate recognition failed: {response.status_code} {response.text}")

    data = response.json()
    results = data.get("results", [])

    if not results:
        if os.environ.get("ENVIRONMENT") == 'DEVELOPMENT':
            print("[DEV] No plate found, returning test plate data.")
            return {
                "plate": "ABC123",
                "score": 0.99,
                "box": {"xmin": 10, "ymin": 10, "xmax": 200, "ymax": 100}
            }
        else:
            print("No plate detected.")
            os.remove(image_path)
            return None

    plate_data = results[0]
    plate = plate_data["plate"]
    score = plate_data["score"]
    box = plate_data["box"]

    return {
        "plate": plate,
        "score": score,
        "box": box
    }
