# Sports League Scoreboard AI (`ScorePulse`)

An AI-assisted full-stack application that manages sports match results, automatically generates engaging match recaps using Large Language Models via OpenRouter API, and incorporates end-to-end telemetry with an AI-driven automatic incident responder.

Built as part of **Homework 3 & Homework 4** for the *AI Dev Tools Zoomcamp 2026*.

---

## Tech Stack

* **Frontend**: HTML5, Modern JavaScript (Fetch API), CSS3
* **Backend**: Python 3.12, FastAPI, Uvicorn
* **Database**: PostgreSQL (Local Docker / Yandex Managed Service for PostgreSQL)
* **LLM Gateway**: OpenRouter API (`inclusionai/ling-3.0-flash-vl:free`)
* **Package Manager**: `uv`
* **Observability & Telemetry**:
  * **OpenTelemetry**: Metrics, Logs, Traces instrumentation & OTel Collector
  * **Prometheus**: Time-series metric storage
  * **Grafana Loki**: Log aggregation
  * **Grafana Tempo**: Distributed tracing
  * **Grafana**: Visual dashboards & HTTP Webhook Alerting
* **Automated Incident Responder**: Python headless AI agent (`incident-response/`)
* **Containerization**: Docker, Docker Compose, Nginx
* **Infrastructure as Code (IaC)**: Terraform (`infra/`)
* **Cloud Provider (Yandex Cloud)**:
  * **YCR**: Yandex Container Registry
  * **Serverless**: Yandex Serverless Containers
  * **Managed Database**: Yandex Managed Service for PostgreSQL
  * **Network & Security**: VPC Network, Subnets, IAM Roles, and Service Accounts
* **CI/CD**: GitHub Actions (Linting, Integration Tests, Image Build, Auto-deploy)

---

## Architecture & Telemetry Loop

```mermaid
flowchart TD
    subgraph CICD["CI/CD Pipeline"]
        Dev["Developer Push"] --> GHA["GitHub Actions CI/CD"]
        GHA --> Tests["Run Tests"]
        GHA --> Build["Build & Push Image"]
    end

    subgraph Infra["Yandex Cloud Infrastructure"]
        TF["Terraform (infra/)\n- VPC / Subnets\n- Managed PostgreSQL\n- YCR & IAM Roles"] --> YCS["Yandex Cloud Services"]
        Build --> YCR["Yandex Container Registry"]
        YCR --> YCS
        YCS --> Serverless["Serverless Containers"]
        Serverless <--> DB[(Managed PostgreSQL)]
    end

    subgraph Telemetry["Observability Loop"]
        Req["App Requests"] --> SDK["OTel SDK"]
        SDK --> Collector["OTel Collector"]
        
        Collector --> Prom["Prometheus\n(Metrics)"]
        Collector --> Loki["Loki\n(Logs)"]
        Collector --> Tempo["Tempo\n(Traces)"]
        
        Prom --> Grafana["Grafana Dashboard"]
        Loki --> Grafana
        Tempo --> Grafana
        
        Grafana -- "Firing 5xx Alert" --> Webhook["POST /alerts Webhook"]
        Webhook --> Agent["Incident Responder Agent\n(Headless Investigation & Fix)"]
    end
```




## Repository Structure

```
.
├── .github/workflows/
│   ├── ci.yml              # Linting, Unit & Integration tests, Docker build
│   └── deploy.yml          # CD pipeline deploying to Yandex Cloud
├── backend/                # FastAPI application core with OpenTelemetry SDK
├── frontend/               # Static UI assets
├── observability/          # Monitoring infrastructure setup
│   ├── collector.yaml      # OpenTelemetry Collector config
│   ├── prometheus.yml     # Prometheus scrape targets
│   ├── loki.yaml           # Loki log storage configuration
│   ├── tempo.yaml          # Tempo trace storage configuration
│   ├── dashboard.json      # Grafana dashboard definitions
│   └── alerts.yaml         # Grafana alert rules (5xx HTTP status monitoring)
├── incident-response/      # Automated incident responder service
│   ├── app.py              # Webhook receiver (POST /alerts on port 8001)
│   ├── collect-evidence.sh # Script gathering logs, traces, and metrics
│   ├── responder-task.md   # System prompt for headless coding agent
│   └── autonomy-policy.yaml# Execution limits & authorization rules
├── infra/                  # Terraform manifests for Yandex Cloud infrastructure
│   ├── main.tf             # Core provider and module definitions
│   ├── variables.tf        # Infrastructure input variables
│   ├── outputs.tf          # Output IDs (Registry ID, Container URL, DB Host)
│   └── terraform.tfvars    # Target environment configuration
├── tests/
│   ├── unit/               # Unit tests for business logic
│   └── integration/        # End-to-end and integration tests
├── docs/
│   ├── testing.md          # Comprehensive testing guide
│   ├── deployment.md       # Yandex Cloud setup & deployment guide
│   └── release-process.md  # Release management guidelines
├── Dockerfile              # Multi-stage container build
└── docker-compose.yml      # Local dev stack (FastAPI, Postgres, OTel stack, Grafana)
```

## Infrastructure Provisioning (Terraform)

Before deploying the application via CI/CD, set up the cloud infrastructure in Yandex Cloud using Terraform:

