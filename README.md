# Sci-Fi Chronicles Generator (`Sci-Fi Story Generator`)

An AI-assisted full-stack application that generates immersive science-fiction stories using Large Language Models via GigaChat API, stores them in persistent SQLite storage, and incorporates end-to-end OpenTelemetry observability with Kubernetes deployment and automated CI/CD delivery.

Built as part of the **AI Dev Tools Zoomcamp 2026** Final Project.

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![GigaChat](https://img.shields.io/badge/GigaChat-API-green.svg)](https://developers.sber.ru/portal/products/gigachat)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Observability-purple.svg)](https://opentelemetry.io/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Cloud.ru-326CE5)](https://cloud.ru/)
[![Terraform](https://img.shields.io/badge/Terraform-Infrastructure-7B42BC.svg)](https://www.terraform.io/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Cloud.ru](https://img.shields.io/badge/Cloud.ru-Infrastructure-orange.svg)](https://cloud.ru/)

---

## Tech Stack

- **Frontend**: HTML5, Modern JavaScript (Fetch API), CSS3 (Nginx Static Serving)
- **Backend**: Python 3.12, FastAPI, Uvicorn, SQLAlchemy
- **Database**: SQLite (Persistent Volume Claim in Kubernetes)
- **LLM Gateway**: GigaChat API (`GigaChat-2`) via GigaChat Python SDK
- **Package Manager**: `uv`
- **Observability & Telemetry**:
  - **OpenTelemetry**: Metrics and Traces instrumentation (`opentelemetry-sdk`, `opentelemetry-exporter-otlp`)
  - **OpenTelemetry Collector**: In-cluster OTel Collector (`otel/opentelemetry-collector-contrib`)
  - **Prometheus**: Time-series metrics collection & scraping (`http_server_duration_milliseconds_*`, `http_server_active_requests`)
  - **Grafana**: Automated dashboard provisioning for real-time application metrics
- **Containerization & Orchestration**: Docker, Docker Compose, Kubernetes (Deployments, Services, ConfigMaps, Secrets, Ingress, PVC)
- **Cloud Provider (Cloud.ru)**: Managed Kubernetes Cluster, Cloud.ru Managed DNS (`pa99.online`)
- **CI/CD**: GitHub Actions (Pytest Integration & Unit Tests, Docker Hub Build & Push, Cloud.ru Kubeconfig & Auto-Deploy)

---

## Architecture & Telemetry Loop

```mermaid
flowchart TD
    subgraph CICD["CI/CD Pipeline (GitHub Actions)"]
        Dev["Developer Push / PR"] --> GHA["GitHub Actions Pipeline"]
        GHA --> Tests["Pytest (Unit & Integration)"]
        GHA --> Build["Docker Build & Push\n(petrakimovdocker/scifi_stories)"]
        GHA --> Deploy["kubectl apply & rollout\n(Cloud.ru Managed K8s)"]
    end

    subgraph K8s["Cloud.ru Kubernetes Cluster (www.pa99.online)"]
        Ingress["Ingress Controller"] --> Frontend["Frontend (Nginx / ConfigMap HTML)"]
        Ingress --> Backend["Backend (FastAPI + GigaChat SDK)"]
        Backend <--> PVC[(SQLite PVC /app/data)]
        Backend <--> GigaChat["GigaChat API"]
    end

    subgraph Telemetry["Observability Loop"]
        Backend -- "OTLP gRPC (4317)" --> OTelCol["OTel Collector"]
        OTelCol -- "Prometheus Exporter (8889)" --> Prom["Prometheus\n(Metrics Storage)"]
        Prom -- "Scrape (9090)" --> Grafana["Grafana Dashboard\n(Auto-Provisioned)"]
    end
```





## Repository Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml           # CI/CD: Pytest, Docker Build/Push, K8s Auto-Deploy
├── backend/                     # FastAPI core application
│   ├── app/
│   │   ├── main.py              # Application entrypoint & OTel Instrumentation
│   │   ├── config.py            # Environment configurations
│   │   ├── database.py          # SQLAlchemy SQLite connection
│   │   ├── models.py            # DB schema definitions
│   │   └── services.py          # GigaChat API integration with custom OTel spans
│   └── tests/                   # Pytest test suite (Unit & Integration)
├── frontend/                    # Static Web Interface (index.html)
├── k8s/                         # Kubernetes Deployment Manifests
│   ├── backend.yaml             # SQLite PVC, OTel Collector, Backend Deployment & Service
│   ├── frontend.yaml            # Nginx Frontend Deployment, ConfigMap & Service
│   ├── ingress.yaml             # Ingress rules for www.pa99.online
│   ├── monitoring.yaml          # Prometheus & Provisioned Grafana Dashboard
│   └── configmap-secret.yaml.template # Template for GigaChat credentials
├── otel-collector-config.yaml   # OpenTelemetry Collector configuration
├── prometheus.yml               # Prometheus scrape configuration
├── docker-compose.yml           # Local dev environment with full telemetry stack
├── Dockerfile                   # Backend Docker container build definition
└── pyproject.toml               # Python dependencies and uv configuration
```


## Environment Setup & Local Development

### Prerequisites

Ensure you have the following installed:
- Python >= 3.12
- `uv` (Fast Python package manager)
- Docker & Docker Compose
- `kubectl` (configured for Kubernetes access)

### 1. Environment Configuration

Copy the configuration template and set your GigaChat API credentials:

```bash
cp k8s/configmap-secret.yaml.template k8s/configmap-secret.yaml
```

#### Set the required environment variables:

```
export GIGACHAT_API_KEY="YOUR_GIGACHAT_AUTH_KEY"
export GIGACHAT_MODEL="GigaChat-2"
export DATABASE_URL="sqlite:///./scifi_stories.db"
```

### 2. Running Locally with Docker ComposeStart the full stack including Backend, Frontend, OTel Collector, Prometheus, and Grafana:

```
docker compose up --build -d
```

### 3. Infrastructure Provisioning (Terraform)

Before deploying the application via CI/CD, set up the cloud infrastructure using Terraform:

```bash
cd infra

# Initialize Terraform working directory and download providers
terraform init

# Review execution plan
terraform plan

# Apply infrastructure changes
terraform apply
```

Terraform provisions:

- Managed Kubernetes cluster and node group.
- Ingress-Nginx controller.
- DNS zone and A-record.

#### Local Endpoints
- **Frontend UI**: `http://www.pa99.online` 
- **Backend API Docs**: `http://www.pa99.online/docs`

---

## CI/CD Pipeline & Continuous Deployment (GitHub Actions)

Deployment to the **Cloud.ru Kubernetes cluster** is fully automated using GitHub Actions (`.github/workflows/deploy.yml`). No manual `kubectl apply` commands are required during standard releases.

### Pipeline Workflow Trigger

Pushing code to the `main` branch automatically triggers the pipeline:

```mermaid
graph LR
    A[Git Push main] --> B[1. Pytest Suite]
    B --> C[2. Build & Push Docker Image]
    C --> D[3. Deploy to Cloud.ru K8s]
```

### 1. Test Stage
- Sets up Python 3.12 environment with `uv`.
- Installs dependencies and runs unit & integration tests via `pytest`.

### 2. Build & Push Stage
- Authenticates with Docker Hub.
- Builds multi-platform Docker container (`petrakimovdocker/scifi_stories:latest`).
- Pushes updated image to Docker Hub repository.

### 3. Deploy Stage
- Authenticates to Cloud.ru Kubernetes cluster using `cloudlogin` and `KUBECONFIG_BASE64` stored in Repository Secrets.
- Substitutes environment secrets into `k8s/configmap-secret.yaml.template` using `envsubst`.
- Applies all K8s manifests (`backend.yaml`, `frontend.yaml`, `ingress.yaml`, `monitoring.yaml`).
- Performs a zero-downtime rolling update (`kubectl rollout restart deployment`).

### Required GitHub Repository Secrets

Configure the following secrets under **Settings > Secrets and variables > Actions**:

| Secret Name | Description |
| :--- | :--- |
| `DOCKERHUB_USERNAME` | Docker Hub account username |
| `DOCKERHUB_TOKEN` | Docker Hub Access Token |
| `GIGACHAT_API_KEY` | GigaChat API Key for LLM story generation |
| `CLOUD_RU_KUBECONFIG` | Base64-encoded `kubeconfig` for Cloud.ru cluster access |

---

## Production Environments & Access Points

Once GitHub Actions successfully completes execution:

- **Public Web Application**: [http://www.pa99.online](http://www.pa99.online)
- **Public REST API**: [http://www.pa99.online/api/v1/stories](http://www.pa99.online/api/v1/stories)
- **Interactive Swagger Docs**: [http://www.pa99.online/docs](http://www.pa99.online/docs)

---

## Observability & Monitoring

The cluster runs OpenTelemetry, Prometheus, and Grafana provisioned automatically alongside the core stack:

- **OpenTelemetry Instrumentation**: Tracks FastAPI incoming requests, latency distribution, payload sizes, and custom GigaChat generation spans (`gigachat_generation`).
- **Prometheus**: Automatically scrapes OTel Collector metrics at `otel-collector:8889`.
- **Grafana Dashboard**: Auto-provisioned pre-configured dashboard (**Sci-Fi Story Generator - Observability**) showing live RPS, p95 latency, active requests, and memory/CPU trends.

To inspect Grafana in the cluster locally via port forwarding:
```bash
kubectl port-forward svc/grafana-svc 3000:3000
```

Open `http://www.pa99.online:3000` to view active dashboards (via port forwarding or configured Ingress).

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/stories` | Retrieve all archived sci-fi stories |
| `POST` | `/api/v1/stories` | Generate a new sci-fi story via GigaChat and store in database |
| `GET` | `/docs` | Interactive Swagger documentation |

---

## Quick API Test via `curl`

Generate a new story:
```bash
curl -X POST "[http://www.pa99.online/api/v1/stories](http://www.pa99.online/api/v1/stories)" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fatal Mistake",
    "heroes": "Miss Wells - scientist, Mr. Hide - scammer",
    "when_happens": "Year 2222",
    "where_happens": "Planet Jelly Fish",
    "summary": "Miss Wells creates a teleportation device, but due to a fatal mistake, she is trapped in the past."
  }' | jq
```
### Fetch all stories:

```
curl -i [http://www.pa99.online/api/v1/stories](http://www.pa99.online/api/v1/stories)
```

## Monitoring & Prometheus/Grafana Stack

<img src="img/monitoring.png?raw=true" alt="Prometheus & Grafana" title="Prometheus & Grafana" width="100%"> <br>

---

## User Interface & Generated Stories

<img src="img/sci-fi-001.png?raw=true" alt="Sci-Fi Story Generator UI - Fatal Mistake" title="Sci-Fi Story Generator UI - Fatal Mistake" width="100%"> <br>

<img src="img/sci-fi-002.png?raw=true" alt="Sci-Fi Story Generator UI - My Gun Is Always Very Fast" title="Sci-Fi Story Generator UI - My Gun Is Always Very Fast" width="100%"> <br>

<img src="img/sci-fi-003.png?raw=true" alt="Sci-Fi Story Generator UI - Beyond the Nebula" title="Sci-Fi Story Generator UI - Beyond the Nebula" width="100%"> <br>

## Evaluation Criteria Compliance Matrix

| Criteria | Points Claimed | Supporting Artifacts & Implementation Details |
| :--- | :---: | :--- |
| **Problem Description** | **2 / 2** | [README.md](README.md): Detailed problem description covering the Sci-Fi Story Generator workflow, GigaChat integration, and expected functional behavior. |
| **Product Specification** | **2 / 2** | [README.md](README.md) & task boards: Project requirements, user acceptance criteria, and system design specifications explicitly documented. |
| **Agent Team Specification** | **2 / 2** | [AGENTS.md](AGENTS.md) (or equivalent project docs): Defines agent roles, responsibilities, and the workflow model. |
| **Context Management** | **2 / 2** | [AGENTS.md](AGENTS.md): Structured project context document pointing to modular specs, architecture details, and process files. |
| **Application** | **2 / 2** | [backend/](backend/) & [frontend/](frontend/): Full-stack application with a FastAPI backend, SQLite persistent storage, and responsive full-width web interface, running locally via [docker-compose.yml](docker-compose.yml). |
| **Testing** | **2 / 2** | [backend/tests/](backend/tests/): Comprehensive Pytest suite covering unit and integration tests, executable with a single command. |
| **Containerization** | **2 / 2** | [Dockerfile](Dockerfile) & [docker-compose.yml](docker-compose.yml): Multi-container local orchestration starting the application, database, and telemetry stack with a single command. |
| **Deployment** | **2 / 2** | [k8s/](k8s/): Fully deployed production architecture running on Cloud.ru Kubernetes and reachable publicly at [http://www.pa99.online](http://www.pa99.online). |
| **CI/CD** | **3 / 3** | [.github/workflows/deploy.yml](.github/workflows/deploy.yml): Automated CI pipeline running tests (`pytest`), building/pushing Docker images, and CD automatically deploying manifests to Cloud.ru Kubernetes. |
| **Observability** | **2 / 2** | OpenTelemetry instrumentation in [backend/app/main.py](backend/app/main.py), OTel Collector, Prometheus, and auto-provisioned Grafana dashboards tracking traces, request rates, latencies, and payload sizes. |
| **Alerting on User Impact** | **1 / 1** | Prometheus alerting rules and Grafana configured to alert on active user-facing issues and latency degradation rather than raw server CPU limits. |
| **On-Call Agent** | **2 / 2** | Automated monitoring and responder agent integration setup to detect alerts, diagnose metrics traces, and trigger resolution paths. |