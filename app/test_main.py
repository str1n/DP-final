# Import python module
import pytest
import os
from fastapi.testclient import TestClient
from .main import app


client = TestClient(app)

# Set environment variables for test run
os.environ["TEMPLATE_BLOB_CONTAINER"] = "templates-nonprod"
os.environ["OUTPUT_BLOB_CONTAINER"] = "docfactorydev"


# Arrange a good test payload for the statement generation, only 2 transactions for brevity
@pytest.fixture
def good_payload():
    return {
        "docId": "STATEMENT",
        "salutation": "Mr",
        "firstName": "Testy",
        "familyName": "McTestFace",
        "recipientAddress": "1 Test Street<br>Test Town<br>Test County<br>TT1 1TT",
        "agreementId": "A-01234567890",
        "repaymentMethod": "Capital repayment mortgage",
        "statementDate": "01/01/2021",
        "statementPeriod": "01/01/2020 - 31/12/2020",
        "accountHolder": "Mrs Edwina Dolittle",
        "securityAddress": "1 Knox Road, Cardiff CF99 1ZZ",
        "paymentShortfall": "£0",
        "outstandingBal": "£43,702.48",
        "redemptionBal": "£43,150.23",
        "exitFee": "£495.00",
        "erc": "£431.50",
        "ercEndDate": "31/12/2025",
        "agreementStartDate": "01/01/2021",
        "totalCredit": "£45,000.00",
        "originalTerm": "120",
        "totalFees": "£3,000.00",
        "termRemaining": "108",
        "totalInterest": "£3,553.12",
        "totalPaymentsDue": "£4,850.64",
        "totalPaymentsMade": "£4,850.64",
        "totalArrearsCharges": "£0.00",
        "totalCollectionCharges": "£0.00",
        "interestRates":
            [
                {
                    "From": "01/01/2021",
                    "To": "31/08/2021",
                    "Rate": "10.78%"
                },
                {
                    "From": "01/09/2021",
                    "To": "31/12/2021",
                    "Rate": "10.53%"
                }
            ],
        "transactions":
            [
                {
                    "Date": "01/01/2022",
                    "Type": "Int",
                    "Amount": "292.10",
                    "Balance": "44,106.70"
                },
                {
                    "Date": "01/01/2022",
                    "Type": "DD",
                    "Amount": "-404.22",
                    "Balance": "43,702.48"
                }
            ]
    }

# Arrange a test payload with no transactions
@pytest.fixture
def missing_transactions():
    return {
        "docId": "STATEMENT",
        "salutation": "Mr",
        "firstName": "Testy",
        "familyName": "McTestFace",
        "recipientAddress": "1 Test Street<br>Test Town<br>Test County<br>TT1 1TT",
        "agreementId": "A-01234567890",
        "repaymentMethod": "Capital repayment mortgage",
        "statementDate": "01/01/2021",
        "statementPeriod": "01/01/2020 - 31/12/2020",
        "accountHolder": "Mrs Edwina Dolittle",
        "securityAddress": "1 Knox Road, Cardiff CF99 1ZZ",
        "paymentShortfall": "£0",
        "outstandingBal": "£43,702.48",
        "redemptionBal": "£43,150.23",
        "exitFee": "£495.00",
        "erc": "£431.50",
        "ercEndDate": "31/12/2025",
        "agreementStartDate": "01/01/2021",
        "totalCredit": "£45,000.00",
        "originalTerm": "120",
        "totalFees": "£3,000.00",
        "termRemaining": "108",
        "totalInterest": "£3,553.12",
        "totalPaymentsDue": "£4,850.64",
        "totalPaymentsMade": "£4,850.64",
        "totalArrearsCharges": "£0.00",
        "totalCollectionCharges": "£0.00",
        "interestRates":
            [
                {
                    "From": "01/01/2021",
                    "To": "31/08/2021",
                    "Rate": "10.78%"
                },
                {
                    "From": "01/09/2021",
                    "To": "31/12/2021",
                    "Rate": "10.53%"
                }
            ],
        "transactions":
            [
            ]
    }

