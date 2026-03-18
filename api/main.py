from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from api.models.database import engine, Base
from api.models.user import User
from api.models.document import Document
from api.routes.auth import router as auth_router
from api.routes.documents import router as documents_router

# ── create tables on startup ─────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up — creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables ready ✓")
    yield
    print("Shutting down...")

# ── app ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Document Processing Pipeline API",
    description="""
    Multi-Agent Document Processing System

    ## Features
    - **Upload** any document image (invoice, receipt, PO, bank statement, resume)
    - **Process** through 5 AI agents automatically
    - **Store** results in PostgreSQL database
    - **Retrieve** processed documents with full JSON output
    - **Authenticate** with JWT tokens

    ## Supported Document Types
    - Invoice
    - Receipt
    - Purchase Order
    - Bank Statement
    - Resume / CV
    - Product Listing
    """,
    version="1.0.0",
    lifespan=lifespan
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(documents_router)

# ── health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Document Processing Pipeline API",
        "docs": "/docs",
        "health": "/health"
    }