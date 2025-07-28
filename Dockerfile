FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files to container
COPY . /app

# Copy pretrained models and nltk data
COPY pretrained_models /app/pretrained_models
COPY nltk_data /root/nltk_data

# Set environment variable for nltk
ENV NLTK_DATA=/root/nltk_data

# Install system dependencies
RUN apt-get update && apt-get install -y gcc poppler-utils && apt-get clean

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add this line after installing nltk
RUN python3 -m nltk.downloader punkt

# Run the main script
CMD ["python", "app/main.py"]