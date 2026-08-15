FROM python:3.11-slim

WORKDIR /app

# Dependencies are copied and installed BEFORE the source code, so that editing
# your Python does not invalidate the (slow) pip install layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# SERVICE is set per-container in docker-compose.yml (gateway/orders/payments/bank).
# Shell form of CMD is used so ${SERVICE} is expanded at container start.
ENV SERVICE=gateway
CMD uvicorn ${SERVICE}.main:app --host 0.0.0.0 --port 8000
