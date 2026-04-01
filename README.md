# 🤖 Multi-Agent Document Processing Pipeline

> **Intelligent document intelligence powered by LangGraph, Gemini Vision, fine-tuned Mistral-7B, and OpenCV.**
> Upload any document image — get back structured JSON in seconds.

[![HuggingFace](https://img.shields.io/badge/Model-Mistral--7B%20Fine--tuned-FFD21E?style=for-the-badge&logo=huggingface)](https://huggingface.co/Isha0408/mistral-json-specialist)
[![Deployment](https://img.shields.io/badge/Cloud%20Version-deployment%20branch-0B0D0E?style=for-the-badge&logo=railway)](../../tree/deployment)

---

## 📌 Branch Overview

| Branch | Description |
|---|---|
| `main` *(this branch)* | 💻 Local version — invoice/product extraction uses **fine-tuned Mistral-7B** via Colab ngrok tunnel. |
| `deployment` | ☁️ Cloud-ready version — all agents use **Gemini Flash**. Deployed on Railway with live URLs. |

---

## 🌐 Live Deployment

The cloud version is live on the `deployment` branch:

| Service | URL |
|---|---|
| 🖥️ Streamlit UI | https://exemplary-learning-production-a01f.up.railway.app |
| ⚡ FastAPI Backend | https://multi-agent-document-pipeline-production.up.railway.app |
| 📖 API Docs | https://multi-agent-document-pipeline-production.up.railway.app/docs |

---

## 🏗️ Architecture

```
User → Streamlit UI → LangGraph Pipeline → PostgreSQL
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   Preprocessor         Extractor          Classifier
   (OpenCV)             (Gemini Vision)    (Gemini Flash)
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
   Invoice/Product      Receipt           Purchase Order
   Specialist           Specialist        Specialist
   (Mistral-7B*)        (Gemini Flash)    (Gemini Flash)
         │
         ▼
   Bank / Resume Specialist → Validator → Structured JSON
```

*\* Fine-tuned Mistral-7B served via Colab ngrok tunnel*

---

## 🤖 Agent Pipeline

| Step | Agent | Technology | Role |
|---|---|---|---|
| 1 | Preprocessor | OpenCV | Grayscale, denoise, CLAHE, deskew |
| 2 | Extractor | Gemini Vision | OCR — extracts raw text |
| 3 | Classifier | Gemini Flash | Identifies document type |
| 4 | Router | LangGraph | Routes to correct specialist |
| 5a | JSON Specialist | **Fine-tuned Mistral-7B** | Invoice / product extraction |
| 5b | Receipt Specialist | Gemini Flash | Receipt extraction |
| 5c | PO Specialist | Gemini Flash | Purchase order extraction |
| 5d | Bank Specialist | Gemini Flash | Bank statement extraction |
| 5e | Resume Specialist | Gemini Flash | Resume / CV extraction |
| 6 | Validator | jsonschema | Schema validation |

---

## 🧠 Fine-tuned Mistral-7B

The `agent_json_specialist.py` uses a **custom fine-tuned Mistral-7B** model trained with **QLoRA + SFT** specifically for structured JSON extraction from invoice and product documents.

- 🤗 Model: [Isha0408/mistral-json-specialist](https://huggingface.co/Isha0408/mistral-json-specialist)
- Training: QLoRA + Supervised Fine-Tuning (SFT)
- Saved at: Google Drive `/content/drive/MyDrive/json-specialist-sft`

### Model Performance
| Metric | Score |
|---|---|
| JSON Valid | 100% |
| Schema Compliant | 100% |
| Zero Extra Text | 100% |
| Safety Compliant | 100% |

### Running Mistral Locally
The model is served via a one-click Google Colab notebook using ngrok tunnel:

1. Open the Colab notebook
2. Run all cells — it starts a FastAPI server
3. Copy the ngrok URL into your `.env` as `MISTRAL_API_URL`
4. Run the Streamlit app locally

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
| LLM (specialist) | Fine-tuned Mistral-7B (QLoRA + SFT) |
| LLM (other agents) | Google Gemini Flash |
| Image Processing | OpenCV |
| REST API | FastAPI + Uvicorn |
| Database | PostgreSQL |
| Authentication | JWT (python-jose) |
| Frontend | Streamlit |
| Model Serving | Colab + ngrok |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11
- PostgreSQL running on port 5434
- Gemini API key
- Mistral model running via Colab notebook (optional — for invoice/product extraction)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/Isha0408/Multi-Agent_Doc_Processing_Pipeline.git
cd Multi-Agent_Doc_Processing_Pipeline

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# Edit .env with your keys

# 5. Run Streamlit
streamlit run src/app.py
```

### .env format
```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_jwt_secret_key
DATABASE_URL=postgresql://postgres:password@127.0.0.1:5434/docpipeline
MISTRAL_API_URL=https://your-ngrok-url/extract  # optional
```

---

## 📁 Project Structure

```
├── src/
│   ├── agent_preprocessor.py
│   ├── agent_extractor.py
│   ├── agent_classifier.py
│   ├── agent_router.py
│   ├── agent_json_specialist.py   ← Uses Mistral-7B
│   ├── agent_receipt_specialist.py
│   ├── agent_po_specialist.py
│   ├── agent_bank_specialist.py
│   ├── agent_resume_specialist.py
│   ├── agent_validator.py
│   ├── gemini_utils.py
│   ├── pipeline.py
│   ├── state.py
│   └── app.py                     ← Streamlit UI
├── api/
│   ├── main.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── documents.py
│   ├── models/
│   │   ├── database.py
│   │   ├── user.py
│   │   └── document.py
│   └── middleware/
│       └── auth.py
├── requirements.txt
└── .env
```

---

## 🔗 Related

- ☁️ Cloud deployment version: [`deployment` branch](../../tree/deployment)
- 🤗 Fine-tuned model: [Isha0408/mistral-json-specialist](https://huggingface.co/Isha0408/mistral-json-specialist)
