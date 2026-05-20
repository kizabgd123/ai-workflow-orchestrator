FROM python:3.11-slim

WORKDIR /app

# Install git and other system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Meeseeks environment variables
ENV MEESEEKS_EXISTENCE_IS_PAIN=true
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
