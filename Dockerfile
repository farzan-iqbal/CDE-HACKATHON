FROM apache/airflow:2.7.1-python3.9

USER root
# Install SQL Server Drivers (just in case) & Postgres Client
RUN apt-get update && apt-get install -y \
    wget unzip gnupg curl unixodbc-dev libpq-dev gcc \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Install Google Chrome for Selenium
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable

USER airflow
# Upgrade pip first to avoid JSON errors
RUN pip install --upgrade pip
COPY Requirements.txt .
# Install with extra timeout to handle network issues
RUN pip install --no-cache-dir --default-timeout=100 -r Requirements.txt