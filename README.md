# 🤖 Multi-Agent Document Processing Pipeline

> **Intelligent document intelligence powered by LangGraph, Gemini Vision, and OpenCV.**
> Upload any document image — get back structured JSON in seconds.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://exemplary-learning-production-a01f.up.railway.app)
[![API Docs](https://img.shields.io/badge/API%20Docs-FastAPI-009688?style=for-the-badge&logo=fastapi)](https://multi-agent-document-pipeline-production.up.railway.app/docs)
[![Railway](https://img.shields.io/badge/Deployed%20on-Railway-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app)

---

## 🌐 Live Links

| Service | URL |
|---|---|
| 🖥️ Streamlit UI | https://exemplary-learning-production-a01f.up.railway.app |
| ⚡ FastAPI Backend | https://multi-agent-document-pipeline-production.up.railway.app |
| 📖 API Docs (Swagger) | https://multi-agent-document-pipeline-production.up.railway.app/docs |

---

## 📌 Branch Overview

| Branch | Description |
|---|---|
| `deployment` *(this branch)* | ☁️ Cloud-ready version — all agents use **Gemini Flash**. Deployed on Railway. |
| `main` | 💻 Local version — invoice/product extraction uses **fine-tuned Mistral-7B** via Colab ngrok tunnel. |

---

## 🏗️ Architecture

```
User → Streamlit UI → FastAPI REST API → LangGraph Pipeline → PostgreSQL
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
             Preprocessor              Extractor                  Classifier
             (OpenCV)                  (Gemini Vision)            (Gemini Flash)
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
             Invoice/Product           Receipt                    Purchase Order
             Specialist                Specialist                 Specialist
             (Gemini Flash)            (Gemini Flash)             (Gemini Flash)
                    │
                    ▼
             Bank / Resume Specialist → Validator → Structured JSON → DB
```

---

## 🤖 Agent Pipeline

| Step | Agent | Technology | Role |
|---|---|---|---|
| 1 | Preprocessor | OpenCV | Grayscale, denoise, CLAHE, deskew |
| 2 | Extractor | Gemini Vision | OCR — extracts raw text |
| 3 | Classifier | Gemini Flash | Identifies document type |
| 4 | Router | LangGraph | Routes to correct specialist |
| 5a | JSON Specialist | Gemini Flash | Invoice / product extraction |
| 5b | Receipt Specialist | Gemini Flash | Receipt extraction |
| 5c | PO Specialist | Gemini Flash | Purchase order extraction |
| 5d | Bank Specialist | Gemini Flash | Bank statement extraction |
| 5e | Resume Specialist | Gemini Flash | Resume / CV extraction |
| 6 | Validator | jsonschema | Schema validation |

---

## 📄 Supported Document Types

- 🧾 **Invoice** — vendor, items, totals, tax
- 🛒 **Receipt** — store, items, total, date
- 📦 **Purchase Order** — PO number, vendor, buyer, items
- 🏦 **Bank Statement** — account info, all transactions
- 📄 **Resume / CV** — name, skills, experience, education
- 🏷️ **Product Listing** — name, price, category, attributes

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph |
| LLM | Google Gemini 2.0 Flash |
| Image Processing | OpenCV |
| REST API | FastAPI + Uvicorn |
| Database | PostgreSQL |
| Authentication | JWT (python-jose) |
| Frontend | Streamlit |
| Containerization | Docker |
| Deployment | Railway |

---

## 🚀 Running Locally with Docker

### Prerequisites
- Docker Desktop installed
- Gemini API key

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/ishaw015/Multi-Agent-Document-Pipeline.git
cd Multi-Agent_Doc_Processing_Pipeline
git checkout deployment

# 2. Create .env file
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and SECRET_KEY

# 3. Start everything
docker compose up --build
```

- API: http://localhost:8080
- API Docs: http://localhost:8080/docs

### .env format
```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_jwt_secret_key
DATABASE_URL=postgresql://postgres:password@db:5432/docpipeline
```

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login and get JWT token |
| GET | `/auth/me` | Get current user info |

### Documents
| Method | Endpoint | Description |
|---|---|---|
| POST | `/documents/process` | Upload and process a document |
| GET | `/documents/` | List all processed documents |
| GET | `/documents/{id}` | Get document by ID |
| DELETE | `/documents/{id}` | Delete document |
| GET | `/documents/stats/summary` | Get processing statistics |

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | API health check |

---

## 📊 Example Output

**Input:** Invoice image

**Output:**
```json
{
  "document_type": "invoice",
  "validation_status": "Valid — Schema Compliant",
  "validated_json": {
    "invoice_number": "INV-001",
    "date": "19-03-2026",
    "vendor": "Stanford Plumbing & Heating",
    "total": 2844.80,
    "currency": "USD",
    "items": [
      {
        "description": "Kitchen sink installation",
        "quantity": 3,
        "unit_price": 50.00,
        "total": 150.00
      }
    ]
  }
}
```

---

## 🔗 Related

- 💻 Local version with Mistral: [`main` branch](../../tree/main)

---

## 📁 Project Structure

```
├── src/
│   ├── agent_preprocessor.py
│   ├── agent_extractor.py
│   ├── agent_classifier.py
│   ├── agent_router.py
│   ├── agent_json_specialist.py
│   ├── agent_receipt_specialist.py
│   ├── agent_po_specialist.py
│   ├── agent_bank_specialist.py
│   ├── agent_resume_specialist.py
│   ├── agent_validator.py
│   ├── gemini_utils.py
│   ├── pipeline.py
│   ├── state.py
│   └── app.py                  ← Streamlit UI
├── api/
│   ├── main.py                 ← FastAPI app
│   ├── routes/
│   │   ├── auth.py
│   │   └── documents.py
│   ├── models/
│   │   ├── database.py
│   │   ├── user.py
│   │   └── document.py
│   └── middleware/
│       └── auth.py
├── Dockerfile                  ← API image
├── Dockerfile.streamlit        ← Streamlit image
├── docker-compose.yml          ← Local dev
├── requirements.txt
└── .env
```
