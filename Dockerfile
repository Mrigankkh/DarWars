# Use Python 3.10 base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install pygbag
RUN pip install --no-cache-dir pygbag

# Set working directory
WORKDIR /app

# Copy requirements and install Python deps (pygame, numpy)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into the container
COPY . .

# Start with interactive shell — you control the build/run
CMD ["/bin/bash"]