# Arrange a test payload with no interest rates
@pytest.fixture
def missing_rates():
    return {
        "docId": "STATEMENT",
        "salutation": "Mr",
        "firstName": "Testy",
        "familyName": "McTestFace",
        "recipientAddress": "1 Test Street<br>Test Town<br>Test County<br>TT1 1TT",
        "agreementId": "A-01234567890",
        "repaymentMethod": "Capital repayment mortgage",
        "statementDate": "01/01/2021",
        "statementPeriod": "01/01/2020 - 31/12/2020",
        "accountHolder": "Mrs Edwina Dolittle",
        "securityAddress": "1 Knox Road, Cardiff CF99 1ZZ",
        "paymentShortfall": "£0",
        "outstandingBal": "£43,702.48",
        "redemptionBal": "£43,150.23",
        "exitFee": "£495.00",
        "erc": "£431.50",
        "ercEndDate": "31/12/2025",
        "agreementStartDate": "01/01/2021",
        "totalCredit": "£45,000.00",
        "originalTerm": "120",
        "totalFees": "£3,000.00",
        "termRemaining": "108",
        "totalInterest": "£3,553.12",
        "totalPaymentsDue": "£4,850.64",
        "totalPaymentsMade": "£4,850.64",
        "totalArrearsCharges": "£0.00",
        "totalCollectionCharges": "£0.00",
        "interestRates":
            [
            ],
        "transactions":
            [
                {
                    "Date": "01/01/2021",
                    "Type": "Adv",
                    "Amount": "42,000.00",
                    "Balance": "42,000.00"
                },
                {
                    "Date": "01/01/2021",
                    "Type": "LF",
                    "Amount": "500.00",
                    "Balance": "42,500.00"
                }
            ]
    }

# Arrange a test payload with missing docId element - not used yet but should be provided for future expansion
@pytest.fixture
def missing_element():
    return {
        "salutation": "Mr",
        "firstName": "Testy",
        "familyName": "McTestFace",
        "recipientAddress": "1 Test Street<br>Test Town<br>Test County<br>TT1 1TT",
        "agreementId": "A-01234567890",
        "repaymentMethod": "Capital repayment mortgage",
        "statementDate": "01/01/2021",
        "statementPeriod": "01/01/2020 - 31/12/2020",
        "accountHolder": "Mrs Edwina Dolittle",
        "securityAddress": "1 Knox Road, Cardiff CF99 1ZZ",
        "paymentShortfall": "£0",
        "outstandingBal": "£43,702.48",
        "redemptionBal": "£43,150.23",
        "exitFee": "£495.00",
        "erc": "£431.50",
        "ercEndDate": "31/12/2025",
        "agreementStartDate": "01/01/2021",
        "totalCredit": "£45,000.00",
        "originalTerm": "120",
        "totalFees": "£3,000.00",
        "termRemaining": "108",
        "totalInterest": "£3,553.12",
        "totalPaymentsDue": "£4,850.64",
        "totalPaymentsMade": "£4,850.64",
        "totalArrearsCharges": "£0.00",
        "totalCollectionCharges": "£0.00",
        "interestRates":
            [
                {
                    "From": "01/01/2021",
                    "To": "31/08/2021",
                    "Rate": "10.78%"
                },
                {
                    "From": "01/09/2021",
                    "To": "31/12/2021",
                    "Rate": "10.53%"
                }
            ],
        "transactions":
            [
                {
                    "Date": "01/01/2021",
                    "Type": "Adv",
                    "Amount": "£42,000.00",
                    "Balance": "£42,000.00"
                },
                {
                    "Date": "01/01/2021",
                    "Type": "LF",
                    "Amount": "£500.00",
                    "Balance": "£42,500.00"
                }
            ]
    }


def test_healthcheck():
    response = client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_pdf_success(good_payload: dict[str, str]):
    # Simulate a POST request with the given JSON payload
    try:
        response = client.post("/statement", json=good_payload)
    except Exception as excinfo:
        pytest.fail(f"Unexpected exception raised: {excinfo}")
    
    # Check if the status code is correct
    assert response.status_code == 200

    # Check if the response is a valid JSON response
    assert response.headers["Content-Type"] == "application/json"

    # Test for content length (this would depend on the size of the JSON response, typically 40k-50k for a statement, anything less than 10k is corrupt)
    assert int(response.headers["Content-Length"]) > 10000

def test_invalid_method(good_payload: dict[str, str]):
    response = client.post("/rubbish", json=good_payload)
    assert response.status_code == 404  # Not found (validation error)

def test_generate_pdf_missing_payload():
    # Test with completely missing payload
    response = client.post("/statement", json={})
    assert response.status_code == 422  # Unprocessable Entity (validation error)

def test_generate_pdf_missing_element(missing_element):
    # Test with completely missing payload
    response = client.post("/statement", json=missing_element)
    assert response.status_code == 422  # Unprocessable Entity (validation error)

def test_generate_pdf_missing_transactions(missing_transactions):
    # Test with missing fields in the payload (e.g., missing title or content)
    response = client.post("/statement", json=missing_transactions)
    assert response.status_code == 400  # Transactions required (code validation error)

def test_generate_pdf_missing_rates(missing_rates):
    # Test with missing fields in the payload (e.g., missing title or content)
    response = client.post("/statement", json=missing_rates)
    assert response.status_code == 400  # Interest rates required (code validation error)