from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from utils.chatgpt_client import ChatGPTClient
from routes.schema_management import schema_manager

nlp_context_router = APIRouter()

class NLPRequest(BaseModel):
    text: str

@nlp_context_router.post("/nlp/extract-schema-key")
async def extract_schema_key(nlp_request: NLPRequest):
    try:
        client = ChatGPTClient()
        # Clean incoming text to remove problematic control characters
        text = nlp_request.text.replace("\n", " ").strip()
        prompt = (
            "Extract the main keywords from the following text. "
            "Return only a comma separated list of keywords without any explanation. "
            f"{text}"
        )
        response = client.client.chat.completions.create(
            model=client.model,
            messages=[
                {"role": "system", "content": "Extract keywords from provided text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=60
        )
        extracted = response.choices[0].message.content.strip()
        if not extracted:
            raise HTTPException(status_code=400, detail="No keywords extracted.")

        keywords = [kw.strip().lower() for kw in extracted.split(',') if kw.strip()]
        buffer_keys = list(schema_manager.get_buffer().keys())
        matched = [key for key in buffer_keys if key.lower() in keywords]
        if not matched:
            return {"detail": "No matching schema context found.", "extracted_keywords": keywords}

        schema_context = ""
        selected = {}
        buf = schema_manager.get_buffer()
        for key in matched:
            selected[key] = buf[key]
            columns = ', '.join(buf[key].get("column_name", []))
            schema_context += f"Table {key}: Columns: {columns}\n"

        sql_query = client.generate_sql_from_question(schema_context, text)
        return {
            "detail": "Matching schema context found.",
            "matched_tables": matched,
            "schema_context": selected,
            "extracted_keywords": keywords,
            "sql_query": sql_query
        }
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")