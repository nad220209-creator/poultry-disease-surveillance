import os
import time
import json
from google import genai
from supabase import create_client, Client

# Read API keys securely from Environment Variables (GitHub Secrets)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

ai_client = genai.Client(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Official announcements to process
raw_announcements = [
    """
    The Poultry Diagnostic Laboratory Vehari has confirmed suspected Newcastle Disease (ND / Rani Khet) in commercial layer and broiler farms near Burewala and Vehari districts. Severe drop in egg production and high mortality reported. Farmers are strongly advised to enforce strict farm quarantine, disinfect feed vehicles, and update ND vaccination schedules immediately.
    """,
    """
    District Diagnostic Lab Arifwala issued an alert regarding Hydropericardium Syndrome (HPS / Angara Disease) cases reported in broiler flocks in Arifwala and Sahiwal districts. High sudden mortality observed in 3 to 5-week-old broilers. Emergency vaccination and liver tonic supplementation recommended.
    """,
    """
    Livestock Department Punjab issued an advisory for Avian Influenza (Bird Flu / H5N1) surveillance in waterfowls and commercial poultry near wetland areas in Multan, Khanewal, and Okara districts. Strictly control bird movement and report sudden mortality to nearby diagnostic labs.
    """
]

print(f"Starting automated batch processing for {len(raw_announcements)} announcements...\n")

for index, raw_text in enumerate(raw_announcements, start=1):
    prompt = f"""
    You are a veterinary disease surveillance assistant for Punjab Poultry Farmers.
    Read the official text below and summarize it into a structured alert.

    Raw Announcement:
    "{raw_text}"

    Return ONLY a JSON object with these exact keys:
    - disease_name
    - severity
    - target_district
    - summary
    - biosecurity_protocol
    """

    print(f"Processing Announcement #{index} with Gemini AI...")
    response = ai_client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
    )

    clean_json_str = response.text.replace("```json", "").replace("```", "").strip()
    alert_data = json.loads(clean_json_str)
    
    alert_data["timestamp_millis"] = int(time.time() * 1000) + (index * 100)

    supabase.table("alerts").insert(alert_data).execute()
    print(f" -> Successfully saved '{alert_data.get('disease_name')}' to Supabase!\n")
    time.sleep(1)

print("All automated results uploaded successfully to Supabase!")