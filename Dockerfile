FROM python:3.11-slim AS backend

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8800

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8800"]
