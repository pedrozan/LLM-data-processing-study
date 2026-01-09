import os
import logging
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values
from datetime import datetime
from io import StringIO
import urllib.request

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

def get_existing_ticket_ids(conn):
    """Get set of ticket_ids already in the database"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ticket_id FROM raw_support_tickets")
            existing_ids = {row[0] for row in cur.fetchall()}
        return existing_ids
    except Exception as e:
        logger.error(f'Failed to retrieve existing ticket IDs: {e}')
        return set()

def load_csv_to_postgres(csv_path, conn):
    """Load CSV data into raw_support_tickets table, skipping already ingested records"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        total_record_count = len(df)
        logger.info(f'Loaded {total_record_count} rows from {csv_path}')
        logger.info(f'CSV columns before cleaning: {df.columns.tolist()}')
        
        # Clean column names (convert to lowercase, replace spaces with underscores)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        logger.info(f'CSV columns after cleaning: {df.columns.tolist()}')
        
        # Check if ticket_id column exists
        if 'ticket_id' not in df.columns:
            logger.warning('ticket_id column not found in CSV, skipping duplicate check. Available columns: ' + str(df.columns.tolist()))
            df_new = df.copy()
            new_record_count = len(df_new)
        else:
            # Get existing ticket IDs from database
            existing_ids = get_existing_ticket_ids(conn)
            logger.info(f'Found {len(existing_ids)} existing records in database')
            
            # Filter to only new records
            df_new = df[~df['ticket_id'].isin(existing_ids)].copy()
            new_record_count = len(df_new)
        
        if new_record_count == 0:
            logger.info('No new records to ingest')
            return 0
        
        logger.info(f'Found {new_record_count} new records to ingest (skipped {total_record_count - new_record_count} existing records)')
        
        # Prepare data for insertion
        with conn.cursor() as cur:
            # Get column names from dataframe
            columns = df_new.columns.tolist()
            
            # Convert dataframe to list of tuples
            values = [tuple(row) for row in df_new.values]
            
            # Build INSERT query
            insert_query = f"""
                INSERT INTO raw_support_tickets ({', '.join(columns)})
                VALUES %s
            """
            
            # Execute insertion
            execute_values(cur, insert_query, values)
            conn.commit()
            
        logger.info(f'Successfully inserted {new_record_count} new records into raw_support_tickets table')
        return new_record_count
    except Exception as e:
        logger.error(f'Failed to load CSV data: {e}')
        raise

def main():
    """Main execution function"""
    csv_url = 'https://raw.githubusercontent.com/pedrozan/LLM-data-processing-study/refs/heads/main/files/customer_support_tickets.csv'
    
    logger.info('Starting data ingestion process')
    
    try:
        # Connect to database
        conn = get_db_connection()
        
        # Create table
        create_table(conn)
        
        # Download CSV from GitHub
        logger.info(f'Downloading CSV from {csv_url}')
        with urllib.request.urlopen(csv_url) as response:
            csv_data = response.read().decode('utf-8')
        
        # Load data
        df = pd.read_csv(StringIO(csv_data))
        
        # Create a temporary file path for logging
        csv_path = 'GitHub: ' + csv_url
        
        # Process the data (reuse the logic from load_csv_to_postgres)
        total_record_count = len(df)
        logger.info(f'Loaded {total_record_count} rows from {csv_path}')
        logger.info(f'CSV columns before cleaning: {df.columns.tolist()}')
        
        # Clean column names (convert to lowercase, replace spaces with underscores)
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        logger.info(f'CSV columns after cleaning: {df.columns.tolist()}')
        
        # Check if ticket_id column exists
        if 'ticket_id' not in df.columns:
            logger.warning('ticket_id column not found in CSV, skipping duplicate check. Available columns: ' + str(df.columns.tolist()))
            df_new = df.copy()
            new_record_count = len(df_new)
        else:
            # Get existing ticket IDs from database
            existing_ids = get_existing_ticket_ids(conn)
            logger.info(f'Found {len(existing_ids)} existing records in database')
            
            # Filter to only new records
            df_new = df[~df['ticket_id'].isin(existing_ids)].copy()
            new_record_count = len(df_new)
        
        if new_record_count == 0:
            logger.info('No new records to ingest')
            conn.close()
            return
        
        logger.info(f'Found {new_record_count} new records to ingest (skipped {total_record_count - new_record_count} existing records)')
        
        # Prepare data for insertion
        with conn.cursor() as cur:
            # Get column names from dataframe
            columns = df_new.columns.tolist()
            
            # Convert dataframe to list of tuples
            values = [tuple(row) for row in df_new.values]
            
            # Build INSERT query
            insert_query = f"""
                INSERT INTO raw_support_tickets ({', '.join(columns)})
                VALUES %s
            """
            
            # Execute insertion
            execute_values(cur, insert_query, values)
            conn.commit()
            
        logger.info(f'Successfully inserted {new_record_count} new records into raw_support_tickets table')
        
        # Close connection
        conn.close()
        
        logger.info(f'Data ingestion completed successfully - {new_record_count} records processed')
        
    except Exception as e:
        logger.error(f'Data ingestion failed: {e}', exc_info=True)
        raise

if __name__ == '__main__':
    main()
