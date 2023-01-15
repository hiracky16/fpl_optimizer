FROM python:3
WORKDIR /app
ENV PYTHONPATH "$PYTHONPATH:/app/optimizers"
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app .
CMD ["python", "server.py"]
