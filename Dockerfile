FROM python:3.10-slim

RUN apt update && apt upgrade -y && apt install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt . RUN pip install --no-cache-dir -U pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m botuser USER botuser

CMD ["python", "bot.py"]
