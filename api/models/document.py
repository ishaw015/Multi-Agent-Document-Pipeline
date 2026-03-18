from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from api.models.database import Base

class Document(Base):
    __tablename__ = "documents"

    id                = Column(Integer, primary_key=True, index=True)
    filename          = Column(String, nullable=False)
    document_type     = Column(String, nullable=False)
    extracted_text    = Column(String)
    raw_json_output   = Column(String)
    validated_json    = Column(JSON)      # accepts dict OR list
    validation_status = Column(String)
    validation_errors = Column(JSON)
    pipeline_log      = Column(JSON)
    processed_by      = Column(String)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())