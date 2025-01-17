# Set OpenAI API key from environment variables
# openai.api_key = os.getenv("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")


import openai
import os

# Set OpenAI API key from environment variables
openai.api_key = os.getenv("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")

def generate_sql_from_question(question: str):
    """Generate SQL query using OpenAI GPT."""
    if not openai.api_key:
        raise ValueError("OpenAI API key is not set.")

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Translate the following question into an SQL query:\n{question}",
        max_tokens=150
    )
    return response.choices[0].text.strip()