from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError
from fastapi import HTTPException
import logging
from typing import Dict

logger = logging.getLogger(__name__)

_templates: Dict[str, str] = {}
_blob_service_client = None

async def load_templates(connection_string: str, container_name: str):
    # Load all templates from Azure Blob Storage
    global _blob_service_client, _templates
    
    try:
        _blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = _blob_service_client.get_container_client(container_name)
                
        # Get all blobs (handles pagination internally)
        blob_list = container_client.list_blobs()
        
        # Process each blob (template)
        for blob in blob_list:
            if blob.name.endswith('.html'):
                try:
                    blob_client = container_client.get_blob_client(blob.name)

                    # Download the blob content synchronously
                    stream = blob_client.download_blob()
                    template_content = stream.readall()
                    template_name = blob.name.replace('.html', '')
                    _templates[template_name] = template_content.decode('utf-8')
                    logger.info(f"Loaded template: {template_name}")
                except AzureError as e:
                    logger.error(f"Failed to load template {blob.name}: {str(e)}")
    
    except AzureError as e:
        logger.error(f"Template loading failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Template loading failed: {str(e)}"
        )

def get(template_name: str) -> str:
    # Get a specific template by name
    template = _templates.get(template_name)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template '{template_name}' not found"
        )
    return template

def get_all() -> Dict[str, str]:
    # Get all loaded templates
    return _templates

async def cleanup():
    # Clean up resources
    global _blob_service_client
    if _blob_service_client:
        await _blob_service_client.close()
    _templates.clear()