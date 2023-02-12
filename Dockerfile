FROM python:3.9
WORKDIR /app
ENV PYTHONPATH "$PYTHONPATH:/app/optimizers"
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app .
EXPOSE 5555
CMD ["python", "server.py"]
