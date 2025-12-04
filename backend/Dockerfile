# backend/Dockerfile
FROM python:3.10.12-slim

WORKDIR /app

# copy requirements first
COPY requirements.txt .

# upgrade pip first
RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# then install packages
RUN pip install --no-cache-dir -r requirements.txt

# copy rest of code
COPY . .

EXPOSE 5000

# CMD ["python", "run.py"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
