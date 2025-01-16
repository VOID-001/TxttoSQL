from fastapi import APIRouter

api_key_router = APIRouter()
openai_api_key = None

@api_key_router.post("/set-api-key/")
async def set_api_key(api_key: str):
    """Set the OpenAI API key."""
    global openai_api_key
    openai_api_key = api_key
    return {"detail": "API key set successfully."}

@api_key_router.get("/get-api-key/")
async def get_api_key():
    """Get the currently set API key."""
    if openai_api_key:
        return {"api_key": openai_api_key}
    return {"detail": "No API key set."}
