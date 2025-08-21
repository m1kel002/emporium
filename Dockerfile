FROM python:3.11-slim

WORKDIR /emporium

# RUN apt-get update apt-get install libpq-dev python3-dev

RUN apt-get update && \
    apt-get install -y libpq-dev \
    python3-dev \
    gcc \
    python3.11-distutils
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
# CMD ["uwsgi", "--ini", "uwsgi.ini"]
