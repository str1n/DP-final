from fastapi import APIRouter, HTTPException
from azure.storage.blob import BlobServiceClient
from typing import List
from app import templates, pdf
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import logging

# Define Pydantic models for the JSON structure
class Payload(BaseModel):
    docId: str
    appId: str
    brokerName: str
    brokerPhone: str
    brokerStreet: str
    brokerCity: str
    brokerCounty: str
    brokerPostcode: str
    brokerEmail: str
    brokerWeb: str
    # etc

    def __del__(self):
         pass # do nothing


router = APIRouter(
    prefix="/esis",
    tags=["esis"]
)


@router.post("/")
async def generate_esis(payload: Payload):
    # Generate a ESIS PDF

    # setup date variables for use in templates and filenames
    today = datetime.today()
    tomorrow = today + timedelta(days=1)
    now = datetime.now()
    nicedate = today.strftime("%d %B, %Y")
    validUntil = tomorrow.strftime("%d %B, %Y")
    shortdatetime = now.strftime("%Y%m%d%H%M%S")

    try:
        # Get the preloaded template
        esis = templates.get("esis")

        # Substitute variables
        variables = {
            "|appId": payload.appId,
            "|validDate|": str(validUntil),
            "|brokerName|": payload.brokerName,
            "|brokerPhone|": payload.brokerPhone,
            "|brokerStreet|": payload.brokerStreet,
            "|brokerCity|": payload.brokerCity,
            "|brokerCounty|": payload.brokerCounty,
            "|brokerPostcode|": payload.brokerPostcode,
            "|brokerEmail|": payload.brokerEmail,
            "|brokerWeb|": payload.brokerWeb
        }
        html_content = pdf.substitute_variables(esis, variables)
            
        # Generate PDF
        pdf_bytes = pdf.generate_pdf(html_content)

        # write to BLOB storage
        connection_string = os.getenv("STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise RuntimeError("Azure Storage connection string not configured (esis.py)")
    
        output_container = os.getenv("OUTPUT_BLOB_CONTAINER") # output container differs per deployment slot (Prod / SIT)
        if not output_container:
            raise RuntimeError("Output container env variable not configured (esis.py)")
        
        filename = payload.appId + "_esis_" + str(shortdatetime) + ".pdf"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        output_blob_client = blob_service_client.get_blob_client(container=output_container, blob=filename)
        output_blob_client.upload_blob(pdf_bytes, blob_type="BlockBlob", overwrite=True)

        logging.info("ESIS produced for " + payload.appId)
        appId = payload.appId

        # Clean up memory
        del payload

        return {
            "pdf_base64": pdf.encode_to_base64(pdf_bytes),
            "application": appId,
            "template": "esis",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate ESIS for AppID {appId}: {str(e)}"
        )