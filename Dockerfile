FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++

# Add Microsoft repo key (modern method)
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg && \
    curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | \
    sed 's#deb #deb [signed-by=/etc/apt/keyrings/microsoft.gpg] #' \
    > /etc/apt/sources.list.d/mssql-release.list

# Install SQL Server ODBC Driver
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
