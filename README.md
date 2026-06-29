# OnyxPay Mock Bank Service

Stateless payment provider simulator for local development and automated tests.

It accepts an authorization request, returns `PENDING`, and selects one of five
configurable callback scenarios. It never moves real money.

> This service is for development and testing only.

## Flow

```text
Payment Orchestrator
    │ POST /authorize
    ▼
Mock Bank
    │ immediate PENDING response
    │ selected asynchronous scenario
    ▼
POST /provider-callbacks/mock-bank/{transaction_id}
    │
    ▼
Payment Orchestrator
```

## API

With the full Compose stack running, the service is available at
`http://localhost:8001`; the container listens on port `8000`.

### Authorize a payment

```http
POST /authorize
Content-Type: application/json
Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000
```

```json
{
  "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
  "amount": 10000,
  "currency": "COP",
  "notification_url": "https://merchant.example/webhooks/payments",
  "customer": {
    "first_name": "Juan",
    "last_name": "Bello",
    "personal_id": "123456789"
  }
}
```

`notification_url` is required by the shared transaction contract and must be
a valid HTTP or HTTPS URL. The Mock Bank validates it but does not call it; the
Webhook Service owns merchant delivery.

Example:

```bash
curl --request POST http://localhost:8001/authorize \
  --header "Content-Type: application/json" \
  --header "Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000" \
  --data '{
    "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
    "amount": 10000,
    "currency": "COP",
    "notification_url": "https://merchant.example/webhooks/payments",
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
  "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
  "provider_transaction_id": "mock_123e4567-e89b-12d3-a456-426614174000",
  "status": "PENDING",
  "message": "Mock bank authorization pending"
}
```

Callback body:

```json
{
  "provider_transaction_id": "mock_123e4567-e89b-12d3-a456-426614174000",
  "status": "APPROVED",
  "message": "Mock bank payment approved asynchronously"
}
```

The transaction ID is part of the callback URL, not the JSON body:

```text
http://payment-orchestrator-service:8001/provider-callbacks/mock-bank/{transaction_id}
```

Interactive OpenAPI documentation is available at
`http://localhost:8001/docs`.

## Callback scenarios

Every authorization selects one mutually exclusive scenario:

| Scenario | Default probability | Behavior |
| --- | ---: | --- |
| Approved | 50% | Sends `APPROVED` after 5 seconds |
| Declined | 20% | Sends `DECLINED` after 20 seconds |
| Duplicate | 10% | Sends `APPROVED`, waits 1 second, and sends it again |
| Early callback | 10% | Sends `APPROVED` before returning the HTTP response |
| No callback | 10% | Returns `PENDING` and sends no callback |

The five probabilities must add up to `1.0`, otherwise settings validation
prevents the application from starting.

## Configuration

| Variable | Default |
| --- | --- |
| `ORCHESTRATOR_CALLBACK_URL` | `http://payment-orchestrator-service:8001/provider-callbacks/mock-bank` |
| `APPROVED_AFTER_5_PROBABILITY` | `0.50` |
| `DECLINED_AFTER_20_PROBABILITY` | `0.20` |
| `DUPLICATE_CALLBACK_PROBABILITY` | `0.10` |
| `CALLBACK_BEFORE_RESPONSE_PROBABILITY` | `0.10` |
| `NO_CALLBACK_PROBABILITY` | `0.10` |
| `APPROVED_DELAY_SECONDS` | `5` |
| `DECLINED_DELAY_SECONDS` | `20` |
| `DUPLICATE_DELAY_SECONDS` | `1` |

For a standalone local orchestrator, override the callback URL:

```dotenv
ORCHESTRATOR_CALLBACK_URL=http://host.docker.internal:8002/provider-callbacks/mock-bank
```

## Health checks

- `GET /health/live`: process liveness.
- `GET /health/startup`: application startup.
- `GET /health/ready`: stateless simulator readiness.
- `GET /health`: backward-compatible basic check.

## Local development

```bash
make install
make format
make lint
make test
.venv/bin/uvicorn app.main:app --reload --port 8000
```

## Docker and Compose

```bash
docker build -t mock-bank-service .
docker run --rm -p 8001:8000 mock-bank-service
```

Published image:

```text
ghcr.io/onyxpayments/mock-bank-service:latest
```

For its normal callback network, run the complete stack:

```bash
cd ../infra
docker compose pull
docker compose up -d
```

## Project structure

```text
.
├── app
│   ├── api                    # Authorization route and HTTP schemas
│   ├── application            # Scenario selection
│   ├── domain                 # Customer and callback scenario models
│   ├── infrastructure         # Environment settings
│   └── main.py
├── tests
├── Dockerfile
├── makefile
└── requirements.txt
```

## Current limitations

- Failed callbacks are not retried or persisted by the Mock Bank.
- The incoming `Idempotency-Key` header is sent by the orchestrator but is not
  currently enforced by this simulator.
