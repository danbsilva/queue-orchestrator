FROM python:3.9-alpine3.18
WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY ./src ./src

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]