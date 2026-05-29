# OnyxPay Mock Bank Service

## Overview

The Mock Bank Service is a simulated payment provider used for development and testing purposes within the OnyxPay platform.

Its primary responsibility is to receive payment authorization requests and return a simulated payment result without interacting with any real banking institution.

This service allows developers to test payment flows, transaction orchestration, webhooks, and failure scenarios in a controlled environment.

---

## Features

* Health check endpoint
* Payment authorization simulation
* Configurable transaction outcomes
* FastAPI-based REST API
* Dockerized deployment
* Automated testing with Pytest
* CI validation through GitHub Actions

---

## API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

---

### Authorize Payment

```http
POST /authorize
```

Request:

```json
{
  "transaction_id": "trx_123",
  "amount": 10000,
  "currency": "COP",
  "country": "CO"
}
```

Response:

```json
{
  "transaction_id": "trx_123",
  "provider_transaction_id": "mock_trx_123",
  "status": "APPROVED",
  "message": "Mock bank authorization approved"
}
```

---

## Running Locally

Create a virtual environment:

```bash
python3 -m venv .venv
```

Install dependencies:

```bash
make install
```

Start the application:

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://localhost:8000/docs
```

---

## Running Tests

```bash
make test
```

---

## Code Quality

Run formatting:

```bash
make format
```

Run linting:

```bash
make lint
```

---

## Docker

Build image:

```bash
docker build -t onyxpay-mock-bank-service .
```

Run container:

```bash
docker run -p 8000:8000 onyxpay-mock-bank-service
```

---

## Future Enhancements

* Asynchronous transaction processing
* Delayed status updates
* Callback simulation
* Configurable approval and decline rates
* Integration with RabbitMQ
* Persistence layer for transaction history

---

## Project Structure

```text
.
├── app
│   ├── api
│   ├── application
│   ├── domain
│   ├── infrastructure
│   └── main.py
├── tests
├── Dockerfile
├── Makefile
├── requirements.txt
└── README.md
```
