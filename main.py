from fastapi import FastAPI
from routes.train_routes import train_router
from routes.sql_generation_routes import sql_generation_router
from routes.execute_sql_routes import execute_sql_router

app = FastAPI()

# Include routers
app.include_router(train_router, prefix="/api")
app.include_router(sql_generation_router, prefix="/api")
app.include_router(execute_sql_router, prefix="/api")

# Root route
@app.get("/")
def read_root():
    return {"message": "FastAPI with T5 SQL Generation and PG Execution is running!"}
