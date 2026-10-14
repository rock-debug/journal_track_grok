# Journal & Patent Research Tracker 🔬📜🤖

A cloud-native, AI-powered research management platform built for researchers to track academic journal papers, patents, research notes, and deadlines. Powered by **Flask**, **PostgreSQL**, **Groq SDK (Llama 3.3)**, **TF-IDF RAG Q&A**, **Crossref API Integration**, **Docker Compose**, **Kubernetes (EKS)**, and **Terraform**.

---

## 🚀 Key Features

### 👥 Multi-Role User Management
- **Guest:** Registration and login authentication.
- **Researcher:** Full CRUD access to personal paper library, patents, notes, reminders, AI summarizer, citation generator, RAG QA, recommendations, and CSV exports.
- **Admin:** System user dashboard to view registered users, promote/demote roles, and manage user accounts.

### 📚 Research Paper & Patent Tracking
- **Paper CRUD:** Title, authors, abstract, journal, publication year, DOI, URL, keywords, and reading status (`Unread`, `Reading`, `Completed`).
- **Patent CRUD:** Title, patent number, description, filing date, publication date, and URL.
- **Strict Data Ownership:** Every paper, patent, note, and reminder is scoped to `current_user.id`. Attempts to access another user's resources return `403 Forbidden`.
- **DOI Normalization & Deduplication:** Normalizes DOIs (`10.xxxx/xxxxx`) and prevents duplicate entries per user.

### 🌐 Crossref API & DOI Integration
- Live search over millions of academic papers via Crossref REST API.
- Direct **"Save to Library"** button to import papers straight into personal library.

### 🤖 Groq AI & TF-IDF RAG Features
1. **Paper Summarization:** Formats paper metadata into structured markdown summaries (Research Problem, Methodology, Key Findings, Limitations, Summary) via Groq **Llama 3.3-70b-versatile**.
2. **Citation Generation:** Instant APA, MLA, and IEEE citation formatting supporting DOI content negotiation and fallback formatting.
3. **TF-IDF RAG Question Answering:** Vectorizes saved research papers, computes cosine similarity with user queries, builds context, and queries Groq Llama 3.3 while citing exact source papers.
4. **Personalized Recommendations:** Extracts key research themes via TF-IDF across saved papers and recommends related external literature from Crossref.

### 📊 Data Export & Monitoring
- Dynamic CSV exports for Research Papers and Patents (`/export/papers`, `/export/patents`).
- `/health` endpoint returning JSON status (`healthy`, database connection verification, Groq status).
- Prometheus metric exporter integration (`/metrics`).

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3, Bootstrap 5, Jinja2 Templates, FontAwesome Icons |
| **Backend** | Python 3.11+, Flask 3.1, Flask-Login, Flask-Migrate, SQLAlchemy ORM |
| **Database** | PostgreSQL 16 / SQLite (Local Dev fallback) |
| **AI / RAG** | Groq SDK (`llama-3.3-70b-versatile`), Scikit-Learn TF-IDF, Cosine Similarity |
| **External APIs** | Crossref REST API, DOI.org Content Negotiation |
| **Infrastructure** | Docker, Docker Compose, Kubernetes (kubectl), AWS EKS, AWS RDS, AWS VPC |
| **DevOps & IaC** | Terraform HCL, Jenkins Pipeline, Prometheus, Grafana |

---

## 📂 Project Structure

