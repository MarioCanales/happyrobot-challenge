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
│   ├── populate_metrics.py  # Script to populate mock data in metrics
│   ├── Dockerfile  
│   └── requirements.txt
├── dashboard/              # Sales Dashboard
│   ├── app.py              # Dashboard UI Logic
│   ├── requirements.txt
│   └── Dockerfile  
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



### Database Seeding
Initialize the SQLite database with some mock data.
```
# Run from the project root
python backend/seed_loads.py
python backend/populate_metrics.py
```

## 🏃‍♂️ Running the Services
You will need two terminal windows running simultaneously. You don't need to create .env since the environment variable fallbacks worksin local.

Terminal 1: Start the API
```
source venv/bin/activate
uvicorn backend.app.main:app --reload
```

Do a GET to the health Check endpoint to validate it worked: `http://localhost:8000/health`

Terminal 2: Start the Dashboard

```
source venv/bin/activate
streamlit run dashboard/app.py
```
Dashboard UI: `http://localhost:8501/`

Your service is up and running.

## 🧠 Key Features & Logic

This POC automates inbound carrier calls using an AI agent connected to a FastAPI backend and a Streamlit dashboard.

---

### 🔐 Secure API (FastAPI)

All operational endpoints require an API Key header  
(`X-API-Key` header).

---

### 🛂 Carrier Verification

**POST /verify-carrier**  
Validates a carrier's MC number using the FMCSA SAFER API and ensures they are active before negotiation.

---

### 📦 Load Search

**GET /loads** — returns only loads with `status="available"`  
**GET /loads/all** — returns *all* loads (used by the dashboard)

Supports filtering by origin/destination.

---

### 🤝 Automated Negotiation Engine

**POST /negotiate**

Simple POC with following rules:
- Accept if offer ≥ loadboard rate  
- Reject if offer < 85% of rate  
- Otherwise counter with a midpoint amount  
- Auto-accept when close to target  
- When accepted, load becomes `"booked"`

---

###  ☎️ Call Summary Logging

**POST /call-summary**
Used to power analytics metrics. Endpoint to be called after a call ends.

---

### 📊 Analytics Dashboard (Streamlit)
Consumes `/logs` and `/loads/all`.

Features:
- KPIs: calls, bookings, failures, revenue  
- Outcome pie chart  
- Sentiment bar chart  
- Load table with toggle: **Available** / **Unavailable**  
- Recent call activity table  

---

### 🔗 FMCSA Integration
Carrier MC numbers are validated through the FMCSA SAFER API to ensure only compliant carriers enter the negotiation workflow.

## 🧠 Testing & Deployment
For finging MC numbers and test FMCSA API you can search here: https://safer.fmcsa.dot.gov/keywordx.asp?searchstring=%2ATRANSPORT%2A&SEARCHTYPE=

For deploying firs create a .env file in the backend/ directory with the following credentials:

```
# backend/.env
SERVICE_API_KEY=
FMCSA_API_KEY
FMCSA_BASE_URL=
```
Then go to the cloud of your choice and configure the entry point to the backend dockerfile. 
After deploying backend, fetch the URL and Create a .env file in the dashboard/ directory with the following credentials
```
# dashboard/.env
BACKEND_URL=
SERVICE_API_KEY=
```
Then go again to the cloud and configure the entry point to the dashboard dockerfile. You can access now the dashboard through the link provided by the cloud

_DEVELOPED BY MARIO CANALES TORRES_