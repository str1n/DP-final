from weasyprint import HTML
from fastapi import HTTPException
import base64
import logging

logger = logging.getLogger(__name__)

def generate_pdf(html_content: str) -> bytes:
    # Generate PDF from HTML content
    try:
        html = HTML(string=html_content)
        return html.write_pdf()
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

def encode_to_base64(pdf_bytes: bytes) -> str:
    # Encode PDF bytes to base64 string
    return base64.b64encode(pdf_bytes).decode('utf-8')

def substitute_variables(template: str, variables: dict) -> str:
    # Replace template variables with actual values
    for key, value in variables.items():
        template = template.replace(f"{key}", str(value))
    return template