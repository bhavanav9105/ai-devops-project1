FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Train model on first build so pkl is always fresh
RUN python train_model.py

# Create data directory for SQLite persistence
RUN mkdir -p /app/data

EXPOSE 5000

CMD ["python", "app.py"]
