FROM python:3.12-bookworm

ENV DEBIAN_FRONTEND=noninteractive

# 1. System dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    apt-transport-https \
    ca-certificates \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 2. Microsoft repo key (correct modern method)
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg

RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list

# 3. Install ODBC Driver 18
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# 4. App setup
WORKDIR /app
COPY . .

# 5. Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 6. Run app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
