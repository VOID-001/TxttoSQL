from openai import OpenAI, OpenAIError
from fastapi import HTTPException
import logging
import os
from .token_counter import token_counter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class ChatGPTClient:
    def __init__(self):
        try:
            logging.info("Initializing ChatGPT Client...")
            self.api_key = os.getenv("OPENAI_API_KEY",
                                     "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")
            self.model = "gpt-4o-mini"
            self.client = OpenAI(api_key=self.api_key)
            self.max_retries = 3
            self.last_user = "VOID-001"
            self.test_connection()
        except Exception as e:
            logging.error(f"Failed to initialize ChatGPT Client: {str(e)}")
            raise

    def test_connection(self):
        """Test the OpenAI connection with a retry mechanism."""
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "Test connection"}],
                    max_tokens=5
                )
                # Track tokens for test connection
                token_counter.add_tokens(response.usage.total_tokens)
                logging.info(" OpenAI API connection successful!")
                return True
            except Exception as e:
                logging.error(f" OpenAI API connection attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    return False

    def generate_sql_from_question(self, schema_context: str, question: str, user_id: str = None) -> str:
        """Generate SQL query using OpenAI GPT."""
        try:
            self.last_user = user_id or self.last_user

            prompt = self._build_prompt(schema_context, question)

            for attempt in range(self.max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self._get_system_prompt()},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=500
                    )

                    # Track token usage
                    warning_msg = token_counter.add_tokens(response.usage.total_tokens)
                    if warning_msg:
                        logging.warning(f"Token Warning: {warning_msg}")

                    sql_query = response.choices[0].message.content.strip()
                    logging.info(f" Successfully generated SQL query for user {self.last_user}")
                    return self._post_process_query(sql_query)

                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    logging.warning(f"Attempt {attempt + 1} failed, retrying...")

        except Exception as e:
            error_msg = f"Failed to generate SQL query: {str(e)}"
            logging.error(f" {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)

    def _get_system_prompt(self) -> str:
        """Get the system prompt."""
        return """You are a SQL query generator.
Rules:
1. Use ONLY columns that exist in the schema
2. Use proper table aliases
3. Return ONLY the SQL query without explanations
4. Keep joins simple and direct based on available columns"""

    def _build_prompt(self, schema_context: str, question: str) -> str:
        return f"""Given the following database schema:
{schema_context}

Generate a SQL query for this question:
{question}

Requirements:
- Return only the SQL query
- Use proper table aliases
- Use only existing columns from schema
- Keep joins simple and direct"""

    def _post_process_query(self, query: str) -> str:
        """Post-process the generated SQL query."""
        # Remove any markdown formatting
        query = query.replace('```sql', '').replace('```', '')
        # Remove extra whitespace
        query = ' '.join(query.split())
        # Ensure the query ends with a semicolon
        if not query.strip().endswith(';'):
            query += ';'
        return query


if __name__ == "__main__":
    try:
        logging.info("Starting ChatGPT Client test...")
        client = ChatGPTClient()
        test_schema = """
Table users:
Columns: id (integer), name (varchar)
"""
        test_question = "Show me all users"
        result = client.generate_sql_from_question(
            test_schema,
            test_question,
            user_id="VOID-001"
        )
        token_status = token_counter.get_status()
        logging.info(f"Test completed successfully. Result: {result}")
        logging.info(f"Current token count: {token_status['total_tokens']}")
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")