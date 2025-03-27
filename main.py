# ===== Imports and Setup =====
from fastapi import FastAPI
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

# ===== FastAPI App Initialization =====
app = FastAPI()

# ===== Root Endpoint =====
# Simple GET route to confirm the server is running and environment is loaded
@app.get("/")
def read_root():
    return {
        "message": "API is running",
        "client_id": client_id,
        "account_number": account_number
    }

# ===== Bearer Token Endpoint =====
# Route to retrieve FedEx sandbox OAuth token
@app.get("/get-token")
def get_token():
    url = "https://apis-sandbox.fedex.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, data=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": response.status_code,
            "details": response.text
        }

# ===== Route Module Registration =====
# Includes external routes from app/rates.py into this FastAPI app
app.include_router(rates.router)
