from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from routes.db_connection import db_connection_router
from routes.schema_management import schema_management_router
from routes.sql_execution import sql_execution_router
from routes.api_key import api_key_router
from utils.logger import log_info, log_error

app = FastAPI()
security = HTTPBasic()

# Dummy user for authentication
fake_users_db = {
    "user": "password"  # Replace with a secure method in production
}

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username not in fake_users_db or fake_users_db[credentials.username] != credentials.password:
        log_error("Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    log_info(f"User {credentials.username} authenticated successfully.")

# Include routers with authentication
app.include_router(db_connection_router, prefix="/api", dependencies=[Depends(authenticate)])
app.include_router(schema_management_router, prefix="/api", dependencies=[Depends(authenticate)])
app.include_router(sql_execution_router, prefix="/api", dependencies=[Depends(authenticate)])
app.include_router(api_key_router, prefix="/api", dependencies=[Depends(authenticate)])

@app.get("/")
def read_root():
    return {"message": "FastAPI with dynamic DB schema handling and buffer logic is running!"}