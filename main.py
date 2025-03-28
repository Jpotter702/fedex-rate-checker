# ===== Imports and Setup =====
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pathlib import Path
import os
import requests  # This is needed for making HTTP requests

# 📦 Import custom rates module (used to handle FedEx rate API)
from app import rates

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

# ===== Root Endpoint =====
# Simple GET route to confirm the server is running and environment is loaded
@app.get("/")
async def root():
    return {"message": "FedEx Rate Checker API is running"}

# ===== Bearer Token Endpoint =====
# Route to retrieve FedEx sandbox OAuth token
@app.get("/get-token")
async def get_token():
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
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve token") from e

# ===== Route Module Registration =====
# Includes external routes from app/rates.py into this FastAPI app
app.include_router(rates.router)
