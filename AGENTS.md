# Project Context & Agent Team Specification

This document defines the agent team, modular architecture documentation pointers, and collaborative workflow guidelines for the **Sci-Fi Chronicles Generator** project (`AI Dev Tools Zoomcamp 2026`).

---

## 1. Modular Documentation Index

To maintain clean context and clear separation of concerns across the project repository, refer to the following auxiliary specifications:
- **[README.md](README.md)**: Main project overview, architecture diagram, tech stack, local Quickstart guide, and CI/CD deployment instructions.
- **[k8s/](k8s/)**: Production Kubernetes manifests, Ingress configuration, and auto-provisioned Prometheus/Grafana monitoring stack.
- **[tf/](tf/)**: Terraform infrastructure provisioning scripts for Cloud.ru Managed Kubernetes clusters and network objects.
- **[backend/tests/](backend/tests/)**: Automated unit and integration test suite (`pytest`).

---

## 2. Agent Team Specification & Responsibilities

The development, deployment, and operation of this project are managed through a specialized multi-agent workflow:

| Agent Role | Core Responsibilities & Workflow Process |
| :--- | :--- |
| **Architect Agent** | • Designs the system topology (FastAPI backend, SQLite persistence, GigaChat LLM integration, and OpenTelemetry instrumentation).<br>• Defines cloud infrastructure requirements using Terraform (`tf/`). |
| **Developer / Coder Agent** | • Implements business logic, API endpoints (`/api/v1/stories`), and frontend UI components.<br>• Manages Python packages using `uv` and maintains clean dependency boundaries in `pyproject.toml`. |
| **QA & Testing Agent** | • Authors and executes unit and integration tests under `backend/tests/` using `pytest`.<br>• Enforces test coverage and validates API schemas via Pydantic models. |
| **DevOps & CI/CD Agent** | • Manages GitHub Actions workflows (`.github/workflows/deploy.yml`) for automated linting, test execution, Docker image building, and rolling updates to Cloud.ru Kubernetes.<br>• Configures Ingress routing and TLS/DNS records. |
| **SRE & On-Call Agent** | • Monitors application health and performance metrics via Prometheus and Grafana dashboards.<br>• Responds to user impact alerts (e.g., latency degradation or GigaChat upstream timeouts) and triggers automated recovery paths. |

---

## 3. Collaborative Process & Workflow

1. **Specification First**: Before code changes are introduced, user stories and requirements are outlined and mapped against the grading criteria matrix.
2. **Automated Validation**: Every pull request triggers the CI pipeline to run linters (`ruff`, `mypy`) and the `pytest` suite.
3. **Continuous Delivery**: Upon successful test verification, container images are pushed to Docker Hub, and manifests are applied to the Cloud.ru production cluster via zero-downtime rolling deployment.