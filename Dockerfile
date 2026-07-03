FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py VERSION ./
COPY templates/ templates/

ENV DB_PATH=/data/shelf.db
VOLUME ["/data"]

EXPOSE 5000

CMD ["python", "app.py"]
