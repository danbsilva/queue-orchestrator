FROM python:3.9-alpine3.18
WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY src ./src
COPY .env .
#COPY entrypoint.sh .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt
COPY ./helpers/flask_jsglue.py ../usr/local/lib/python3.9/site-packages/flask_jsglue.py
#RUN chmod +x entrypoint.sh

#CMD ["sh", "entrypoint.sh"]







