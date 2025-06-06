import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PLATE_RECOGNIZER_API_KEY")

def recognize_plate(image_path: str):
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
        print("No plate detected.")
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
