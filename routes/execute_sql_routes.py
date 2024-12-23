from fastapi import APIRouter, HTTPException
from utils.pgvector_client import PGVectorClient

execute_sql_router = APIRouter()

# Initialize PGVector Client
pgvector_client = PGVectorClient("postgresql://postgres:password@localhost:5432/vectordb")

@execute_sql_router.post("/execute-sql/")
async def execute_sql_query(query: str):
    try:
        # Execute the SQL query on PostgreSQL
        result = pgvector_client.execute_query(query)

        if not result:
            return {"detail": "No data found."}

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing SQL query: {str(e)}")
