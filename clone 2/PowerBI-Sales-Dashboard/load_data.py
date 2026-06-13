import pandas as pd
import psycopg2
from io import StringIO
import re

def clean_col_names(df):
    """Cleans column names to be database-friendly."""
    cols = df.columns
    new_cols = []
    for col in cols:
        # Convert to lowercase
        new_col = col.lower()
        # Replace spaces and hyphens with underscores
        new_col = re.sub(r'[\s-]', '_', new_col)
        # Remove any characters that are not alphanumeric or underscore
        new_col = re.sub(r'[^a-zA-Z0-9_]', '', new_col)
        new_cols.append(new_col)
    df.columns = new_cols
    return df

# --- Step 1: Load and Clean the CSV Data ---
try:
    # Load the CSV into a pandas DataFrame
    df = pd.read_csv('train.csv')

    # Clean the column names for SQL compatibility
    df = clean_col_names(df)

    print("Successfully loaded and cleaned the CSV file.")
    print("Columns are now:", df.columns.tolist())

except FileNotFoundError:
    print("Error: train.csv not found. Make sure the CSV file is in the same directory as this script.")
    exit()


# --- Step 2: Configure Your PostgreSQL Connection ---
# IMPORTANT: Replace these with your actual database credentials
db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'Hemesh@123',
    'host': 'localhost',  # Or your DB host
    'port': '5432'       # Default PostgreSQL port
}

# --- Step 3: Connect to PostgreSQL and Load Data ---
conn = None
try:
    # Establish the connection
    print("Connecting to the PostgreSQL database...")
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Define the table name
    table_name = 'superstore_sales'

    # --- Create the Table ---
    # Drop the table if it already exists to start fresh
    cur.execute(f"DROP TABLE IF EXISTS {table_name};")

    # Create the CREATE TABLE statement from the DataFrame columns
    # This automatically generates the SQL schema based on your CSV
    cols = ', '.join([f'"{col}" TEXT' for col in df.columns])
    create_table_sql = f'CREATE TABLE {table_name} ({cols});'

    print(f"Creating table '{table_name}'...")
    cur.execute(create_table_sql)

    # --- Use copy_from for Bulk Insertion ---
    # This is the most efficient way to load a large dataset
    print("Preparing to copy data... This may take a moment.")
    
    # Create an in-memory string buffer
    buffer = StringIO()
    # Write DataFrame to the buffer as a CSV, without the header
    df.to_csv(buffer, index=False, header=False)
    # Reset the buffer's position to the beginning
    buffer.seek(0)
    
    # Execute the COPY command
    cur.copy_expert(f"COPY {table_name} FROM STDIN WITH (FORMAT CSV)", buffer)

    # Commit the transaction to make the changes permanent
    conn.commit()

    # Verify the number of rows inserted
    cur.execute(f"SELECT COUNT(*) FROM {table_name};")
    row_count = cur.fetchone()[0]
    print(f"✅ Success! Copied {row_count} rows into '{table_name}'.")


except psycopg2.OperationalError as e:
    print(f"Connection Error: Could not connect to the database. Please check your db_params.")
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the cursor and connection
    if conn is not None:
        cur.close()
        conn.close()
        print("Database connection closed.")