```
cd infra

# Initialize Terraform working directory and download providers
terraform init

# Review execution plan
terraform plan

# Apply infrastructure changes
terraform apply
```

Terraform provisions:

- VPC Network and Subnets.
- Yandex Container Registry (YCR).
- Yandex Managed Service for PostgreSQL cluster and database.
- Yandex Serverless Container resource and execution IAM service account.

Export outputs (e.g., registry_id, container_name, database_host) to populate your GitHub Secrets.

## Initial Environment Setup

Prerequisites
Ensure you have the following installed on your machine:

- Python >= 3.12
- uv (Fast Python package installer)
- Docker & Docker Compose
- Terraform >= 1.5.0
- Yandex Cloud CLI (yc)

1. Clone Repository & Prepare Configuration

Clone the repository and copy the environment template:

```
git clone [https://gitlab.com/ai-tools-20261/hw3.git](https://gitlab.com/ai-tools-20261/hw3.git)
cd hw3
cp .env.example .env
```

2. Configure Environment Variables

Edit .env or env.sh and set your OpenRouter API key:

```
export OPENROUTER_BASE_URL="[https://openrouter.ai/api/v1](https://openrouter.ai/api/v1)"
export OPENROUTER_MODEL="inclusionai/ling-3.0-flash-vl:free"
export OPENROUTER_API_KEY="sk-or-v1-YOUR-ACTUAL-API-KEY"
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/scoreboard"
```

Apply variables into your current shell session:

```
source env.sh
```

## Running Locally with Full Observability Stack

Start the entire application stack including Order/Match Tracker, OpenTelemetry Collector, Prometheus, Loki, Tempo, and Grafana:

```
docker compose up --build -d --wait
```

### Local Services & Ports

- Application API: http://localhost:8000
- Health Check: curl http://localhost:8000/health (or /healthz) -> {"status":"ok"}
- Grafana UI: http://localhost:3000 (Default credentials: admin / admin)
- Incident Responder: http://localhost:8001

## Observability & Incident Response Workflow (Homework 4)

1. Verification of Endpoint Health & Metrics
Check application health:

```
curl -i http://localhost:8000/healthz
```

Expected response: {"status":"ok"} with HTTP status 200.

2. Inspecting Telemetry (Metrics, Logs & Traces)

Request standard match/order details:

```
curl -i http://localhost:8000/api/orders/standard-10010
```

Metrics & Traces: Recorded with HTTP status code 200.
Request non-existing item:

```
curl -i http://localhost:8000/api/orders/standard-1002
```

- Grafana Telemetry: Records HTTP status 404 (Client error).
- Alert Status: Remains Normal because 404 does not trigger 5xx server error alerts.

3. Testing Automated Incident Responder

Send a simulated firing alert payload to the responder endpoint:

```
curl -X POST http://localhost:8001/alerts \
  -H 'Content-Type: application/json' \
  -d '{"alerts":[{"status":"firing","labels":{"alertname":"ResponderTest","test":"true"},"annotations":{"summary":"Test notification; no incident to fix"}}]}'
```

The agent starts automatically in headless mode, processes the event, and logs the response:

No incident to fix.

4. End-to-End Automatic Incident Investigation & Fix

Trigger an express order processing failure:

```
curl -i http://localhost:8000/api/orders/express-1002
```

- Root Cause: An edge-case bug where express delivery date calculations try to compute a day that does not exist in the target month.
- Automated Action: Grafana triggers a 5xx alert webhook -> Incident Responder captures evidence -> Headless AI Coding Agent investigates the code base -> Generates and verifies a fix.

## Running the Project in Yandex Cloud / CI/CD

This project uses GitHub Actions for automated testing and continuous delivery:

- CI (.github/workflows/ci.yml): Executes linter, unit tests, integration tests against Postgres, and verifies the Docker build on pull requests.
- CD (.github/workflows/deploy.yml): Pushes container images to Yandex Container Registry (YCR) and updates Yandex Serverless Containers on push to main.

For detailed setup instructions, refer to:

- docs/testing.md — Local and CI testing instructions.
- docs/deployment.md — Terraform and Yandex Cloud deployment guide.
- docs/release-process.md — Branching and release management.

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` / `/healthz` | Health check endpoint for ingress & monitoring |
| `GET` | `/api/v1/matches` | Retrieve saved matches and AI recaps |
| `POST` | `/api/v1/matches` | Save match and trigger OpenRouter AI recap |
| `GET` | `/api/orders/{order_id}` | Lookup order status and record OpenTelemetry signals |

---

## Quick Test via curl

Submit a match to generate an AI recap:

```bash
curl -X POST "http://localhost:8000/api/v1/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Arsenal",
    "away_team": "Chelsea",
    "home_score": 2,
    "away_score": 1,
    "match_date": "Sept 2026",
    "scorers": [
      {"player": "Bukayo Saka", "minute": 12, "team": "Arsenal"},
      {"player": "Cole Palmer", "minute": 45, "team": "Chelsea"},
      {"player": "Declan Rice", "minute": 88, "team": "Arsenal"}
    ],
    "summary_notes": "Late drama with a winning goal from Rice."
  }' | jq
```
Test an order lookup (verifying telemetry metrics & traces):

```
curl -i http://localhost:8000/api/orders/standard-1001
```

Trigger express order failure to test automated incident responder:

```
curl -i http://localhost:8000/api/orders/express-1002
```
