from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from utils.pgvector_client import get_schema_metadata
from threading import Lock
import io
import os
from datetime import datetime

schema_management_router = APIRouter()
schema_store = {}
schema_lock = Lock()


def ensure_schema_directory(): # Here i check for directory if it exists in the routes dir
    """Create the schema directory if it doesn't exist."""
    schema_dir = os.path.join(os.path.dirname(__file__), 'schema')
    if not os.path.exists(schema_dir):
        os.makedirs(schema_dir)
    return schema_dir


@schema_management_router.get("/download-schema/")# Here i get the metadata from db about schema and save it in csv form
async def download_schema():

    try:
        schema_data = get_schema_metadata()
        df = pd.DataFrame(schema_data, columns=["table_name", "column_name", "data_type"])

        # Save to a csv file in the format Year, month ,day ,hour, mins and seconds
        schema_dir = ensure_schema_directory()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"schema_{timestamp}.csv"
        file_path = os.path.join(schema_dir, filename)
        df.to_csv(file_path, index=False)

        # Return file content in response
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return {"schema.csv": buffer.getvalue(), "saved_to": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching schema: {str(e)}")


@schema_management_router.post("/upload-schema/")
async def upload_schema(file: UploadFile = File(...)):
    """Upload schema as a CSV file and store it as key-value pairs."""
    try:
        df = pd.read_csv(file.file)

        # Save uploaded file locally
        schema_dir = ensure_schema_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"uploaded_schema_{timestamp}.csv"
        file_path = os.path.join(schema_dir, filename)
        df.to_csv(file_path, index=False)

        global schema_store
        with schema_lock:
            schema_store = {row["table_name"]: row["column_name"].split(',') for _, row in df.iterrows()}
        return {"detail": "Schema uploaded and stored successfully.", "saved_to": file_path}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading schema: {str(e)}")