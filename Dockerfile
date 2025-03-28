# Use the latest stable Python image
FROM python:3.10-slim

# Update and install dependencies
RUN apt update && apt upgrade -y && apt install -y git

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt

# Copy bot files into the container
COPY . .

# Start the bot
CMD ["python", "bot.py"]
