# API GuardFlow

### Adaptive API Rate Limiting and Behavioral Abuse Detection

API GuardFlow is an adaptive API protection middleware built with **FastAPI, Redis, and Machine Learning**.

Unlike a traditional rate limiter that only counts requests, API GuardFlow analyzes **how a client behaves over time**. It combines fixed-window rate limiting, Redis-backed behavioral telemetry, an Isolation Forest anomaly detector, and interpretable behavioral rules to identify suspicious API usage such as rapid endpoint probing and scraping-like traffic.

---

## Why API GuardFlow?

Traditional API protection often relies on simple rules such as:

```text
10 requests per minute → block
```

This controls request volume, but request count alone does not describe how a client is interacting with an API.

For example, two clients can generate similar request volumes while exhibiting very different behavior:

| Client | Requests/min | Unique Paths | Error Rate | Behavior |
|---|---:|---:|---:|---|
| Normal client | 6 | 2 | 0% | Repeated, consistent API access |
| Suspicious client | 6 | 5 | 66.7% | Rapid endpoint probing |

API GuardFlow adds a behavioral detection layer on top of traditional rate limiting.

---

## Key Features

- Fixed-window API rate limiting
- Redis-backed request telemetry
- Sliding-window behavioral analysis
- Isolation Forest anomaly detection
- Interpretable behavioral abuse rules
- Temporary client throttling
- Temporary client blocking
- Redis-backed client security state
- Security event history
- Real-time monitoring dashboard
- FastAPI middleware architecture
- Simulated normal and suspicious traffic
- Automated tests for feature engineering
- Automated tests for decision logic

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      API Client      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │     GuardFlow Middleware     │
                    └──────────────┬───────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
              ┌──────────────┐           ┌──────────────┐
              │ Client State │           │ Redis Rate   │
              │ Check        │           │ Limiter      │
              └──────┬───────┘           └──────┬───────┘
                     │                           │
                     │                           ▼
                     │                    ┌──────────────┐
                     │                    │    FastAPI   │
                     │                    │      API     │
                     │                    └──────┬───────┘
                     │                           │
                     │                           ▼
                     │                  ┌─────────────────┐
                     │                  │ Feature         │
                     │                  │ Extraction      │
                     │                  └────────┬────────┘
                     │                           │
                     │                           ▼
                     │                  ┌─────────────────┐
                     │                  │ Redis Feature   │
                     │                  │ Store           │
                     │                  └────────┬────────┘
                     │                           │
                     │                           ▼
                     │                  ┌─────────────────┐
                     │                  │ Sliding Window  │
                     │                  │ Aggregation     │
                     │                  └────────┬────────┘
                     │                           │
                     │                           ▼
                     │                  ┌─────────────────┐
                     │                  │ Isolation       │
                     │                  │ Forest          │
                     │                  └────────┬────────┘
                     │                           │
                     │                           ▼
                     │                  ┌─────────────────┐
                     │                  │ Decision Engine │
                     │                  │ ML + Rules      │
                     │                  └────────┬────────┘
                     │                           │
                     │              ┌────────────┼────────────┐
                     │              ▼            ▼            ▼
                     │           ALLOW        THROTTLE       BLOCK
                     │
                     └──────────────────────────────────────────┐
                                                                │
                                                                ▼
                                                     ┌────────────────────┐
                                                     │ Security Event     │
                                                     │ Store              │
                                                     └─────────┬──────────┘
                                                               │
                                                               ▼
                                                     ┌────────────────────┐
                                                     │ Monitoring         │
                                                     │ Dashboard          │
                                                     └────────────────────┘
