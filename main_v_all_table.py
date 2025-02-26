import oracledb
from PIL import Image
import io
import os
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(override=True)

oracle_host = os.getenv("ORACLE_HOST")
oracle_port = os.getenv("ORACLE_PORT")
oracle_service_name = os.getenv("ORACLE_SERVICE_NAME")
oracle_user = os.getenv("ORACLE_USER")
oracle_password = os.getenv("ORACLE_PASSWORD")
image_dir = os.getenv("IMG_DIR")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 100))  # Default batch size is 100
OFFSET = 0  # Start from 0

def connect_oracle():
    params = oracledb.ConnectParams(host=oracle_host, port=oracle_port, service_name=oracle_service_name)
    conn = oracledb.connect(user=oracle_user, password=oracle_password, params=params)
    return conn

def get_all_tables():
    connection = connect_oracle()
    cursor = connection.cursor()
    query = f"""
    SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER = UPPER('{oracle_user}')
    """
    cursor.execute(query)
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()
    return tables

def fetch_data_from_table(table_name):
    connection = connect_oracle()
    cursor = connection.cursor()
    query = f"""
    SELECT SO_CCCD, ANH_CHAN_DUNG FROM {oracle_user}.{table_name}
    OFFSET {OFFSET} ROWS FETCH NEXT {BATCH_SIZE} ROWS ONLY
    """
    cursor.execute(query)
    records = []
    for row in cursor:
        identity_id = row[0]
        image_blob_data = row[1].read() if row[1] else None  # Read LOB data before closing connection
        records.append((identity_id, image_blob_data))
    cursor.close()
    connection.close()
    return records

def save_blob_as_image(table_name, identity_id, image_blob_data):
    try:
        if image_blob_data:
            table_image_dir = os.path.join(image_dir, table_name)
            if not os.path.exists(table_image_dir):
                os.makedirs(table_image_dir)
            image = Image.open(io.BytesIO(image_blob_data))
            image_path = os.path.join(table_image_dir, f"{identity_id}.jpg")
            image.save(image_path)
        else:
            print(f"No image data found for {identity_id}")
    except Exception as e:
        print(f"Error saving image for {identity_id}: {e}")

def process_all_tables():
    global OFFSET
    tables = get_all_tables()
    for table in tables:
        table_image_dir = os.path.join(image_dir, table)
        if not os.path.exists(table_image_dir):
            os.makedirs(table_image_dir)
        print(f"Processing table: {table}")
        while True:
            records = fetch_data_from_table(table)
            if not records:
                break
            for record in records:
                save_blob_as_image(table, record[0], record[1])
            OFFSET += BATCH_SIZE
            print(f"Processed {OFFSET} records from {table}")
        OFFSET = 0  # Reset OFFSET for the next table

if __name__ == "__main__":
    start_time = time.time()
    process_all_tables()
    end_time = time.time()
    print(f"\nTotal Execution Time: {end_time - start_time:.2f} seconds")
