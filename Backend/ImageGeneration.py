import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Ensure the Data folder exists
DATA_FOLDER = "Data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
API_KEY = get_key('.env', 'HuggingFaceAPIKey')

if not API_KEY:
    print("❌ Error: Hugging Face API key not found in .env file.")
    exit(1)

headers = {"Authorization": f"Bearer {API_KEY}"}


async def query(payload):
    """Send request to Hugging Face API."""
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None  # Return None if there's an error
        
        return response.content
    except Exception as e:
        print(f"❌ Request Error: {e}")
        return None


async def generate_images(prompt: str):
    """Generate and save images asynchronously."""
    tasks = []
    
    for _ in range(4):  # Generate 4 images
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)  

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is None:
            print(f"❌ Skipping image {i+1} due to API failure.")
            continue  # Skip if API failed
        
        image_name = f"{prompt.replace(' ', '__')}{i + 1}.jpg"
        image_path = os.path.join(DATA_FOLDER, image_name)

        try:
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # Verify the saved file
            with Image.open(image_path) as img:
                img.verify()

            print(f"✅ Image saved successfully: {image_path}")
        except Exception as e:
            print(f"❌ Failed to save image {image_path}: {e}")


def generate_and_open_images(prompt: str):
    """Generate images and open them after saving."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_images(prompt))
    loop.close()

    open_images(prompt)


def open_images(prompt):
    """Open generated images from the Data folder."""
    prompt = prompt.replace(" ", "__")
    file_paths = [os.path.join(DATA_FOLDER, f"{prompt}{i}.jpg") for i in range(1, 5)]

    for image_path in file_paths:
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            continue  

        if os.path.getsize(image_path) == 0:
            print(f"❌ Image file is empty: {image_path}")
            continue
        
        try:
            img = Image.open(image_path)
            print(f"🖼️ Opening image: {image_path}")
            img.show()
        except Exception as e:
            print(f"❌ Error opening image {image_path}: {e}")


# 🚀 MAIN LOOP: Check for image generation requests
IMAGE_GEN_FILE = r"Frontend\Files\ImageGeneration.data"

while True:
    try:
        if not os.path.exists(IMAGE_GEN_FILE):
            print(f"❌ File not found: {IMAGE_GEN_FILE}, waiting for input...")
            sleep(1)
            continue  

        with open(IMAGE_GEN_FILE, "r", encoding="utf-8") as f:
            Data = f.read().strip()

        if not Data:
            print("⚠️ File is empty, waiting for valid data...")
            sleep(1)
            continue

        Prompt, Status = Data.split(",")

        if Status.strip().lower() == "true":  
            print("🖼️ Generating Images...")
            generate_and_open_images(prompt=Prompt)

            # Reset status to False after generating images
            with open(IMAGE_GEN_FILE, "w", encoding="utf-8") as f:
                f.write("False,False")
            break  
        else:
            sleep(1)

    except Exception as e:
        print(f"❌ Error: {e}")  
        sleep(1)
