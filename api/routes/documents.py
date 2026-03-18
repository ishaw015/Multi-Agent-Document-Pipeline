from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import shutil
import os

from api.models.database import get_db
from api.models.document import Document
from api.middleware.auth import get_current_user
from api.models.user import User

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from pipeline import run_pipeline

router = APIRouter(prefix="/documents", tags=["Documents"])

# ── schemas ─────────────────────────────────────────────────────────────────
class DocumentResponse(BaseModel):
    id:               int
    filename:         str
    document_type:    str
    validation_status: str
    validated_json:   Optional[dict]
    validation_errors: Optional[list]
    processed_by:     str
    created_at:       datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    extracted_text:  Optional[str]
    raw_json_output: Optional[str]
    pipeline_log:    Optional[list]

# ── routes ──────────────────────────────────────────────────────────────────
@router.post("/process", response_model=DocumentDetailResponse, status_code=201)
async def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and process a document image.
    Runs the full pipeline and saves results to database.
    """

    # validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Use JPEG, PNG or WEBP."
        )

    # save uploaded file temporarily
    os.makedirs("outputs", exist_ok=True)
    temp_path = f"outputs/temp_{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # run pipeline
        result = run_pipeline(temp_path)

        # save to database
        doc = Document(
            filename         = file.filename,
            document_type    = result.get("document_type", "unknown"),
            extracted_text   = result.get("extracted_text", ""),
            raw_json_output  = result.get("raw_json_output", ""),
            validated_json   = result.get("validated_json"),
            validation_status = result.get("validation_status", ""),
            validation_errors = result.get("validation_errors", []),
            pipeline_log     = result.get("pipeline_log", []),
            processed_by     = current_user.username
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}"
        )
    finally:
        # cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/", response_model=List[DocumentResponse])
def get_all_documents(
    skip: int = 0,
    limit: int = 20,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all documents processed by the current user.
    Optionally filter by document type.
    """
    query = db.query(Document).filter(
        Document.processed_by == current_user.username
    )

    if document_type:
        query = query.filter(Document.document_type == document_type)

    documents = query.order_by(
        Document.created_at.desc()
    ).offset(skip).limit(limit).all()

    return documents


@router.get("/{document_id}", response_model=DocumentDetailResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document by ID with full details"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.processed_by == current_user.username
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a document by ID"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.processed_by == current_user.username
    ).first()

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(doc)
    db.commit()
    return None


@router.get("/stats/summary")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get processing statistics for current user"""
    total = db.query(Document).filter(
        Document.processed_by == current_user.username
    ).count()

    # count by document type
    from sqlalchemy import func
    type_counts = db.query(
        Document.document_type,
        func.count(Document.id).label("count")
    ).filter(
        Document.processed_by == current_user.username
    ).group_by(Document.document_type).all()

    # count by validation status
    status_counts = db.query(
        Document.validation_status,
        func.count(Document.id).label("count")
    ).filter(
        Document.processed_by == current_user.username
    ).group_by(Document.validation_status).all()

    return {
        "total_documents": total,
        "by_type": {t: c for t, c in type_counts},
        "by_validation_status": {s: c for s, c in status_counts}
    }