import psycopg2

class PGVectorClient:
    def __init__(self, database_url):
        self.conn = psycopg2.connect(database_url)
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            raise Exception(f"Query Execution Failed: {str(e)}")

    def close(self):
        self.conn.close()
