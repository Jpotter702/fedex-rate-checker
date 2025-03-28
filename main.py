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

# ===== Route Module Registration =====
# Includes external routes from app/rates.py into this FastAPI app
app.include_router(rates_router, prefix="/rates")
