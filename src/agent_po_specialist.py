import google.genai as genai
import os
from dotenv import load_dotenv
from state import PipelineState
from gemini_utils import generate_with_retry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def po_specialist(state: PipelineState) -> PipelineState:
    """
    Agent 4c: Purchase Order Specialist
    Uses Gemini to extract structured JSON from purchase order documents.
    Schema: po_number, date, vendor, buyer, items, subtotal, 
            tax, total, currency, status
    """
    log = state.get("pipeline_log", [])
    log.append("Purchase Order Specialist Agent: Extracting structured JSON...")

    extracted_text = state.get("extracted_text", "")

    if not extracted_text:
        log.append("Purchase Order Specialist Agent: No extracted text in state")
        return {**state, "pipeline_log": log}

    prompt = f"""You are a JSON extraction API. Extract purchase order information from this document.

Document text:
{extracted_text}

Return ONLY a valid JSON object matching this exact schema — no markdown, no explanation, no extra text:
{{
    "po_number": "string",
    "date": "string",
    "vendor": "string",
    "buyer": "string",
    "items": [
        {{
            "description": "string",
            "quantity": number,
            "unit_price": number,
            "total": number
        }}
    ],
    "subtotal": number,
    "tax": number,
    "total": number,
    "currency": "string",
    "status": "string"
}}

Rules:
- quantity, unit_price, subtotal, tax, total must be numbers not strings
- items must be an array of objects
- currency should be 3-letter code e.g. USD, EUR, GBP, INR
- status: pending, approved, delivered, cancelled, unknown
- date format: DD-MM-YYYY
- po_number: extract as string exactly as it appears
- If a value is not found, use null for strings and 0 for numbers
- Output ONLY the JSON object, nothing else"""

    response = generate_with_retry(
        client,
        'gemini-2.5-flash',
        prompt
    )

    raw_output = response.text.strip()

    # strip markdown code fences if Gemini wraps in ```json
    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    log.append(f"  ✓ JSON extracted ({len(raw_output)} chars)")
    log.append("Purchase Order Specialist Agent: Complete")

    return {
        **state,
        "raw_json_output": raw_output,
        "pipeline_log": log,
        "current_agent": "validator"
    } 