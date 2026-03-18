import google.genai as genai
import os
from dotenv import load_dotenv
from state import PipelineState
from gemini_utils import generate_with_retry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def receipt_specialist(state: PipelineState) -> PipelineState:
    """
    Agent 4b: Receipt Specialist
    Uses Gemini to extract structured JSON from receipt documents.
    Schema: merchant_name, date, items, subtotal, tax, total, 
            currency, payment_method
    Note: Can be replaced with fine-tuned Mistral later for 
          higher volume/consistency.
    """
    log = state.get("pipeline_log", [])
    log.append("Receipt Specialist Agent: Extracting structured JSON...")

    extracted_text = state.get("extracted_text", "")

    if not extracted_text:
        log.append("Receipt Specialist Agent: No extracted text in state")
        return {**state, "pipeline_log": log}

    prompt = f"""You are a JSON extraction API. Extract receipt information from this document.

Document text:
{extracted_text}

Return ONLY a valid JSON object matching this exact schema — no markdown, no explanation, no extra text:
{{
    "merchant_name": "string",
    "date": "string",
    "items": [
        {{
            "name": "string",
            "price": number
        }}
    ],
    "subtotal": number,
    "tax": number,
    "total": number,
    "currency": "string",
    "payment_method": "string"
}}

Rules:
- subtotal, tax, total must be numbers not strings
- items must be an array of objects with name and price
- currency should be 3-letter code e.g. USD, EUR, GBP, INR
- payment_method: cash, card, upi, unknown
- date format: DD-MM-YYYY
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
    log.append("Receipt Specialist Agent: Complete")

    return {
        **state,
        "raw_json_output": raw_output,
        "pipeline_log": log,
        "current_agent": "validator"
    }