FROM python:3
WORKDIR /app
ENV PYTHONPATH "$PYTHONPATH:/app/optimizers"
COPY app .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "server.py"]
