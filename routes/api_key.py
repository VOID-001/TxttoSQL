from fastapi import APIRouter, HTTPException
from utils.chatgpt_client import generate_sql_from_question
from routes.schema_management import BUFFER
from utils.logger import log_info, log_error

api_key_router = APIRouter()

@api_key_router.post("/validate-schema/")
async def validate_schema(key: str):
    """Validate if the key exists in the buffer."""
    if key in BUFFER:
        log_info(f"Key '{key}' is present in buffer.")
        return {"detail": "Key is present in buffer.", "schema": BUFFER[key]}
    else:
        log_error(f"Key '{key}' not found in buffer.")
        raise HTTPException(status_code=404, detail="Key not found in buffer.")

@api_key_router.post("/generate-query/")
async def generate_query_from_key(key: str, question: str):
    """Generate a SQL query based on schema and question."""
    if key not in BUFFER:
        log_error(f"Key '{key}' not found in buffer.")
        raise HTTPException(status_code=404, detail="Key not found in buffer.")

    schema_context = f"Key: {key}\nTables and Columns:\n"
    for table, columns in BUFFER[key].items():
        schema_context += f"{table}: {', '.join(columns)}\n"

    sql_query = generate_sql_from_question(f"Schema:\n{schema_context}\nQuestion: {question}")
    log_info(f"Generated SQL query for key '{key}': {sql_query}")
    return {"sql_query": sql_query}