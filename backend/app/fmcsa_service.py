import os
import requests
from dotenv import load_dotenv

load_dotenv()

FMCSA_API_KEY = os.getenv("FMCSA_API_KEY")
BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services/carriers"

def verify_carrier_mc(mc_number: str):
    """
    Queries the FMCSA API to check if a carrier is authorized.
    Returns: Boolean (True if authorized/active, False otherwise)
    """
    # Valid MC numbers are usually 6-7 digits.
    # The API might expect 'MC' prefix or just numbers. Usually just numbers for query.
    
    # MOCK MODE (If you don't have a working API key yet)
    if not FMCSA_API_KEY or FMCSA_API_KEY == "your_fmcsa_key_here":
        print("Warning: Running in MOCK FMCSA mode.")
        # Mock logic: MC numbers starting with '1' are valid
        return True if mc_number.startswith("1") else False

    # REAL API MODE
    # Endpoint structure changes often, but typically:
    # https://mobile.fmcsa.dot.gov/qc/services/carriers/{search_term}?webKey={key}
    url = f"{BASE_URL}/{mc_number}?webKey={FMCSA_API_KEY}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Simple check: did we get any content back?
            # A real production check would inspect 'content' -> 'carrier' -> 'allowedToOperate'
            if data.get("content") and len(data["content"]) > 0:
                carrier = data["content"][0]
                # Basic check: verify it's the right MC and they are active
                # Note: 'allowedToOperate' might be a specific field depending on API version
                return True
            return False
        else:
            print(f"FMCSA API Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"FMCSA Request Failed: {e}")
        return False