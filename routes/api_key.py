from fastapi import APIRouter, HTTPException
from typing import Dict, List
from utils.chatgpt_client import ChatGPTClient
from routes.schema_management import schema_manager
from datetime import datetime
import logging

api_key_router = APIRouter()
chatgpt_client = ChatGPTClient()


def get_schema_context(tables: List[str]) -> str:
    """Generate clear schema context without forcing relationships."""
    buffer = schema_manager.get_buffer()
    schema_context = "Database Schema:\n"

    # Add detailed schema for each requested table
    for table in tables:
        if table not in buffer:
            raise KeyError(f"Table '{table}' not found in schema")

        schema_context += f"\nTable {table}:\n"
        schema_context += f"Columns: {', '.join(buffer[table]['column_name'])}\n"

    return schema_context


@api_key_router.post("/generate-query/")
async def generate_query_from_key(key: str, question: str):
    """Generate SQL query based on actual schema."""
    try:
        timestamp = "2025-01-19 05:32:15"
        user_id = "VOID-001"

        # Parse and validate tables
        tables = [t.strip() for t in key.split(',') if t.strip()]
        if not tables:
            raise ValueError("No tables provided")

        # Generate schema context
        schema_context = get_schema_context(tables)

        # Generate SQL query
        sql_query = chatgpt_client.generate_sql_from_question(
            schema_context,
            question,
            user_id=user_id,
            timestamp=timestamp
        )

        return {
            "sql_query": sql_query,
            "tables_used": tables,
            "schema_context": schema_context
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))