```

---

## How It Works

### 1. Request arrives

An incoming request first passes through the GuardFlow middleware.

The middleware identifies the client and checks whether the client already has a temporary security state.

---

### 2. Cached client state is checked

If a client has previously been classified as suspicious, its state is stored in Redis.

Possible states are:

```text
ALLOW
THROTTLE
BLOCK
```

A cached `BLOCK` state prevents subsequent requests from reaching the API while the temporary state is active.

A cached `THROTTLE` state introduces a delay before processing the request.

---

### 3. Traditional rate limiting

GuardFlow also maintains a Redis fixed-window rate limiter.

The current demonstration configuration is:

```text
10 requests / 60 seconds / client
```

Requests beyond the configured limit receive:

```http
429 Too Many Requests
```

This provides a traditional protection layer independent of behavioral detection.

---

### 4. Request is processed

If the request passes the initial protection layers, it is forwarded to the FastAPI application.

GuardFlow then records information about the request and response.

---

### 5. Behavioral features are extracted

The system tracks several characteristics of client behavior:

| Feature | Description |
|---|---|
| `request_count` | Number of requests in the analysis window |
| `requests_per_second` | Request frequency |
| `requests_per_minute` | Normalized request frequency |
| `unique_paths` | Number of distinct API paths |
| `path_entropy` | Diversity of accessed paths |
| `error_rate` | Percentage of requests returning 4xx/5xx |
| `avg_payload_size` | Average request payload size |
| `avg_processing_time` | Average API processing time |
| `avg_inter_request_time` | Average time between requests |

The Isolation Forest currently uses:

```text
requests_per_second
unique_paths
path_entropy
error_rate
avg_payload_size
avg_processing_time
avg_inter_request_time
```

`requests_per_minute` is retained for dashboard and event reporting but is not passed to the ML model because it is redundant with request frequency.

---

## Sliding-Window Analysis

Raw request observations are stored in Redis.

GuardFlow analyzes recent traffic using a sliding window.

The current analysis window is:

```text
60 seconds
```

This allows the system to reason about recent client behavior instead of treating each request independently.

For example:

```text
/api/data
/unknown1
/unknown2
/api/data
/unknown3
/unknown4
```

provides more behavioral information than simply knowing:

```text
6 requests
```

---

# Machine Learning

## Isolation Forest

GuardFlow uses an **Isolation Forest** from `scikit-learn` for unsupervised anomaly detection.

The model is trained using simulated normal traffic.

Current model configuration:

```text
Algorithm:       Isolation Forest
Estimators:      200
Contamination:   0.01
Random State:    42
```

The model produces:

- An anomaly prediction
- A decision score

A lower decision score represents behavior that is more unusual relative to the training distribution.

---

## Why combine ML with behavioral rules?

During development, testing showed that an unusual traffic pattern could receive a lower Isolation Forest score than normal traffic without crossing the model's binary anomaly threshold.

For example:

```text
Normal traffic
Score ≈ 0.081
Prediction = Normal

Suspicious traffic
Score ≈ 0.028
Prediction = Normal
```

The suspicious traffic had a lower anomaly score, but the binary prediction alone did not classify it as an anomaly.

Instead of forcing the ML model to make every security decision, GuardFlow combines the anomaly score with explicit behavioral signals.

This creates a layered decision process:

```text
                 Request Behavior
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
       Isolation Forest     Behavioral Rules
              │                   │
              └─────────┬─────────┘
                        │
                        ▼
                 Decision Engine
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
            ALLOW    THROTTLE    BLOCK
```

---

# Behavioral Detection Rules

The current decision engine contains interpretable rules for strong abuse indicators.

### Strong endpoint probing

A client is blocked when:

```text
error_rate >= 0.5
AND
unique_paths >= 5
AND
path_entropy >= 2.0
```

### Rapid endpoint probing

A client is throttled when:

```text
avg_inter_request_time < 0.2 seconds
AND
unique_paths >= 5
```

These are explicit behavioral rules and are **not presented as ML predictions**.

The final decision combines:

```text
Isolation Forest result
+
Behavioral rules
```

---

# Decision Flow

The decision engine produces one of three outcomes:

```text
ALLOW
THROTTLE
BLOCK
```

### ALLOW

The request is considered acceptable and continues normally.

### THROTTLE

The request is delayed before returning the response.

Current demonstration delay:

```text
1.5 seconds
```

### BLOCK

The client receives:

```http
403 Forbidden
```

A temporary client state is also stored in Redis so subsequent requests can be blocked before reaching the API.

---

# Redis State

Redis is used for several parts of the system.

### Rate-limit counters

```text
rate_limit:{client_ip}:{window}
```

### Request feature history

```text
request_features:{client_ip}
```

### Temporary client security state

```text
guardflow:client_state:{client_ip}
```

### Security events

```text
guardflow:security_events
```

The temporary client state currently has a TTL of:

```text
60 seconds
```

Request feature history and security events are retained longer for analysis and dashboard purposes.

---

# Security Event Store

Every analyzed request contributes to the security event history.

Events contain information such as:

```text
timestamp
client IP
decision
anomaly score
anomaly prediction
requests/minute
unique paths
error rate
path entropy
```

This makes it possible to inspect how a client's behavior changed over time.

For example:

```text
ALLOW
   ↓
ALLOW
   ↓
ALLOW
   ↓
ALLOW
   ↓