```
journal_track_grok-main/
│
├── app/
│   ├── __init__.py          # Flask App Factory & Blueprint registration
│   ├── config.py            # Development, Production, & Testing configurations
│   ├── extensions.py        # SQLAlchemy, Flask-Login, Migrate, PrometheusMetrics
│   │
│   ├── models/
│   │   ├── __init__.py      # Package export
│   │   ├── user.py          # User entity & Werkzeug password hashing
│   │   ├── paper.py         # ResearchPaper entity
│   │   ├── patent.py        # Patent entity
│   │   ├── note.py          # Note entity with foreign keys
│   │   └── reminder.py      # Reminder entity
│   │
│   ├── routes/
│   │   ├── __init__.py      # Blueprint exports
│   │   ├── auth.py          # /register, /login, /logout
│   │   ├── dashboard.py     # /dashboard overview
│   │   ├── papers.py        # /papers CRUD
│   │   ├── patents.py       # /patents CRUD
│   │   ├── notes.py         # /notes CRUD
│   │   ├── reminders.py     # /reminders CRUD
│   │   ├── ai.py            # /ai, /ai/summarize, /ai/citation, /ai/ask, /ai/recommendations
│   │   ├── search.py        # /search/crossref, /search/save_paper
│   │   ├── export.py        # /export/papers, /export/patents
│   │   └── admin.py         # /admin user management
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crossref_service.py      # Crossref API integration
│   │   ├── doi_service.py           # DOI normalization & validation
│   │   ├── groq_service.py          # Groq SDK & Llama 3.3 AI interface
│   │   ├── rag_service.py           # TF-IDF vectorization & cosine RAG Q&A
│   │   ├── citation_service.py      # APA/MLA/IEEE citation generator
│   │   └── recommendation_service.py # TF-IDF recommendation engine
│   │
│   ├── templates/          # Bootstrap 5 Jinja2 Templates
│   │   ├── base.html
│   │   ├── 404.html, 403.html, 500.html
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── papers/
│   │   ├── patents/
│   │   ├── notes/
│   │   ├── reminders/
│   │   ├── ai/
│   │   ├── search/
│   │   └── admin/
│   │
│   └── static/
│       ├── css/style.css
│       └── js/main.js
│
├── scripts/
│   └── seed.py             # Database seed script for admin & researcher demo data
│
├── tests/                  # Pytest test suite (21 automated test cases)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_papers.py
│   ├── test_patents.py
│   ├── test_notes.py
│   ├── test_reminders.py
│   ├── test_ai.py
│   ├── test_search.py
│   ├── test_export.py
│   └── test_health.py
│
├── k8s/                    # Kubernetes Production Manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml     # 2 Replicas with Readiness & Liveness Probes
│   ├── service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
│
├── terraform/              # Infrastructure as Code for AWS Cloud
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── vpc.tf              # Multi-AZ VPC with public/private subnets
│   ├── eks.tf              # AWS EKS Cluster & Node Groups
│   ├── rds.tf              # AWS RDS PostgreSQL database
│   ├── security_groups.tf
│   └── terraform.tfvars.example
│
├── main.py                 # Root Application Entrypoint
├── Dockerfile              # Production Multi-Stage Container build
├── docker-compose.yml      # Local Compose file (Web + PostgreSQL + Prometheus + Grafana)
├── Jenkinsfile             # End-to-end CI/CD Pipeline
├── prometheus.yml          # Prometheus Scraping Config
├── grafana/
│   └── dashboard.json      # Grafana Dashboard configuration
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚡ Environment Variables

Copy `.env.example` to `.env` and populate your credentials:

```bash
FLASK_ENV=development
SECRET_KEY=a-very-secret-key-change-in-production
DATABASE_URL=postgresql://tracker_user:tracker_password@postgres:5432/research_tracker_db
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
CROSSREF_EMAIL=researcher@example.com
```

---

## 💻 Local Quickstart & Development

### 1. Python Virtual Environment Setup
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Seed Demo Data
```bash
python scripts/seed.py
```
This initializes demo credentials:
- **Admin User:** `admin` / `admin123`
- **Researcher User:** `researcher` / `researcher123`

### 3. Run Development Server
```bash
python main.py
```
Access the web app at `http://localhost:5000`.

---

## 🧪 Running Automated Tests

Run the complete 21-test Pytest suite:
```bash
python -m pytest
```

---

## 🐳 Docker & Docker Compose Setup

Run the full platform stack locally using Docker Compose (Flask Web + PostgreSQL + Prometheus + Grafana):

```bash
docker compose up --build -d
```

### Access Services:
- **Web App:** `http://localhost:5000`
- **Health Check:** `http://localhost:5000/health`
- **Prometheus Metrics:** `http://localhost:5000/metrics`
- **Prometheus UI:** `http://localhost:9090`
- **Grafana Dashboard:** `http://localhost:3000` (User: `admin` / Password: `admin`)

Stop containers:
```bash
docker compose down -v
```

---

## ☸️ Kubernetes Deployment (EKS)

Apply Kubernetes manifests:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

Verify deployment rollout:
```bash
kubectl get pods -n research-tracker
kubectl rollout status deployment/tracker-web -n research-tracker
```

---

## 🏗️ Terraform Infrastructure (AWS Cloud)

Deploy AWS VPC, EKS Cluster, and RDS PostgreSQL:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Update terraform.tfvars with db_password

terraform init
terraform plan
terraform apply
```

Outputs will display EKS Cluster Name and RDS Endpoint.

---

## 🔄 Jenkins CI/CD Pipeline

The included `Jenkinsfile` executes:
1. **Checkout:** Clones repository.
2. **Install:** Installs dependencies in virtual environment.
3. **Lint:** Checks code quality with `flake8`.
4. **Test:** Runs unit/integration tests with `pytest`.
5. **Build & Tag:** Builds production Docker image tagged with build number.
6. **Push:** Pushes image to Docker Hub / Container Registry.
7. **Deploy:** Performs zero-downtime rolling deployment to AWS EKS cluster via `kubectl`.

---

## 🔒 Security & Data Isolation

- Passwords are strictly hashed with **Werkzeug** PBKDF2:SHA256 password hashing algorithm.
- Every database query for papers, patents, notes, and reminders is scoped to `user_id == current_user.id`.
- Admin routes (`/admin`) enforce `current_user.role == 'admin'`, returning `403 Forbidden` for unauthorized requests.
- Environment variables isolate API keys (`GROQ_API_KEY`, `SECRET_KEY`, `DATABASE_URL`). No secrets are hardcoded in source control.

---

## 📝 License

This project is licensed under the MIT License.
