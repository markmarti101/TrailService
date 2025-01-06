# Use Docker BuildKit syntax (allows specifying platform in FROM)
# syntax=docker/dockerfile:1.4

FROM --platform=linux/amd64 python:3.9-slim-bullseye

# Set environment variables to prevent Python from writing .pyc files and to enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# 1. Install dependencies for Microsoft repositories
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# 2. Add Microsoft’s GPG key and repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list -o /etc/apt/sources.list.d/mssql-release.list

# 3. Install msodbcsql17 and unixodbc-dev (ODBC dependencies)
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql17 \
    unixodbc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements.txt file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code into the container
COPY . /app/

# Expose the port your application will use
EXPOSE 8000

# Set the default command to run your application
CMD ["python", "microservice.py"]
