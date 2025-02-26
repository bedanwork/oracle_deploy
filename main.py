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
oracle_table_name = os.getenv("ORACLE_TABLE_NAME")

BATCH_SIZE = int(os.getenv("BATCH_SIZE"))  # Convert to integer
OFFSET = int(os.getenv("OFFSET"))  # Convert to integer

def connect_oracle():
    params = oracledb.ConnectParams(host=oracle_host, port=oracle_port, service_name=oracle_service_name)
    conn = oracledb.connect(user=oracle_user, password=oracle_password, params=params)
    return conn

def fetch_data_from_oracle():
    connection = connect_oracle()
    cursor = connection.cursor()
    query = f"""
    SELECT SO_CCCD, ANH_CHAN_DUNG
    FROM {oracle_user}.{oracle_table_name}
    OFFSET {OFFSET} ROWS FETCH NEXT {BATCH_SIZE} ROWS ONLY
    """
    cursor.execute(query)
    records = []
    for row in cursor:
        identity_id = row[0]
        image_blob_data = row[1].read() if row[1] else None  # Read while connection is open
        records.append((identity_id, image_blob_data))

    cursor.close()
    connection.close()
    return records

def save_blob_as_image(identity_id,image_blob_data):
    try:
        if image_blob_data:
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)  # Creates the directory if it doesn't exist
            image = Image.open(io.BytesIO(image_blob_data))
            image_path = os.path.join(image_dir, f"{identity_id}.jpg")
            image.save(image_path)
        else :
            print(f"No image data found for {identity_id}")

    except Exception as e:
        print(f"Error saving image for {identity_id}: {e}")


def process_and_save_image():
    global OFFSET  # Declare OFFSET as global
    start_time = time.time()
    while True:
        records = fetch_data_from_oracle()
        if not records:
            break

        for record in records:
            save_blob_as_image(record[0], record[1])
        
        OFFSET += BATCH_SIZE  # Ensure BATCH_SIZE is treated as an integer
        print(f"Processed {OFFSET} records")
    end_time = time.time()  # End timing
    execution_time = end_time - start_time
    print(f"\nExecution Time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    process_and_save_image()