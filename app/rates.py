# ===== Imports and Setup =====
from fastapi import APIRouter, HTTPException, Depends
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from app.main import get_token  # Import the token retrieval function

# ===== Environment Loading (if not already loaded) =====
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

client_id = os.getenv("FEDEX_CLIENT_ID")
client_secret = os.getenv("FEDEX_CLIENT_SECRET")
account_number = os.getenv("FEDEX_ACCOUNT_NUMBER")

# ===== FastAPI Router Initialization =====
router = APIRouter()

# ===== FedEx Rates Endpoint =====
@router.post("/get-rates")
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
