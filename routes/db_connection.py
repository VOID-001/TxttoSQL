from fastapi import APIRouter, HTTPException
from utils.pgvector_client import initialize_pgvector_client

db_connection_router = APIRouter()

@db_connection_router.post("/connect-db/")
async def connect_db(connection_url: str):
    """Set the database connection URL dynamically."""
    try:
        initialize_pgvector_client(connection_url)
        return {"detail": "Connected to database successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")
