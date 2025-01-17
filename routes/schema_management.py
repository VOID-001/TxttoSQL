from fastapi import APIRouter, HTTPException, UploadFile, File
import csv
import io
import os
import pandas as pd
from datetime import datetime
from utils.pgvector_client import get_schema_metadata
from utils.logger import log_info, log_error

schema_management_router = APIRouter()

BUFFER = {}
SCHEMA_DIR = "schema"


def ensure_schema_directory():
    """Ensure the schema directory exists."""
    os.makedirs(SCHEMA_DIR, exist_ok=True)
    return SCHEMA_DIR


@schema_management_router.get("/download-schema/")
async def download_schema():
    """Fetch schema metadata and save it as a CSV file."""
    try:
        schema_data = get_schema_metadata()
        df = pd.DataFrame(schema_data, columns=["table_name", "column_name", "data_type"])

        # Save CSV file with timestamp
        schema_dir = ensure_schema_directory()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"schema_{timestamp}.csv"
        file_path = os.path.join(schema_dir, filename)
        df.to_csv(file_path, index=False)

        log_info(f"Schema metadata saved to {file_path}.")

        # Return file content in response
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        return {"schema.csv": buffer.getvalue(), "saved_to": file_path}
    except Exception as e:
        log_error(f"Error fetching schema: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching schema: {str(e)}")


@schema_management_router.post("/upload-schema/")
async def upload_schema(file: UploadFile = File(...)):
    """Upload schema file and process into buffer."""
    global BUFFER
    try:
        contents = await file.read()
        buffer_data = io.StringIO(contents.decode())
        reader = csv.DictReader(buffer_data)

        # Check if CSV has the required columns
        if "table_name" not in reader.fieldnames or "column_name" not in reader.fieldnames or "data_type" not in reader.fieldnames:
            raise ValueError("CSV must contain 'Table', 'Column', and 'Data Type' headers.")

        for row in reader:
            key = row["table_name"]
            if key not in BUFFER:
                BUFFER[key] = {"column_name": []}
            BUFFER[key]["column_name"].append(f"{row['column_name']} ({row['data_type']})")

        log_info("Schema successfully uploaded and stored in buffer.")
        return {
            "detail": "Schema successfully uploaded and stored in buffer.",
            "buffer": BUFFER
        }
    except Exception as e:
        log_error(f"Error processing schema file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error processing schema file: {str(e)}")

@schema_management_router.get("/print-buffer/")
async def print_buffer():
    """Print the current buffer."""
    return {"buffer": BUFFER}
