import google.genai as genai
import os
from dotenv import load_dotenv
from state import PipelineState
from gemini_utils import generate_with_retry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def classify_document(state: PipelineState) -> PipelineState:
    """
    Agent 3: Classifier
    Takes extracted text and classifies the document type.
    Supported types: invoice, receipt, purchase_order, bank_statement, resume, product_listing, unknown
    """
    log = state.get("pipeline_log", [])
    log.append("Classifier Agent: Classifying document type...")

    extracted_text = state.get("extracted_text", "")

    if not extracted_text:
        log.append("Classifier Agent: No extracted text found in state")
        return {**state, "pipeline_log": log}

    prompt = f"""Classify this document into exactly one of these categories:
- invoice: A bill for goods/services with line items and total amount due
- receipt: Proof of payment/purchase with merchant name, items, and total paid
- purchase_order: A buyer's official order to a vendor requesting goods/services
- bank_statement: A bank record showing account transactions over a period
- resume: A person's CV with work experience, education, and skills
- product_listing: A product description with price and details
- unknown: Cannot be classified into above categories

Document text:
{extracted_text}

Reply with ONLY one word from the list above. Nothing else."""

    response = generate_with_retry(client, 'gemini-2.5-flash', prompt)

    document_type = response.text.strip().lower()

    # validate it's one of our expected types
    valid_types = ["invoice", "receipt", "purchase_order", "bank_statement",
                   "resume", "product_listing", "unknown"]
    if document_type not in valid_types:
        document_type = "unknown"

    log.append(f"  ✓ Document classified as: {document_type}")
    log.append("Classifier Agent: Complete")

    return {
        **state,
        "document_type": document_type,
        "pipeline_log": log,
        "current_agent": "router"
    }