BLOCK
```

The dashboard can preserve this historical progression even after a temporary client state expires.

---

# Monitoring Dashboard

GuardFlow includes a lightweight real-time monitoring dashboard.

Open:

```text
http://127.0.0.1:8000/dashboard
```

The dashboard displays:

- Total clients
- Allowed clients
- Throttled clients
- Blocked clients
- Requests per minute
- Unique paths
- Error rate
- Path entropy
- Isolation Forest score
- Current security status
- Recent security events

---

## Example Detection

A suspicious test client produced:

```text
Client IP:          127.0.0.3
Requests/minute:   6
Unique paths:      5
Error rate:        66.7%
Path entropy:      2.2516
ML score:          ~0.0376
Decision:          BLOCK
```

A normal test client produced:

```text
Client IP:          127.0.0.2
Requests/minute:   6
Unique paths:      2
Error rate:        0%
Path entropy:      ~0.9183
ML score:          ~0.0737
Decision:          ALLOW
```

This demonstrates that similar request volume can still result in different security decisions based on client behavior.

---

# API Endpoints

## Root

```http
GET /
```

Returns basic service information.

Example:

```json
{
  "service": "API GuardFlow",
  "status": "running"
}
```

---

## Protected API

```http
GET /api/data
```

Example response:

```json
{
  "message": "This is protected API data"
}
```

---

## Product API

```http
GET /api/products/{product_id}
```

Example:

```http
GET /api/products/42
```

---

## Health Check

```http
GET /health
```

Checks the API and Redis connection.

---

## Debug: Request Features

```http
GET /debug/features
```

Returns recently stored request observations for the current client.

---

## Debug: Aggregated Features

```http
GET /debug/aggregated-features
```

Returns the current sliding-window behavioral features.

---

## Debug: Client Analysis

```http
GET /debug/analyze
```

Runs the current detector and decision engine for the requesting client.

> The `/debug/*` endpoints are intended for development and demonstration and should not be publicly exposed in a production deployment without appropriate protection.

---

# Project Structure

```text
smart-rate-limiter/
│
├── app/
│   ├── dashboard/
│   │   └── routes.py
│   │
│   ├── middleware/
│   │   ├── feature_extractor.py
│   │   └── rate_limiter.py
│   │
│   ├── ml/
│   │   ├── anomaly_detector.py
│   │   ├── decision_engine.py
│   │   ├── detector_service.py
│   │   ├── feature_builder.py
│   │   ├── features.py
│   │   ├── isolation_forest.joblib
│   │   └── train.py
│   │
│   ├── redis/
│   │   ├── client.py
│   │   ├── client_state.py
│   │   ├── feature_store.py
│   │   └── security_events.py
│   │
│   └── main.py
│
├── simulation/
│   ├── generate_training_data.py
│   ├── test_decision_engine.py
│   ├── test_live_traffic.py
│   └── test_two_clients.py
│
├── tests/
│   └── test_feature_builder.py
│
├── simulation/
│   └── normal_traffic.csv
│
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Tech Stack

## Backend

- Python
- FastAPI
- Starlette Middleware

## Machine Learning

- scikit-learn
- Isolation Forest
- pandas
- NumPy
- joblib

## Infrastructure

- Redis
- Docker
- Docker Compose

## Testing

- pytest
- Simulated client traffic
- Multi-client local traffic testing

## Frontend

- HTML
- CSS
- Vanilla JavaScript

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/jethasriM/smart-rate-limiter.git
cd smart-rate-limiter
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# Start Redis

API GuardFlow uses Redis for rate limiting, request history, client state, and security events.

Start Redis using Docker Compose:

```powershell
docker compose up -d
```

Verify that Redis is running:

```powershell
docker exec abuse-sentinel-redis redis-cli ping
```

Expected output:

```text
PONG
```

---

# Train the Model

Generate the simulated normal-traffic dataset:

```powershell
python simulation/generate_training_data.py
```

Train the Isolation Forest:

```powershell
python -m app.ml.train
```

The trained model is saved to:

```text
app/ml/isolation_forest.joblib
```

---

# Run the API

From the project root:

```powershell
python -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

Dashboard:

```text
http://127.0.0.1:8000/dashboard
```

---

# Running Tests

Run the automated test suite:

```powershell
pytest
```

The current test suite validates the implemented feature and behavioral logic.

Run the decision engine simulation:

```powershell
python -m simulation.test_decision_engine
```

Expected behavior:

```text
Normal traffic       → ALLOW
Moderate anomaly     → THROTTLE
Strong anomaly       → BLOCK
```

---

# Live Traffic Simulation

GuardFlow includes a simulation for testing two different clients.

Run:

```powershell
python simulation/test_two_clients.py
```

The simulation generates:

### Normal client

```text
127.0.0.2
```

with repeated API access and slower request intervals.

### Suspicious client

```text
127.0.0.3
```

with rapid access to multiple endpoints, including unknown endpoints.

A typical result is:

```text
127.0.0.2 → ALLOW
127.0.0.3 → BLOCK
```

The suspicious client can then receive subsequent `403` responses because its temporary security state is cached in Redis.

---

# Example Behavioral Detection

The suspicious traffic pattern used for demonstration includes requests such as:

```text
/api/data
/unknown1
/unknown2
/api/data
/unknown3
/unknown4
/api/data
/unknown5
```

This creates a combination of:

```text
High endpoint diversity
+
High error rate
+
High path entropy
+
Rapid requests
```

The behavioral decision layer can therefore classify the client as suspicious even when the Isolation Forest's binary prediction alone does not cross its anomaly threshold.

---

# Rate Limiting vs Behavioral Detection

API GuardFlow deliberately uses both mechanisms.

| Protection | Purpose |
|---|---|
| Fixed-window rate limiter | Controls request volume |
| Feature extraction | Captures client behavior |
| Sliding window | Aggregates recent activity |
| Isolation Forest | Detects unusual behavioral patterns |
| Behavioral rules | Detects interpretable abuse signals |
| Client state | Enforces temporary decisions |
| Security events | Preserves detection history |

The two layers complement each other:

```text
Traditional protection
        +
Behavioral protection
        =
Adaptive API protection
```

---

# Design Considerations

## ML is not the only decision-maker

The Isolation Forest provides an anomaly signal rather than being treated as a complete security policy.

The final decision can incorporate both:

```text
ML anomaly score
+
Behavioral evidence
```

This makes the system easier to reason about and debug.

---

## Minimum data requirement

The detector requires at least three recent observations before performing behavioral analysis.

This prevents the system from making decisions based on an extremely small amount of traffic.

---

## Post-response analysis

New behavioral observations are currently collected after the API request is processed.

Therefore, the request that first provides enough evidence for a new behavioral decision may reach the API.

Once the client state is cached, subsequent suspicious requests can be blocked before reaching the API.

---

# Current Limitations

This project is a prototype and demonstration of behavior-aware API protection.

Current limitations include:

- The Isolation Forest is trained on simulated normal traffic.
- The training data does not represent the full diversity of real-world API traffic.
- Behavioral thresholds are manually defined.
- The current system does not use a production attack dataset.
- Client identification is based on IP address.
- Temporary client state uses a short TTL.
- The middleware currently performs analysis locally within the application process.
- The current fixed-window limiter can be replaced with more advanced distributed rate-limiting strategies for production deployments.
- The dashboard is designed for demonstration rather than production security operations.

The project should therefore be considered an **experimental adaptive API protection system**, not a production-ready security gateway.

---

# Future Improvements

Potential extensions include:

- Replace simulated training data with real anonymized API telemetry
- Add labeled abuse datasets for supervised evaluation
- Compare Isolation Forest with other anomaly detection algorithms
- Add model evaluation and threshold calibration
- Introduce adaptive thresholds based on API endpoint behavior
- Add per-endpoint behavioral profiles
- Add user/API-key based client identity in addition to IP
- Add persistent incident tracking
- Add Redis-based distributed counters
- Add Prometheus metrics
- Add Grafana monitoring
- Add Dockerized API deployment
- Add CI/CD with GitHub Actions
- Add authentication and authorization for the dashboard
- Add production-grade logging
- Add alerting for repeated abuse
- Add model retraining based on validated traffic patterns

---

# Testing Results

The implemented system has been tested with both automated and live traffic.

### Automated tests

```text
pytest

4 passed
```

### Decision engine

```text
Normal traffic       → ALLOW
Moderate anomaly     → THROTTLE
Strong anomaly       → BLOCK
```

### Live behavioral test

Normal client:

```text
127.0.0.2
→ ALLOW
```

Suspicious client:

```text
127.0.0.3
→ BLOCK
```

The suspicious client was successfully transitioned into a temporary Redis-backed blocked state.

---

# What This Project Demonstrates

API GuardFlow demonstrates practical implementation of:

- API middleware design
- Redis state management
- Rate limiting
- Behavioral telemetry
- Feature engineering
- Sliding-window analysis
- Unsupervised machine learning
- Isolation Forest anomaly detection
- Rule-based decision systems
- Security event tracking
- Real-time dashboards
- FastAPI development
- Docker-based infrastructure
- Automated testing
- Local traffic simulation

The main engineering idea is to move beyond:

```text
"How many requests did this client make?"
```

toward:

```text
"How is this client behaving?"
```

---

# License

This project is intended for educational, experimental, and portfolio purposes.

Add an appropriate open-source license before distributing the project publicly.
