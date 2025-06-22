from fastapi import APIRouter, HTTPException
from azure.storage.blob import BlobServiceClient
from app import templates, pdf
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import os
import logging
import re


# Define Pydantic models for the JSON structure
class Payload(BaseModel):
    docId: str
    appId: str
    loanApplicant: str
    brokerName: str
    brokerPhone: str
    brokerStreet: str
    brokerCity: str
    brokerCounty: str
    brokerPostcode: str
    brokerEmail: str
    brokerWeb: str
    brokerCommission: float
    subBroker: bool
    subBrokerName: Optional[str] = ""
    subBrokerPhone: Optional[str] = ""
    subBrokerStreet: Optional[str] = ""
    subBrokerCity: Optional[str] = ""
    subBrokerCounty: Optional[str] = ""
    subBrokerPostcode: Optional[str] = ""
    subBrokerEmail: Optional[str] = ""
    subBrokerWeb: Optional[str] = ""
    advance: str
    initialRate: float
    margin: float
    referenceRate: float
    aprc: str
    loanType: str #FixedTerm, FixedReversion, Variable
    feesAdded: str
    loanTermYYMM: str
    loanTermMonths: str
    totalAmountRepayable: str
    costOfCredit: str
    valuation: str
    minValuation: str
    securityAddress: str
    lenderFee: str
    lenderFeeAdded: str
    brokerFee: str
    brokerFeeAdded: str
    applicationFee: str
    applicationFeeAdded: str
    adviceFee: str
    adviceFeeAdded: str
    valuationFee: str
    valuationFeeAdded: str
    otherFee: str
    otherFeeDescription: str
    otherFeeAdded: str
    interestRateIllustrationIncrease: str
    aprcIllustrationIncrease: str
    paymentsIllustrationIncrease: str
    ercYear1: str
    ercYear2: str
    ercYear3: str
    ercYear4: str
    ercYear5: str
    maxERC: str
    imlAddress: str
    imlPhone: str
    imlWebsite: str
    scotland: bool

    def __del__(self):
         pass # do nothing


#-------------------------------------------------------------------------
# Single routine to remove any block & delimiters - TO TEST
def remove_block(text, delimiter):
    pattern = fr'\b{delimiter}\b.*?\/b{delimiter}\b'
    new_block = re.sub(pattern, '', text, flags=re.DOTALL)
    new_block2 = re.sub(delimiter, '', new_block, flags=re.DOTALL)
    return re.sub('/' + delimiter, '', new_block2, flags=re.DOTALL)


# Routine to evaluate expression-based condition in HTML template - TO TEST
# looks for [[CONDITION::expression_to_evaluate]]{{tag}}content to display{{/tag}}
# where expression_to_evaluate is somethine like subBroker=TRUE or scotland=TRUE
# and tag is something like {{scotland}}scottish content{{/scotland}}
import re

def render_conditional_html(html, context):
    pattern = re.compile(
        r'\[\[CONDITION::(.*?)\]\]\s*\{\{(\w+)\}\}(.*?)\{\{/\2\}\}',
        re.DOTALL
    )
    
    result = html
    
    for match in pattern.finditer(html):
        expression, tag, content = match.groups()
        full_block = match.group(0)
        
        try:
            # Safely evaluate the expression using context
            condition_result = eval(expression.strip(), {}, context)
            if bool(condition_result):
                result = result.replace(full_block, content)
            else:
                result = result.replace(full_block, '')
        except Exception as e:
            print(f"Error in condition '{expression}': {e}")
            result = result.replace(full_block, '')  # Remove on failure
    
    return result
#-------------------------------------------------------------------------


# Define routines to strip out conditional blocks that are not required
def remove_variable_rate_blocks(text):
    pattern = r'\{\{VariableRate\}\}.*?\{\{\/VariableRate\}\}'
    return re.sub(pattern, '', text, flags=re.DOTALL)


def remove_fixed_term_blocks(text):
    pattern = r'\{\{FixedTerm\}\}.*?\{\{\/FixedTerm\}\}'
    return re.sub(pattern, '', text, flags=re.DOTALL)


def remove_fixed_reversion_blocks(text):
    pattern = r'\{\{FixedReversion\}\}.*?\{\{\/FixedReversion\}\}'
    return re.sub(pattern, '', text, flags=re.DOTALL)


def remove_broker(text):
    pattern = r'\{\{Broker\}\}.*?\{\{\/Broker\}\}'
    return re.sub(pattern, '', text, flags=re.DOTALL)


def remove_sub_broker(text):
    pattern = r'\{\{subBroker\}\}.*?\{\{\/subBroker\}\}'
    return re.sub(pattern, '', text, flags=re.DOTALL)

def remove_scotland(text):
    pattern = r'\{\{scotland\}\}.*?\{\{\/scotland\}\}'
    return re.sub(pattern, '', text, flags=re.DOTALL)


