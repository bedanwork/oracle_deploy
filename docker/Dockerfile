# Use official Python 3.10 image
FROM python:3.10

RUN apt-get update && apt-get install -y \
    libaio1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/oracle
RUN wget https://download.oracle.com/otn_software/linux/instantclient/219000/instantclient-basic-linux.x64-21.9.0.0.0dbru.zip \
    && unzip instantclient-basic-linux.x64-21.9.0.0.0dbru.zip \
    && rm instantclient-basic-linux.x64-21.9.0.0.0dbru.zip \
    && sh -c "echo /opt/oracle/instantclient_21_9 > /etc/ld.so.conf.d/oracle-instantclient.conf" \
    && ldconfig
    
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app
WORKDIR /app

# Default command (optional, can be changed later)
CMD ["python"]
