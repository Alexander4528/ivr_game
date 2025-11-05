FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for pygame
RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy game files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir pygame

# Create necessary directories if they don't exist
RUN mkdir -p "Sprites and objects" Music Sounds Save_files

# Set the entry point
CMD ["python", "main.py"]