import psycopg2

pgvector_client = None

def initialize_pgvector_client(database_url):
    global pgvector_client
    pgvector_client = psycopg2.connect(database_url)

def get_schema_metadata():
    """Fetch schema metadata from the database."""
    query = """
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'public';
    """
    cursor = pgvector_client.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def execute_sql_query(query):
    """Execute a SQL query on the database."""
    cursor = pgvector_client.cursor()
    cursor.execute(query)
    return cursor.fetchall()
