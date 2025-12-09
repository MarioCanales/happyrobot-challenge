import os
import requests
from dotenv import load_dotenv

load_dotenv()

FMCSA_API_KEY = os.getenv("FMCSA_API_KEY")
BASE_URL = os.getenv("FMCSA_BASE_URL")

def verify_carrier_mc(mc_number: str):
    """
    Queries the FMCSA API to check if a carrier is authorized.
    Returns: Boolean (True if authorized/active, False otherwise)
    """
    
    # MOCK MODE for testing without real API key -> MC numbers starting with '1' are valid
    if not FMCSA_API_KEY or FMCSA_API_KEY == "mock_phase":
        print("Warning: Running in MOCK FMCSA mode.")
        return True if mc_number.startswith("1") else False

    url = f"{BASE_URL}/{mc_number}?webKey={FMCSA_API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # SAFE PARSING: Check the specific flag
            content = data.get("content", {})
            # I have seen some responses in a list, others in a dict. Handle both:
            if isinstance(content, list) and len(content) > 0:
                carrier = content[0].get("carrier", {})
            else:
                carrier = content.get("carrier", {})
            # Return True if allowedToOperate is 'Y'. Explored by testing various responses using curl
            return carrier.get("allowedToOperate") == "Y"
        return False
    except Exception as e:
        print(f"FMCSA Request Failed: {e}")
        return False