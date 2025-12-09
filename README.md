# Inbound Carrier Sales Automation (POC)

This project is a Proof of Concept (POC) designed to automate inbound carrier calls for **Acme Logistics**. It utilizes an AI-driven approach to authenticate carriers, match them with viable loads, and negotiate pricing automatically.

## 📋 Overview

The solution is architected as a **monorepo** containing two distinct microservices:

1.  **Backend API (FastAPI):** The core "brain" that handles carrier verification (FMCSA), load searching, and negotiation logic.
2.  **Analytics Dashboard (Streamlit):** A visualization layer for sales managers to monitor call outcomes, revenue, and sentiment in real-time.

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **API Framework:** FastAPI
* **Database:** SQLite (SQLAlchemy ORM)
* **Dashboard:** Streamlit + Plotly
* **External Integrations:** FMCSA API (Department of Transportation)

## 🚀 Project Structure

```text
happyrobot-challenge/
├── backend/                # Main API
│   ├── app/
│   │   ├── main.py         # API Entry point & Routes
│   │   ├── models.py       # Database Tables (Loads, CallLogs)
│   │   ├── auth.py         # API Key Security
│   │   └── fmcsa_service.py # Carrier Verification Logic
│   ├── seed_loads.py       # Script to populate mock data
│   └── requirements.txt
├── dashboard/              # Sales Dashboard
│   ├── app.py              # Dashboard UI Logic
│   └── requirements.txt
└── README.md
```

## ⚙️ Setup & Installation
Ensure you have python and a virtual environment.
```
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
Install requirements for both services:
```
pip install -r backend/requirements.txt
pip install -r dashboard/requirements.txt
```

### Environment Configuration
Create a .env file in the backend/ directory with the following credentials:

```
# backend/.env
SERVICE_API_KEY=
FMCSA_API_KEY
FMCSA_BASE_URL=
```
Create a .env file in the dashboard/ directory:
```
# dashboard/.env
BACKEND_URL=
SERVICE_API_KEY=
```

### Database Seeding
Initialize the SQLite database with the "Context" genai generated load data:

```
# Run from the project root
python backend/seed_loads.py
```

## 🏃‍♂️ Running the Services
You will need two terminal windows running simultaneously.

Terminal 1: Start the API

```
source venv/bin/activate
uvicorn backend.app.main:app --reload
```

Health Check: `http://127.0.0.1:8000/health`

Terminal 2: Start the Dashboard

```
source venv/bin/activate
streamlit run dashboard/app.py
```

Dashboard UI: `http://localhost:8501`

## 🧠 Key Features & Logic [PENDING]
TO ADD
## 🧠 Testing & Deployment [PENDING]
TO ADD