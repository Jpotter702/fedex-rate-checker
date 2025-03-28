# ===== Imports and Setup =====
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pathlib import Path
import os
import requests  # This is needed for making HTTP requests
from datetime import datetime, timedelta

# 📦 Import custom rates module (used to handle FedEx rate API)
from app import rates  # Ensure the import statement for rates is correct
from app.rates import router as rates_router  # Import the router from rates.py

# Ensure all dependencies are installed using `pip install -r requirements.txt`
# This includes FastAPI, Uvicorn, python-dotenv, and requests.

# ===== Environment Variable Loading =====
# Load the .env file containing credentials like client_id, secret, and account number
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

client_id = os.getenv("FEDEX_CLIENT_ID")
client_secret = os.getenv("FEDEX_CLIENT_SECRET")
account_number = os.getenv("FEDEX_ACCOUNT_NUMBER")

# Validate environment variables
if not all([client_id, client_secret, account_number]):
    raise RuntimeError("Missing required environment variables. Please check your .env file.")

# ===== FastAPI App Initialization =====
app = FastAPI()

# ===== Token Cache =====
# A dictionary to store the token and its expiration time
token_cache = {
    "token": None,
    "expires_at": None
}

# ===== Root Endpoint =====
# Simple GET route to confirm the server is running and environment is loaded
@app.get("/")
async def root():
    return {"message": "FedEx Rate Checker API is running"}

# ===== Bearer Token Endpoint with Caching =====
@app.get("/get-token")
async def get_token():
    # Check if the token is cached and still valid
    if token_cache["token"] and token_cache["expires_at"] > datetime.utcnow():
        return {"access_token": token_cache["token"], "expires_at": token_cache["expires_at"]}

    # If no valid token is cached, request a new one
    url = "https://apis-sandbox.fedex.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()

        # Cache the new token and its expiration time
        token_cache["token"] = token_data["access_token"]
        token_cache["expires_at"] = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])

        return {"access_token": token_cache["token"], "expires_at": token_cache["expires_at"]}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve token") from e

# ===== Route Module Registration =====
# Includes external routes from app/rates.py into this FastAPI app
app.include_router(rates_router, prefix="/rates")
