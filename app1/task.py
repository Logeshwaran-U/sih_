import os
import json
import base64
import requests
import google.generativeai as genai
from celery import shared_task
from gtts import gTTS

# --- Get API Keys from environment variables ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")


@shared_task
def generate_story_task(prompt):
    """
    Generates a 5-page story with text, images, and audio.
    """
    print("\n--- [DEBUG 1/5] Starting new story generation task. ---")
    pages = []
    os.makedirs("media", exist_ok=True)

    # --- Step 1: Generate Story Text using Gemini ---
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        story_prompt = f"""
        Write a 5-page children's story about "{prompt}".
        Return ONLY valid JSON as a list of pages with:
        - page: page number
        - text: story text
        - illustration_prompt: A detailed, vibrant, and imaginative description for an illustration suitable for a children's book.
        """
        response = model.generate_content(story_prompt)
        text = response.text.strip().replace("json", "").replace("", "").strip()
        story_pages = json.loads(text)
        print("--- [DEBUG 2/5] Successfully generated story text from Gemini. ---")
    except Exception as e:
        print(f"--- [ERROR] Text generation failed: {e} ---")
        story_pages = [
            {"page": i, "text": f"Page {i} of {prompt}", "illustration_prompt": f"A beautiful illustration of {prompt} for a children's storybook."}
            for i in range(1, 6)
        ]

    # --- Step 2: Loop Through Pages to Generate Images and Audio ---
    for page in story_pages:
        page_num = page['page']
        page_text = page['text']
        illustration_prompt = page['illustration_prompt']
        
        # --- Image Generation ---
        print(f"--- [DEBUG 3/5] Starting image generation for page {page_num}... ---")
        if not STABILITY_API_KEY:
            print("--- [ERROR] STABILITY_API_KEY not found. Using placeholder. ---")
            image_url = "https://placehold.co/1024x1024/EEE/31343C?text=API+Key+Missing"
        else:
            try:
                # FIXED: The URL is now a clean string.
                url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
                
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {STABILITY_API_KEY}",
                }
                payload = {
                    "text_prompts": [
                        {"text": f"{illustration_prompt}, cute, high quality, digital art, storybook illustration", "weight": 1},
                        {"text": "blurry, ugly, text, words, watermark, deformed", "weight": -1} # Negative prompt
                    ],
                    "cfg_scale": 7, "height": 1024, "width": 1024, "steps": 30, "samples": 1,
                }
                
                response = requests.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                image_b64 = data["artifacts"][0]["base64"]
                image_path = f"media/page_{page_num}.png"
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_b64))
                
                image_url = f"/media/page_{page_num}.png"
                print(f"--- [SUCCESS] Image for page {page_num} saved. ---")

            except Exception as e:
                print(f"--- [ERROR] Image generation failed for page {page_num}: {e} ---")
                # FIXED: The fallback URL is also now a clean string.
                image_url = "https://placehold.co/1024x1024/EEE/31343C?text=Image+Failed"
        
        # --- Audio Generation ---
        print(f"--- [DEBUG 4/5] Starting audio generation for page {page_num}... ---")
        audio_b64 = ""
        try:
            tts = gTTS(page_text, lang='en', tld='co.in')
            audio_path = f"media/page_{page_num}.mp3"
            tts.save(audio_path)
            with open(audio_path, "rb") as f:
                audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"--- [ERROR] Audio generation failed for page {page_num}: {e} ---")

        pages.append({
            "page": page_num, "text": page_text, "image": image_url,
            "audio": "data:audio/mp3;base64," + audio_b64 if audio_b64 else ""
        })

    print("--- [DEBUG 5/5] Task finished successfully. Returning pages. ---\n")
    return pages


from celery import shared_task
import google.generativeai as genai
import os
import random
import json

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh", 
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", 
    "Lakshadweep", "Puducherry"
]

import os
import json
import random
import mimetypes  # <-- 1. IMPORT THE MIMETYPES LIBRARY
import google.generativeai as genai
from celery import shared_task

# Assume INDIAN_STATES is defined somewhere
#INDIAN_STATES = ["Tamil Nadu", "Kerala", "Karnataka", "Maharashtra", "Goa", "Rajasthan", "Punjab", "Uttarakhand", "West Bengal", "Delhi"]

import os
import json
import random
import mimetypes
import google.generativeai as genai
from celery import shared_task

