from fastapi import APIRouter, HTTPException, UploadFile, File
import csv
import io
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel
from utils.pgvector_client import get_schema_metadata


class SchemaManagement:
    def __init__(self, schema_dir: str = "schema"):
        self.BUFFER: Dict[str, Dict[str, List[str]]] = {}
        self.SCHEMA_DIR = schema_dir
        self.ensure_schema_directory()

    def ensure_schema_directory(self) -> str:
        os.makedirs(self.SCHEMA_DIR, exist_ok=True)
        return self.SCHEMA_DIR

    def get_timestamp_filename(self, prefix: str = "schema", extension: str = "csv") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{prefix}_{timestamp}.{extension}"

    def validate_csv_headers(self, headers: List[str]) -> bool:
        required_headers = {"table_name", "column_name", "data_type"}
        return all(header in headers for header in required_headers)

    def clear_buffer(self) -> None:
        self.BUFFER.clear()

    def get_buffer(self) -> Dict:
        return self.BUFFER

    def process_csv_data(self, reader: csv.DictReader) -> int:
        processed_rows = 0
        for row in reader:
            key = row["table_name"].strip()
            if not key:
                continue

            if key not in self.BUFFER:
                self.BUFFER[key] = {"column_name": []}

            column_info = f"{row['column_name'].strip()} ({row['data_type'].strip()})"
            self.BUFFER[key]["column_name"].append(column_info)
            processed_rows += 1
        return processed_rows


schema_manager = SchemaManagement()
schema_management_router = APIRouter()

@schema_management_router.get("/download-schema/")
async def download_schema():
    try:
        schema_data = get_schema_metadata()
        if not schema_data:
            raise HTTPException(status_code=404, detail="No schema data available")

        df = pd.DataFrame(schema_data, columns=["table_name", "column_name", "data_type"])
        filename = schema_manager.get_timestamp_filename()
        file_path = os.path.join(schema_manager.SCHEMA_DIR, filename)

        df.to_csv(file_path, index=False)

        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        return {
            "schema_data": buffer.getvalue(),
            "saved_to": file_path,
            "row_count": len(df),
            "tables_count": len(df['table_name'].unique())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process schema: {str(e)}")


@schema_management_router.post("/upload-schema/")
async def upload_schema(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.csv'):
            raise ValueError("Only CSV files are supported")

        contents = await file.read()
        buffer_data = io.StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(buffer_data)

        if not schema_manager.validate_csv_headers(reader.fieldnames):
            raise ValueError("CSV must contain 'table_name', 'column_name', and 'data_type' headers")

        schema_manager.clear_buffer()
        processed_rows = schema_manager.process_csv_data(reader)

        return {
            "detail": "Schema successfully uploaded and stored in buffer",
            "processed_rows": processed_rows,
            "tables_count": len(schema_manager.BUFFER),
            "buffer": schema_manager.get_buffer()
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process schema file: {str(e)}")


@schema_management_router.get("/print-buffer/")
async def print_buffer():
    buffer = schema_manager.get_buffer()
    if not buffer:
        return {"detail": "Buffer is empty"}

    return {
        "buffer": buffer,
        "tables_count": len(buffer),
        "total_columns": sum(len(table["column_name"]) for table in buffer.values())
    }


@schema_management_router.post("/clear-buffer/")
async def clear_buffer():
    schema_manager.clear_buffer()
    return {"detail": "Buffer cleared successfully"}