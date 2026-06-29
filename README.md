# OnyxPay Mock Bank Service

Stateless payment provider simulator for local development and automated tests.

The service emulates the asynchronous behavior of an external bank without
moving real money. It accepts an authorization request, immediately returns a
`PENDING` response, waits five seconds, and then sends an `APPROVED` callback to
the Payment Orchestrator.

> This service is for development and testing only. It must never be used as a
> real payment provider.

## Responsibilities

- Validate mock authorization requests.
- Return a deterministic provider transaction identifier.
- Respond immediately with a pending status.
- Simulate asynchronous provider processing.
- Send an approval callback to the Payment Orchestrator.
- Remain stateless; transaction persistence belongs to the orchestrator.

## Authorization Flow

```text
Payment Orchestrator
    │
    │ POST /authorize
    ▼
Mock Bank
    │
    ├── Returns PENDING immediately
    │
    └── Waits 5 seconds
             │
             │ POST /provider-callbacks/mock-bank/{transaction_id}
             ▼
       Payment Orchestrator
              APPROVED
```

## API

When the platform is running through Docker Compose, the Mock Bank is available
at `http://localhost:8001`.

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

### Authorize Payment

```http
POST /authorize
Content-Type: application/json
```

Request:

```json
{
  "transaction_id": "9d03c06f-66b6-4495-82a7-e2fa41d740e4",
  "amount": 10000,
  "currency": "COP",
  "customer": {
    "first_name": "Juan",
    "last_name": "Bello",
    "personal_id": "123456789"
  }
}
```

Example:

```bash
curl -X POST http://localhost:8001/authorize \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "9d03c06f-66b6-4495-82a7-e2fa41d740e4",
    "amount": 10000,
    "currency": "COP",
    "customer": {
      "first_name": "Juan",
      "last_name": "Bello",
      "personal_id": "123456789"
    }
  }'
```

Immediate response:

```json
{
  "transaction_id": "9d03c06f-66b6-4495-82a7-e2fa41d740e4",
  "provider_transaction_id": "mock_9d03c06f-66b6-4495-82a7-e2fa41d740e4",
  "status": "PENDING",
  "message": "Mock bank authorization pending"
}
```

Five seconds later, the service sends:

```json
{
  "transaction_id": "9d03c06f-66b6-4495-82a7-e2fa41d740e4",
  "provider_transaction_id": "mock_9d03c06f-66b6-4495-82a7-e2fa41d740e4",
  "status": "APPROVED",
  "message": "Mock bank payment approved asynchronously"
}
```

to:

```text
http://payment-orchestrator-service:8001/provider-callbacks/mock-bank/{transaction_id}
```

Interactive API documentation:

```text
http://localhost:8001/docs
```

## Running the Full Platform

The Mock Bank is designed to run inside the OnyxPay Compose network:

```bash
cd ../infra
docker compose pull
docker compose up -d
```

## Local Development

Requirements:

- Python 3.13
- Make

Install dependencies:

```bash
make install
```

Run the service:

```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Run quality checks:

```bash
make format
make lint
make test
```

> The callback URL currently uses the orchestrator's Docker Compose hostname.
> A standalone local instance can accept authorization requests, but its
> callback will not reach an orchestrator outside that network unless the URL
> is externalized or changed.

## Docker

Build and run the image:

```bash
docker build -t mock-bank-service .
docker run --rm -p 8001:8000 mock-bank-service
```

Published image:

```text
ghcr.io/onyxpayments/mock-bank-service:latest
```

## Project Structure

```text
.
├── app
│   ├── api                 # Authorization routes and schemas
│   ├── application         # Application layer placeholder
│   ├── domain              # Shared payment models
│   ├── infraestructure     # Adapter placeholders
│   └── main.py             # FastAPI entry point
├── tests                   # Health, validation, and callback tests
├── Dockerfile
├── makefile
└── requirements.txt
```

## CI/CD

GitHub Actions runs formatting checks, tests, and a Docker build. Pushes to
`main` publish:

```text
ghcr.io/onyxpayments/mock-bank-service:latest
ghcr.io/onyxpayments/mock-bank-service:<commit-sha>
```

## Current Limitations

- Failed callback deliveries are not retried or persisted.
- RabbitMQ and repository modules are placeholders.

## Probabilistic callback scenarios

Each authorization selects one mutually exclusive scenario:

| Scenario | Default probability | Behavior |
| --- | ---: | --- |
| Approved | 50% | Sends `APPROVED` after 5 seconds |
| Declined | 20% | Sends `DECLINED` after 20 seconds |
| Duplicate | 10% | Sends the same `APPROVED` callback twice |
| Early callback | 10% | Sends `APPROVED` before the HTTP response |
| No callback | 10% | Leaves the transaction pending |

The probabilities and delays are configurable through environment variables.
The five probability values must add up to `1.0`; otherwise the service
refuses to start. See `.env.example` for the complete configuration.

## Health probes

- `GET /health/live` checks that the API process can respond.
- `GET /health/startup` confirms application startup completed.
- `GET /health/ready` confirms the stateless simulator is ready.
- `GET /health` remains available for backward compatibility.
