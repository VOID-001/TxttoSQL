from openai import OpenAI, OpenAIError
from fastapi import HTTPException
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class ChatGPTClient:
    def __init__(self):
        try:
            logging.info("Initializing ChatGPT Client...")
            self.api_key = os.getenv("OPENAI_API_KEY", "sk-proj-0gUcZqKp-EX49UPeIQuSEZsRE_SsqSDQLqzPz0eviiwax3YNZ7WQ-I6Fo35AhBoSA8lZIKozViT3BlbkFJlK0GPdQyObJAgM01xPqO-DF3l0bUnUfX6D1tDdwI0H4vuyT_lSWkdzVW3q_FhD3vxK58VcPXcA-123-lol")  # Better to use environment variable
            self.model = "gpt-3.5-turbo"
            self.client = OpenAI(api_key=self.api_key)
            self.max_retries = 3
            self.test_connection()
        except Exception as e:
            logging.error(f"Failed to initialize ChatGPT Client: {str(e)}")
            raise

    def test_connection(self):
        """Test the OpenAI connection with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Test connection"}],
                    max_tokens=5
                )
                logging.info("✅ OpenAI API connection successful!")
                return True
            except Exception as e:
                logging.error(f"❌ OpenAI API connection attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    return False

    def generate_sql_from_question(self, schema_context: str, question: str) -> str:
        """Generate SQL query using OpenAI GPT with improved error handling and retries."""
        try:
            prompt = self._build_prompt(schema_context, question)

            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system",
                             "content": "You are a SQL query generator. Generate only SQL queries without explanation."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=500
                    )
                    sql_query = response.choices[0].message.content.strip()
                    logging.info("✅ Successfully generated SQL query")
                    return self._post_process_query(sql_query)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    logging.warning(f"Attempt {attempt + 1} failed, retrying...")

        except Exception as e:
            error_msg = f"Failed to generate SQL query: {str(e)}"
            logging.error(f"❌ {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

    def _build_prompt(self, schema_context: str, question: str) -> str:
        """Build a structured prompt for SQL generation."""
        return f"""Given the following database schema:
{schema_context}

Generate a SQL query for this question:
{question}

Requirements:
- Return only the SQL query
- Use proper table aliases
- Include appropriate JOIN conditions
- Use proper column names as shown in schema
"""

    def _post_process_query(self, query: str) -> str:
        """Post-process the generated SQL query."""
        # Remove any markdown formatting
        query = query.replace('```sql', '').replace('```', '')
        # Remove extra whitespace
        query = ' '.join(query.split())
        # Ensure query ends with semicolon
        if not query.strip().endswith(';'):
            query += ';'
        return query


if __name__ == "__main__":
    try:
        logging.info("Starting ChatGPT Client test...")
        client = ChatGPTClient()
        test_schema = "CREATE TABLE users (id INT, name VARCHAR(255));"
        test_question = "Show me all users"
        result = client.generate_sql_from_question(test_schema, test_question)
        logging.info(f"Test completed successfully. Result: {result}")
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")