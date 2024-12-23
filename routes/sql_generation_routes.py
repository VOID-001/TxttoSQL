from fastapi import APIRouter, HTTPException
from transformers import T5Tokenizer, T5ForConditionalGeneration
import os

sql_generation_router = APIRouter()

# Load the fine-tuned model and tokenizer
model_path = "./MySQL_t5_model"

# Lazy model loading (to prevent app from crashing on startup)
model = None
tokenizer = None


def load_model():
    global model, tokenizer
    if not os.path.exists(model_path):
        raise HTTPException(status_code=500,
                            detail=f"Model not found at {model_path}. Please fine-tune the model first.")

    model = T5ForConditionalGeneration.from_pretrained(model_path)
    tokenizer = T5Tokenizer.from_pretrained(model_path)


@sql_generation_router.post("/generate-sql/")
async def generate_sql_query(question: str):
    try:
        # Load the model and tokenizer if not loaded
        if model is None or tokenizer is None:
            load_model()

        # Combine schema and question with a clear prompt
        input_text = f"translate English to SQL based on the provided schema:\nSchema: employees(employee_id, name, department, position, salary, bike_owned)\nQuestion: {question}"

        # Preprocess the input question
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

        # Generate the output (SQL query)
        outputs = model.generate(inputs, max_length=150, num_beams=5, early_stopping=True)

        # Decode the output and return the SQL query
        sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return {"sql_query": sql_query}

    except HTTPException as e:
        raise e  # Re-raise the model loading error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating SQL query: {str(e)}")