@shared_task
def image_to_culture_task(image_path):
    """
    Identify and provide detailed cultural information from an uploaded image using Gemini.
    """
    print(f"\n[DEBUG] Starting detailed cultural analysis for: {image_path}")

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        # --- Upload image safely ---
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith('image'):
            raise ValueError(f"Could not determine image type for {image_path}")

        print(f"[DEBUG] Guessed MIME type: {mime_type}")
        img = genai.upload_file(path=image_path, mime_type=mime_type)
        print("[DEBUG] Image uploaded successfully to Gemini")

        # --- NEW: Detailed prompt for comprehensive analysis ---
        prompt = """
        You are an expert on Indian culture, history, and commerce. Analyze the provided image and return a detailed JSON object.

        Your task is to identify the object or landmark, its cultural context, and provide relevant information.

        The JSON response MUST follow this exact structure:
        {
          "identification": {
            "state": "The Indian state most associated with the image.",
            "city": "The city or specific location, if identifiable. Otherwise, null.",
            "object_name": "The specific name of the building, object, or scene."
          },
          "details": {
            "description": "A brief, informative paragraph about what is shown in the image.",
            "founder": "The founder or key historical figures associated with the construction or origin, if applicable. Otherwise, null.",
            "history_summary": "A concise summary of the history or cultural significance."
          },
          "commercial_info": {
            "type": "Categorize as 'landmark', 'artifact', 'food', 'clothing', or 'other'.",
            "purchase_suggestion": "If the item can be purchased (like an artifact, food, or clothing), provide a helpful tip on where to find it cheaply and authentically in India. Otherwise, this should be null."
          },
          "confidence": "A number between 0.0 and 1.0 indicating your confidence in the identification."
        }

        Analyze the image and provide the complete JSON. Do not include any other text or markdown formatting.
        """

        response = model.generate_content([prompt, img])
        raw_text = response.text.strip()
        print(f"[DEBUG] Raw Gemini response: {raw_text[:300]}...")

        # --- Clean and parse the detailed JSON ---
        clean_text = raw_text.replace("json", "").replace("", "").strip()
        try:
            result = json.loads(clean_text)
            print("[SUCCESS] Detailed information extracted successfully.")
            return result
        except Exception as e:
            print(f"[ERROR] JSON parsing failed: {e}")
            return {"error": "Failed to parse the detailed response from the AI."}

    except Exception as e:
        print(f"[ERROR] Image recognition task failed: {e}")
        return {"error": f"An unexpected error occurred: {str(e)}"}
    
    
# app1/tasks.py

@shared_task
def generate_culture_story_task(object_name, description, history):
    """
    Generate a story based on the cultural image analysis.
    """
    pages = []
    os.makedirs("media", exist_ok=True)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        story_prompt = f"""
        Write a short children's story (3–5 paragraphs) about the cultural heritage:
        - Object: {object_name}
        - Description: {description}
        - History: {history}
        Keep it engaging, magical, and easy for children to understand.
        """
        response = model.generate_content(story_prompt)
        story_text = response.text.strip()
    except Exception as e:
        story_text = f"Unable to generate story. Error: {str(e)}"

    # Audio narration
    audio_data = ""
    try:
        tts = gTTS(story_text, lang="en", tld="co.in")
        audio_path = "media/culture_story.mp3"
        tts.save(audio_path)
        with open(audio_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        audio_data = "data:audio/mp3;base64," + audio_b64
    except Exception as e:
        print(f"[ERROR] Audio failed: {e}")

    return {
        "story": story_text,
        "audio": audio_data
    }
    
    
import os
import time
import requests
from celery import shared_task

MESHY_API_KEY = os.getenv("MESHY_API_KEY")

def generate_3d_model_sync(prompt: str, mode: str = "preview", poll_interval: int = 5, timeout: int = 300):
    """
    Synchronous function: submit to Meshy, poll until SUCCEEDED or FAILED or timeout.
    Returns the GLB URL on success or raises an Exception.
    """
    if not MESHY_API_KEY:
        raise RuntimeError("MESHY_API_KEY environment variable is not set")

    url = "https://api.meshy.ai/v2/text-to-3d"
    headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}
    payload = {"mode": mode, "prompt": prompt}

    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    task_id = data.get("result")
    if not task_id:
        raise RuntimeError(f"Failed to create Meshy task: {data}")

    status_url = f"{url}/{task_id}"
    elapsed = 0
    while True:
        status_resp = requests.get(status_url, headers=headers, timeout=30)
        status_resp.raise_for_status()
        status_data = status_resp.json()
        status = status_data.get("status")

        if status == "SUCCEEDED":
            # try common places for the GLB URL
            model_urls = status_data.get("model_urls") or {}
            glb = model_urls.get("glb") or model_urls.get("file") or None
            # fallback into nested keys if API returns a different structure
            if not glb:
                glb = status_data.get("result", {}).get("model_urls", {}).get("glb")
            if not glb:
                raise RuntimeError(f"Meshy returned success but no GLB URL: {status_data}")
            return glb

        if status == "FAILED":
            raise RuntimeError(f"Meshy task failed: {status_data}")

        time.sleep(poll_interval)
        elapsed += poll_interval
        if elapsed > timeout:
            raise RuntimeError("Timed out waiting for Meshy result")


# Optional: Celery task wrapper so you can run this asynchronously if you want:
@shared_task
def generate_3d_model_task(prompt: str):
    return generate_3d_model_sync(prompt)