# ===== Imports and Setup =====
from fastapi import APIRouter
import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# ===== Environment Loading (if not already loaded) =====
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client_id = os.getenv("FEDEX_CLIENT_ID")
client_secret = os.getenv("FEDEX_CLIENT_SECRET")
account_number = os.getenv("FEDEX_ACCOUNT_NUMBER")

# ===== FastAPI Router Initialization =====
router = APIRouter()

# ===== FedEx Rates Endpoint =====
@router.get("/get-rates")
def get_rates():
    # Get token
    token_url = "https://apis-sandbox.fedex.com/oauth/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    token_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_response = requests.post(token_url, data=token_data, headers=token_headers)

    if token_response.status_code != 200:
        return {"error": "Token request failed", "details": token_response.text}

    token = token_response.json()["access_token"]

    # Prepare rate request
    rate_url = "https://apis-sandbox.fedex.com/rate/v1/rates/quotes"
    rate_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    rate_payload = {
        "accountNumber": {"value": account_number},
        "requestedShipment": {
            "shipper": {"address": {"postalCode": "89104", "countryCode": "US"}},
            "recipient": {"address": {"postalCode": "10001", "countryCode": "US"}},
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "rateRequestType": ["ACCOUNT"],
            "requestedPackageLineItems": [
                {
                    "weight": {"units": "LB", "value": 3},
                    "dimensions": {"length": 12, "width": 10, "height": 6, "units": "IN"}
                }
            ],
            "packagingType": "YOUR_PACKAGING"
        }
    }

    rate_response = requests.post(rate_url, headers=rate_headers, json=rate_payload)

    if rate_response.status_code == 200:
        return rate_response.json()
    else:
        return {"error": "Rate request failed", "details": rate_response.text}
