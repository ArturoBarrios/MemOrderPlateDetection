import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")  
API_KEY = os.getenv("BACKEND_API_KEY")  

def findPlate(plate: str, image_url: str):
    mutation = """
    mutation($plate: String!, $imageUrl: String!) {
      createPlate(plate: $plate, imageUrl: $imageUrl) {
        id
        plate
        imageUrl
      }
    }
    """  # use createOrder instead if you want that right away

    variables = {
        "plate": plate,
        "imageUrl": image_url
    }

    headers = {
        "Content-Type": "application/json",
    }

    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    response = requests.post(BACKEND_URL, json={"query": mutation, "variables": variables}, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Backend call failed: {response.status_code} {response.text}")

    return response.json()
