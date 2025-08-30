FROM python:3.11-slim

WORKDIR /emporium

RUN apt-get update && \
    apt-get install -y libpq-dev \
    python3-dev \
    gcc
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
