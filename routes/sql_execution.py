from fastapi import APIRouter, HTTPException
from utils.pgvector_client import execute_sql_query

sql_execution_router = APIRouter()

@sql_execution_router.post("/execute-query/")
async def execute_query(sql_query: str):
    """Execute an input SQL query and return results."""
    try:
        results = execute_sql_query(sql_query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")
