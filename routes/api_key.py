from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Union
from utils.chatgpt_client import ChatGPTClient
from utils.logger import log_info, log_error
from routes.schema_management import schema_manager
from datetime import datetime
import logging

api_key_router = APIRouter()
chatgpt_client = ChatGPTClient()


def parse_keys(key_string: str) -> List[str]:
    """Parse comma-separated keys into a list."""
    logging.info(f"[{datetime.utcnow()}] Parsing keys: {key_string}")
    return [k.strip() for k in key_string.split(',') if k.strip()]


def get_schema_context(keys: List[str]) -> str:
    """Generate schema context for the specified keys."""
    logging.info(f"[{datetime.utcnow()}] Generating schema context for keys: {keys}")
    buffer = schema_manager.get_buffer()
    schema_context = "Database Schema:\n"

    for key in keys:
        if key not in buffer:
            logging.error(f"[{datetime.utcnow()}] Table not found: {key}")
            raise KeyError(f"Table '{key}' not found in schema buffer")

        schema_context += f"\nTable {key}:\n"
        schema_context += f"Columns: {', '.join(buffer[key]['column_name'])}\n"

    logging.info(f"[{datetime.utcnow()}] Schema context generated successfully")
    return schema_context


@api_key_router.post("/generate-query/")
async def generate_query_from_key(key: str, question: str):
    """Generate a SQL query based on schema and question."""
    try:
        logging.info(f"[{datetime.utcnow()}] Received query request - Key: {key}, Question: {question}")

        keys = parse_keys(key)
        if not keys:
            logging.error(f"[{datetime.utcnow()}] No valid keys provided")
            raise ValueError("No valid keys provided")

        # Validate all keys exist
        buffer = schema_manager.get_buffer()
        invalid_keys = [k for k in keys if k not in buffer]
        if invalid_keys:
            logging.error(f"[{datetime.utcnow()}] Invalid tables found: {invalid_keys}")
            raise KeyError(f"Tables not found in schema buffer: {', '.join(invalid_keys)}")

        # Generate schema context
        schema_context = get_schema_context(keys)
        logging.info(f"[{datetime.utcnow()}] Schema context generated for tables: {keys}")

        # Enhanced prompt for better context
        enhanced_question = f"""
Given these tables: {', '.join(keys)}
Question: {question}
Requirements:
- Use proper JOIN conditions if multiple tables are involved
- Include appropriate WHERE clauses
- Use proper column names as shown in schema
"""

        # Generate SQL query
        logging.info(f"[{datetime.utcnow()}] Requesting SQL generation from ChatGPT")
        sql_query = chatgpt_client.generate_sql_from_question(schema_context, enhanced_question)
        logging.info(f"[{datetime.utcnow()}] SQL query generated successfully")

        return {
            "sql_query": sql_query,
            "tables_used": keys,
            "schema_context": schema_context
        }

    except Exception as e:
        logging.error(f"[{datetime.utcnow()}] Error in generate_query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Rest of your endpoints remain the same...