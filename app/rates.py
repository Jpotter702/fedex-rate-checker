# ===== Imports and Setup =====
from fastapi import APIRouter, HTTPException, Depends
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timedelta

# ===== Environment Loading (if not already loaded) =====
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client_id = os.getenv("FEDEX_CLIENT_ID")
client_secret = os.getenv("FEDEX_CLIENT_SECRET")
account_number = os.getenv("FEDEX_ACCOUNT_NUMBER")

# ===== Token Cache =====
token_cache = {
    "token": None,
    "expires_at": None
}

def get_token():
    """
    Retrieve a FedEx API token with caching to avoid redundant requests.
    """
    if token_cache["token"] and token_cache["expires_at"] > datetime.utcnow():
        return {"access_token": token_cache["token"]}

    url = "https://apis-sandbox.fedex.com/oauth/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials", "client_id": client_id, "client_secret": client_secret}

    try:
        response = requests.post(url, data=data, headers=headers)
        response.raise_for_status()
        token_data = response.json()

        token_cache["token"] = token_data["access_token"]
        token_cache["expires_at"] = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        return {"access_token": token_cache["token"]}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve token: {str(e)}")

# ===== FastAPI Router Initialization =====
router = APIRouter()

# ===== FedEx Rates Endpoint =====
@router.post("/get-rates")  # Removed methods=["POST"]
async def get_rates(
    shipment_details: dict,
    token: dict = Depends(get_token)  # Automatically fetch the token
):
    """
    Fetch shipping rates from FedEx API.
    """
    url = "https://apis-sandbox.fedex.com/rate/v1/rates/quotes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token['access_token']}"
    }

    # Example payload for FedEx rate request
    payload = {
        "accountNumber": {
            "value": shipment_details.get("account_number", "YOUR_ACCOUNT_NUMBER")
        },
        "requestedShipment": {
            "shipper": {
                "address": {
                    "postalCode": shipment_details["origin_zip"],
                    "countryCode": shipment_details["origin_country"]
                }
            },
            "recipient": {
                "address": {
                    "postalCode": shipment_details["destination_zip"],
                    "countryCode": shipment_details["destination_country"]
                }
            },
            "pickupType": "DROPOFF_AT_FEDEX_LOCATION",
            "rateRequestType": ["ACCOUNT"],
            "requestedPackageLineItems": [
                {
                    "weight": {
                        "units": "LB",
                        "value": shipment_details["weight"]
                    },
                    "dimensions": {
                        "length": shipment_details["dimensions"]["length"],
                        "width": shipment_details["dimensions"]["width"],
                        "height": shipment_details["dimensions"]["height"],
                        "units": "IN"
                    }
                }
            ]
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        rates_data = response.json()
        return rates_data
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rates: {str(e)}")
