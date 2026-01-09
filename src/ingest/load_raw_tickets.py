import os
import logging
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from datetime import datetime

# Configure logging
log_dir = '/app/logs'
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'data_ingestion_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Establish connection to Postgres database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'llm_data'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            port=os.getenv('DB_PORT', 5432)
        )
        logger.info('Successfully connected to Postgres database')
        return conn
    except Exception as e:
        logger.error(f'Failed to connect to database: {e}')
        raise

def create_table(conn):
    """Create raw_support_tickets table if it doesn't exist"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_support_tickets (
                    ticket_id SERIAL PRIMARY KEY,
                    customer_name VARCHAR(255),
                    customer_email VARCHAR(255),
                    customer_age INTEGER,
                    customer_gender VARCHAR(50),
                    product_purchased VARCHAR(255),
                    date_of_purchase DATE,
                    ticket_type VARCHAR(100),
                    ticket_subject VARCHAR(255),
                    ticket_description TEXT,
                    ticket_status VARCHAR(100),
                    resolution TEXT,
                    ticket_priority VARCHAR(50),
                    ticket_channel VARCHAR(100),
                    first_response_time VARCHAR(255),
                    time_to_resolution VARCHAR(255),
                    customer_satisfaction_rating FLOAT
                )
            """)
        conn.commit()
        logger.info('Successfully created or verified raw_support_tickets table')
    except Exception as e:
        logger.error(f'Failed to create table: {e}')
        raise

def load_csv_to_postgres(csv_path, conn):
    """Load CSV data into raw_support_tickets table"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        record_count = len(df)
        logger.info(f'Loaded {record_count} rows from {csv_path}')
        
        # Clean column names (convert to lowercase, replace spaces with underscores)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Prepare data for insertion
        with conn.cursor() as cur:
            # Get column names from dataframe
            columns = df.columns.tolist()
            
            # Convert dataframe to list of tuples
            values = [tuple(row) for row in df.values]
            
            # Build INSERT query
            insert_query = f"""
                INSERT INTO raw_support_tickets ({', '.join(columns)})
                VALUES %s
            """
            
            # Execute insertion
            execute_values(cur, insert_query, values)
            conn.commit()
            
        logger.info(f'Successfully inserted {record_count} records into raw_support_tickets table')
        return record_count
    except Exception as e:
        logger.error(f'Failed to load CSV data: {e}')
        raise

def main():
    """Main execution function"""
    csv_path = '/app/files/customer_support_tickets.csv'
    
    logger.info('Starting data ingestion process')
    
    try:
        # Connect to database
        conn = get_db_connection()
        
        # Create table
        create_table(conn)
        
        # Load data
        record_count = load_csv_to_postgres(csv_path, conn)
        
        # Close connection
        conn.close()
        
        logger.info(f'Data ingestion completed successfully - {record_count} records processed')
        
    except Exception as e:
        logger.error(f'Data ingestion failed: {e}', exc_info=True)
        raise

if __name__ == '__main__':
    main()
