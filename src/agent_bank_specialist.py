import google.genai as genai
import os
from dotenv import load_dotenv
from state import PipelineState
from gemini_utils import generate_with_retry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def bank_specialist(state: PipelineState) -> PipelineState:
    """
    Agent 4d: Bank Statement Specialist
    Uses Gemini to extract structured JSON from bank statement documents.
    Schema: bank_name, account_holder, account_number, statement_period,
            opening_balance, closing_balance, currency, transactions
    """
    log = state.get("pipeline_log", [])
    log.append("Bank Statement Specialist Agent: Extracting structured JSON...")

    extracted_text = state.get("extracted_text", "")

    if not extracted_text:
        log.append("Bank Statement Specialist Agent: No extracted text in state")
        return {**state, "pipeline_log": log}

    prompt = f"""You are a JSON extraction API. Extract bank statement information from this document.

Document text:
{extracted_text}

Return ONLY a valid JSON object matching this exact schema — no markdown, no explanation, no extra text:
{{
    "bank_name": "string",
    "account_holder": "string",
    "account_number": "string",
    "statement_period": "string",
    "opening_balance": number,
    "closing_balance": number,
    "currency": "string",
    "transactions": [
        {{
            "date": "string",
            "description": "string",
            "amount": number,
            "type": "credit or debit"
        }}
    ]
}}

Rules:
- opening_balance, closing_balance, amount must be numbers not strings
- transactions must be an array of objects
- type must be either "credit" or "debit" only
- currency should be 3-letter code e.g. USD, EUR, GBP, INR
- account_number: extract as string exactly as it appears
- statement_period: format as "DD-MM-YYYY to DD-MM-YYYY"
- date format in transactions: DD-MM-YYYY — dates appear in the leftmost column of the transaction table, convert from YYYY-MM-DD to DD-MM-YYYY format
- every transaction row in the table has a date — do NOT return null for date, look carefully at the Date column
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
    log.append("Bank Statement Specialist Agent: Complete")

    return {
        **state,
        "raw_json_output": raw_output,
        "pipeline_log": log,
        "current_agent": "validator"
    }