def strip_delimiters(pattern1, pattern2, text):
    interim_text = re.sub(pattern1, '', text, flags=re.DOTALL)
    return re.sub(pattern2, '', interim_text, flags=re.DOTALL)


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
        esis_template = templates.get("esis")

        # Deal with subBroker conditional statement
        if not payload.subBroker:
            esis_step1 = remove_sub_broker(esis)
            esis = strip_delimiters("{{subBroker}}","{{/subBroker}}",esis_step1)
        else:
            esis_step1 = remove_broker(esis)
            esis = strip_delimiters("{{Broker}}","{{/Broker}}",esis_step1)

        # Deal with Scottish conditional statement
        if not payload.scotland:
            esis_step1 = remove_scotland(esis)
            esis = strip_delimiters("{{scotland}}","{{/scotland}}",esis_step1)
        
        # Deal with loanType conditional statements
        if payload.loanType == "FixedTerm":
            esis_step1 = remove_variable_rate_blocks(esis_template)
            esis_step2 = remove_fixed_reversion_blocks(esis_step1)
            esis = strip_delimiters("{{FixedTerm}}","{{/FixedTerm}}",esis_step2)
        elif payload.loanType == "FixedReversion":
            esis_step1 = remove_variable_rate_blocks(esis_template)
            esis_step2 = remove_fixed_term_blocks(esis_step1)
            esis = strip_delimiters("{{FixedReversion}}","{{/FixedReversion}}",esis_step2)
        else: # assume variable
            esis_step1 = remove_fixed_reversion_blocks(esis_template)
            esis_step2 = remove_fixed_term_blocks(esis_step1)
            esis = strip_delimiters("{{Variable}}","{{/Variable}}",esis_step2)

        # Substitute variables
        variables = {
            "|appId|": payload.appId,
            "|loanApplicant|":  payload.loanApplicant,
            "|date|": str(nicedate),
            "|validDate|": str(validUntil),
            "|brokerName|": payload.brokerName,
            "|brokerPhone|": payload.brokerPhone,
            "|brokerStreet|": payload.brokerStreet,
            "|brokerCity|": payload.brokerCity,
            "|brokerCounty|": payload.brokerCounty,
            "|brokerPostcode|": payload.brokerPostcode,
            "|brokerEmail|": payload.brokerEmail,
            "|brokerWeb|": payload.brokerWeb,
            "|brokerCommission|": payload.brokerCommission,
            "|subBrokerName|": payload.subBrokerName,
            "|subBrokerPhone|": payload.subBrokerPhone,
            "|subBrokerStreet|": payload.subBrokerStreet,
            "|subBrokerCity|": payload.subBrokerCity,
            "|subBrokerCounty|": payload.subBrokerCounty,
            "|subBrokerPostcode|": payload.subBrokerPostcode,
            "|subBrokerEmail|": payload.subBrokerEmail,
            "|subBrokerWeb|": payload.subBrokerWeb,
            "|advance|":  payload.advance,
            "|initialRate|":  payload.initialRate,
            "|margin|":  payload.margin,
            "|referenceRate|":  payload.referenceRate,
            "|aprc|":  payload.aprc,            
            "|feesAdded|":  payload.feesAdded,
            "|loanTermYYMM|":  payload.loanTermYYMM,
            "|loanTermMonths|":  payload.loanTermMonths,
            "|totalAmountRepayable|":  payload.totalAmountRepayable,
            "|costOfCredit|":  payload.costOfCredit,
            "|valuation|":  payload.valuation,
            "|minValuation|":  payload.minValuation,
            "|securityAddress|":  payload.securityAddress,
            "|valuationFee|":  payload.valuationFee,
            "|valuationFeeAdded|":  payload.valuationFeeAdded,
            "|lenderFee|":  payload.lenderFee,
            "|lenderFeeAdded|":  payload.lenderFeeAdded,
            "|brokerFee|":  payload.brokerFee,
            "|brokerFeeAdded|":  payload.brokerFeeAdded,
            "|applicationFee|":  payload.applicationFee,
            "|applicationFeeAdded|":  payload.applicationFeeAdded,
            "|adviceFee|":  payload.adviceFee,
            "|adviceFeeAdded|":  payload.adviceFeeAdded,
            "|valuationFee|":  payload.valuationFee,
            "|valuationFeeAdded|":  payload.valuationFeeAdded,
            "|otherFee|":  payload.otherFee,
            "|otherFeeDescription|":  payload.otherFeeDescription,
            "|otherFeeAdded|":  payload.otherFeeAdded,
            "|interestRateIllustrationIncrease|":  payload.interestRateIllustrationIncrease,
            "|aprcIllustrationIncrease|":  payload.aprcIllustrationIncrease,
            "|paymentsIllustrationIncrease|":  payload.paymentsIllustrationIncrease,
            "|ercYear1|":  payload.ercYear1,
            "|ercYear2|":  payload.ercYear2,
            "|ercYear3|":  payload.ercYear3,
            "|ercYear4|":  payload.ercYear4,
            "|ercYear5|":  payload.ercYear5,
            "|maxERC|":  payload.maxERC,
            "|imlAddress|":  payload.imlAddress,
            "|imlPhone|":  payload.imlPhone,
            "|imlWebsite|":  payload.imlWebsite
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