from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

load_dotenv()

# Define the name of the header we expect
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get the valid key from environment variables
expected_api_key = os.getenv("SERVICE_API_KEY", "dev-secret-key")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == expected_api_key:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials"
    )