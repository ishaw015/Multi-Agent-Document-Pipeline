import google.genai as genai
import base64
import os
from dotenv import load_dotenv
from state import PipelineState
from gemini_utils import generate_with_retry
import mimetypes

load_dotenv()


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text(state: PipelineState) -> PipelineState:
    """
    Agent 2: Text Extractor
    Takes the preprocessed image and uses Gemini Vision
    to extract all text content from the document.
    """
    log = state.get("pipeline_log", [])
    log.append("Extractor Agent: Starting text extraction...")

    processed_image_path = state.get("processed_image_path")

    if not processed_image_path:
        log.append("Extractor Agent: No processed image found in state")
        return {**state, "pipeline_log": log}

    # read and encode image as base64
    with open(processed_image_path, "rb") as f:
        image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # call Gemini Vision
    prompt = """Extract ALL text from this document image exactly as it appears.
Include all:
- Company names, addresses, contact details
- Item names, descriptions, quantities
- Prices, totals, taxes, discounts
- Dates, invoice numbers, reference numbers
- Any other text visible in the document

Return the raw extracted text only. No formatting, no commentary."""

    mime_type, _ = mimetypes.guess_type(processed_image_path)
    mime_type = mime_type or "image/jpeg" 

    response = generate_with_retry(
        client,'gemini-2.5-flash',
        contents=[
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_b64
                        }
                    }
                ]
            }
        ]
    )

    extracted_text = response.text
    log.append(f"Extracted {len(extracted_text)} characters of text")
    log.append("Extractor Agent: Complete")

    return {
        **state,
        "extracted_text": extracted_text,
        "pipeline_log": log,
        "current_agent": "classifier"
    }