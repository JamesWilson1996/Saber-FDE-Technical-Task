
import logging
import pandas as pd
import sqlite3
        
logger = logging.getLogger(__name__)
        
class SQLiteConnection:
    def __init__(self, database, uri=False):
        self.database = database
        self.uri = uri
        self.connection = None
    
    def query_customer_spend(self, city, date_time):
        logger.info("query_customer_spend request executing.")
        with sqlite3.connect(self.database, uri=self.uri) as conn:
            query_string = """
                SELECT
                    c.customer_id,
                    c.name,
                    c.email,
                    SUM(o.order_total) AS total_spend
                FROM customers c 
                INNER JOIN orders o 
                ON c.customer_id = o.customer_id 
                WHERE TRIM(LOWER(c.city)) = ?
                AND o.order_date >= ?
                GROUP BY
                    c.customer_id,
                    c.name,
                    c.email;
            """
            params = (city.lower(), date_time,)
            df = pd.read_sql_query(query_string, conn, params=params)
        return df