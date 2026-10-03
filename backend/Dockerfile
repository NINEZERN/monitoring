FROM aquasec/trivy:0.69.3 AS trivy
FROM python:3.12.10-slim
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
WORKDIR /app
COPY requirements.txt requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
RUN useradd -m -u 10001 lens && mkdir /data && chown lens:lens /data
COPY . .
USER lens
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
