from fastapi import APIRouter, HTTPException
from azure.storage.blob import BlobServiceClient
from typing import List
from app import templates, pdf
from pydantic import BaseModel
from datetime import datetime
import os
import logging


# Define Pydantic models for the JSON structure
class InterestRate(BaseModel):
     From: str
     To: str
     Rate: str

     def __del__(self):
         pass # do nothing


class Transaction(BaseModel):
     Date: str
     Type: str
     Amount: str
     Balance: str

     def __del__(self):
         pass # do nothing


class Payload(BaseModel):
     docId: str
     salutation: str
     firstName: str
     familyName: str
     recipientAddress: str
     agreementId: str
     repaymentMethod: str
     statementDate: str
     statementPeriod: str
     accountHolder: str
     securityAddress: str
     paymentShortfall: str
     outstandingBal: str
     redemptionBal: str
     exitFee: str
     erc: str
     ercEndDate: str
     agreementStartDate: str
     totalCredit: str
     originalTerm: str
     totalFees: str
     termRemaining: str
     totalInterest: str
     totalPaymentsDue: str
     totalPaymentsMade: str
     totalArrearsCharges: str
     totalCollectionCharges: str
     interestRates: List[InterestRate]
     transactions: List[Transaction]

     def __del__(self):
         pass # do nothing


router = APIRouter(
    prefix="/statement",
    tags=["statement"]
)


@router.post("/")
async def generate_statement(payload: Payload):
    # Generate a statement PDF

    # run some simple payload validation checks:
    # check for interest rates
    if not bool(payload.interestRates):
      raise HTTPException(status_code=400, detail="Payload must contain at least one interest rate for the statement period.")

    # check for transactions
    if not bool(payload.transactions):
      raise HTTPException(status_code=400, detail="Payload is missing transactions for the statement.")

    # setup date variables for use in templates and filenames
    today = datetime.today()
    now = datetime.now()
    nicedate = today.strftime("%d %B, %Y")
    shortdatetime = now.strftime("%Y%m%d%H%M%S")

    # Get current directory
    this_folder = os.path.dirname(os.path.abspath(__file__))
    # Get parent directory
    head_tail = os.path.split(this_folder)
    app_folder = head_tail[0]

    # Construct the interest rate table
    interest_table = '<table border="1" data-testid="interestTable">\n<thead>\n'

    # Create headers using the class keys
    ir_headers = InterestRate.model_fields.keys()
    interest_table += (
       "  <tr>" + "".join(f"<th>{header}</th>" for header in ir_headers) + "</tr>\n"
    )
    interest_table += "</thead>"

    # Add each interest rate as a row in the table
    for rate in payload.interestRates:
       interest_table += (
           "  <tr>"
           + "".join(f"<td>{getattr(rate, header)}</td>" for header in ir_headers)
           + "</tr>\n"
       )

    # End the interest rate table
    interest_table += "</table>"

    # Construct the transaction table
    transaction_table = '<table border="1" class="fullwidth" data-testid="transactionTable">\n<thead>'

    # Create headers using the class keys
    tr_headers = Transaction.model_fields.keys()
    transaction_table += (
       "  <tr>" + "".join(f"<th>{header}</th>" for header in tr_headers) + "</tr>\n"
    )
    transaction_table += "</thead>"

    # Add each interest rate as a row in the table
    for transaction in payload.transactions:
        transaction_table += '  <tr>' + ''.join(f'<td>{getattr(transaction, header)}</td>' for header in tr_headers) + '</tr>\n'

    # End the transaction table
    transaction_table += "</table>"
  
    try:
        # Get the preloaded template
        statement = templates.get("statement")
        footer = templates.get("footer")
        
        # Substitute variables
        variables = {
            "|date|": str(nicedate),
            "|salutation|": payload.salutation,
            "|firstName|": payload.firstName,
            "|familyName|": payload.familyName,
            "|recipientAddress|": payload.recipientAddress,
            "|agreementId|": payload.agreementId,
            "|repaymentMethod|": payload.repaymentMethod,
            "|statementDate|": payload.statementDate,
            "|statementPeriod|": payload.statementPeriod,
            "|accountHolder|": payload.accountHolder,
            "|securityAddress|": payload.securityAddress,
            "|paymentShortfall|": payload.paymentShortfall,
            "|outstandingBal|": payload.outstandingBal,
            "|redemptionBal|": payload.redemptionBal,
            "|exitFee|": payload.exitFee,
            "|erc|": payload.erc,
            "|ercEndDate|": payload.ercEndDate,
            "|totalPaymentsDue|": payload.totalPaymentsDue,
            "|totalPaymentsMade|": payload.totalPaymentsMade,
            "|totalArrearsCharges|": payload.totalArrearsCharges,
            "|totalCollectionCharges|": payload.totalCollectionCharges,
            "|agreementStartDate|": payload.agreementStartDate,
            "|totalCredit|": payload.totalCredit,
            "|originalTerm|": payload.originalTerm,
            "|totalFees|": payload.totalFees,
            "|termRemaining|": payload.termRemaining,
            "|totalInterest|": payload.totalInterest,
            "|transactionTable|": str(transaction_table),
            "|interestTable|": str(interest_table),
            "|imagePath|": str("file://" + os.path.join(app_folder, "images", "logo-200.png")),
            "|signaturePath|": str("file://" + os.path.join(app_folder, "images", "AjaySignature.png")),
            "|stylePath|": str("file://" + os.path.join(app_folder, "stylesheets", "statement.css")),
            "|footerContent|": str(footer)           
        }
        html_content = pdf.substitute_variables(statement, variables)
        
        # Generate PDF
        pdf_bytes = pdf.generate_pdf(html_content)

        # write to BLOB storage
        connection_string = os.getenv("STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise RuntimeError("Azure Storage connection string not configured (statement.py)")
    
        output_container = os.getenv("OUTPUT_BLOB_CONTAINER") # output container differs per deployment slot (Prod / SIT)
        if not output_container:
            raise RuntimeError("Output container env variable not configured (statement.py)")
        
        filename = payload.agreementId + "_statement_" + str(shortdatetime) + ".pdf"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        output_blob_client = blob_service_client.get_blob_client(container=output_container, blob=filename)
        output_blob_client.upload_blob(pdf_bytes, blob_type="BlockBlob", overwrite=True)

        logging.info("Statement produced for " + payload.agreementId)
        agreementId = payload.agreementId

        # clean up memory
        del payload
        del ir_headers
        del tr_headers

        return {
            "pdf_base64": pdf.encode_to_base64(pdf_bytes),
            "agreement": agreementId,
            "template": "statement",
            "status": "success"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate statement for AgreementID {agreementId}: {str(e)}"
        )