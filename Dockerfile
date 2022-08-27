FROM python:3
WORKDIR /app
COPY app/* .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "server.py"]
