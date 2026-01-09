import os
import psycopg2
import pandas as pd
from psycopg2.extras import execute_values

def get_db_connection():
    """Establish connection to Postgres database"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'llm_data'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        port=os.getenv('DB_PORT', 5432)
    )

def create_table(conn):
    """Create raw_support_tickets table if it doesn't exist"""
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

def load_csv_to_postgres(csv_path, conn):
    """Load CSV data into raw_support_tickets table"""
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Clean column names (convert to lowercase, replace spaces with underscores)
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    
    print(f"Loaded {len(df)} rows from {csv_path}")
    
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
        
    print(f"Successfully inserted {len(df)} records into raw_support_tickets table")

def main():
    """Main execution function"""
    csv_path = '/app/files/customer_support_tickets.csv'
    
    try:
        # Connect to database
        conn = get_db_connection()
        print("Connected to Postgres database")
        
        # Create table
        create_table(conn)
        print("Table created or already exists")
        
        # Load data
        load_csv_to_postgres(csv_path, conn)
        
        # Close connection
        conn.close()
        print("Data ingestion completed successfully")
        
    except Exception as e:
        print(f"Error during data ingestion: {e}")
        raise

if __name__ == '__main__':
    main()
