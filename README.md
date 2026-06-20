# SmartHR AI – Automation Platform

## Project Objective
An AI-powered HRMS platform to automate employee management, payroll processing, and workforce analytics. The platform utilizes local machine learning models and an isolated LLM service to provide predictive insights while guaranteeing 100% data privacy.

---

## Tech Stack

* **Frontend:** React.js (Served on Port `3000`)
* **Backend:** FastAPI (Python) (Served on Port `8000`)
* **Database:** SQLite (Local Dev) / PostgreSQL (Production ready)
* **AI/ML:** Scikit-Learn (Attrition Pipeline), RandomForest (Leave Anomaly Monitoring), Ollama, LangChain (`OllamaLLM`)

---

## 🏗️ System Architecture & Service Mesh

The platform is fully containerized within an isolated Docker virtual network (`smarthr-mesh`). This eliminates host-level dependencies, UFW firewall blocks, and port conflicts by routing all internal traffic natively.

```text
       [ React UI Canvas Command Center ]
                       │
                       ▼ (CORS Approved / Preflight Interceptor)
         [ FastAPI Core Backend Engine ]
             │                       │
     (SQLAlchemy ORM)         (Internal Bridge Mesh)
             ▼                       ▼
     [ Local Database ]      [ Ollama Core Container ]
                                     │
                                     ▼ (Resource Clamped)
                             [ llama3.2:1b / llama3 ]
