from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncIterator
import logging
from . import templates
import os
import uvicorn


# setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
   # Lifespan handler for startup and shutdown events

   # Startup
   logger.info("Initializing application resources")

   try:
      # Initialize templates
      connection_string = os.getenv("STORAGE_CONNECTION_STRING")
      if not connection_string:
         raise RuntimeError("Azure Storage connection string not configured")
      
      template_container = os.getenv("TEMPLATE_BLOB_CONTAINER")
      if not template_container:
         raise RuntimeError("Tempalte container string not configured")
   
      await templates.load_templates(connection_string, template_container)
         
      logger.info(f"Successfully loaded {len(templates.get_all())} templates")
      
   except Exception as e:
      logger.error(f"Application startup failed: {str(e)}")
      raise

   yield  # Application runs here
      
   # Shutdown
   logger.info("Cleaning up application resources")
   await templates.cleanup()
   logger.info("Application shutdown complete")


# create the FastAPI app
app = FastAPI(
   title="Document Factory",
   description="Converts HTML templates with variable-substitution to base64-encoded PDFs",
   version="1.0.0",
   lifespan=lifespan
)


# Import all endpoint routers
from app.endpoints import statement, esis #,other routers


# Include all endpoint routers
app.include_router(statement.router)
app.include_router(esis.router)
#add more endpoint routers here as required

# Root endpoint with basic information
@app.get("/", status_code=200)
async def root():
    return {
        "service": "HTML Template to PDF Converter",
        "status": "running",
        "loaded_templates": list(templates.get_all().keys())
    }
 

# Create healthcheck endpoint for Azure Web App Healthcheck monitoring, needs to exist and return 200
@app.get("/healthcheck", status_code=200)
async def health_check():
    return {
        "status": "healthy"
    }


if __name__ == "__main__":
     uvicorn.run(app, host="127.0.0.1", port=80)