FROM python:3.9-slim

# Set environment variables
ENV ORACLE_HOME=/opt/oracle/instantclient_21_9
ENV PATH=$ORACLE_HOME:$PATH
ENV LD_LIBRARY_PATH=$ORACLE_HOME
ENV http_proxy=deb.debian.org/debian
ENV https_proxy=deb.debian.org/debian
# Install Oracle Instant Client
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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app
WORKDIR /app

# Command to run the application
CMD ["python", "main.py"]
