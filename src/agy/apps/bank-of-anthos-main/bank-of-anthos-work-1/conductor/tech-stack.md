# Technology Stack: Bank of Anthos

This document outlines the polyglot microservice technology stack utilized by Bank of Anthos.

## 1. Programming Languages & Runtimes
- **Java 17:** Primary language for backend financial transactional logic. Run with Spring Boot.
- **Python >= 3.14:** Primary language for user-facing frontends, auxiliary services, and background simulators. Run with Flask and Gunicorn.

## 2. Microservices, Frameworks & Libraries

### Java Services (`src/ledger/`)
- **Ledger Writer, Balance Reader, Transaction History:**
  - **Framework:** Spring Boot 3.5.15
  - **Cloud Integration:** Spring Cloud GCP 5.13.11 / Spring Cloud Dependencies 2025.1.2
  - **Telemetry/Tracing:** OpenTelemetry / Micrometer 1.17.0
  - **JPA & Persistence:** Spring Boot Starter Data JPA (Hibernate)

### Python Services (`src/frontend/`, `src/accounts/`)
- **Frontend, User Service, Contacts, Load Generator:**
  - **Framework:** Flask >= 3.1.2
  - **Production WSGI Server:** Gunicorn >= 23.0.0
  - **Dependency Management:** UV (`pyproject.toml` and `uv.lock`)
  - **HTTP Request Handling:** `requests` and `urllib3`
  - **Security:** `pyjwt` and `cryptography`
  - **Tracing:** OpenTelemetry SDK, OpenTelemetry Flask/Jinja2/Requests Instrumentations

## 3. Data Storage & Persistence
- **PostgreSQL:**
  - `ledger-db`: For transaction history and user balance records.
  - `accounts-db`: For user accounts, recipient contact lists, and profile metadata.

## 4. Deployment & Orchestration
- **Kubernetes:** Declared via standard YAML manifests in `/kubernetes-manifests` and customized per-environment using Kustomize overlays in each service's directory.
- **Skaffold:** Orchestrates multi-service container builds and hot-reloads during local or cluster development.
- **Cloud Build:** Handles continuous integration (CI) and build automation.
