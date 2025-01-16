import openai


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
