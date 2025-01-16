from fastapi import APIRouter, HTTPException
from utils.pgvector_client import execute_sql_query
from utils.chatgpt_client import generate_sql_from_question

sql_execution_router = APIRouter()

@sql_execution_router.post("/generate-sql-query/")
async def generate_sql_query(question: str):
    """Generate SQL query based on natural language question and schema."""
    try:
        sql_query = generate_sql_from_question(question)
        return {"sql_query": sql_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL query: {str(e)}")

@sql_execution_router.post("/execute-query/")
async def execute_query(sql_query: str):
    """Execute an input SQL query and return results."""
    try:
        results = execute_sql_query(sql_query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")
