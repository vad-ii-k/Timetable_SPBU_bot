FROM python:3.10-alpine

ADD . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]