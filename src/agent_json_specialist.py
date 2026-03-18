import google.genai as genai
import os
from dotenv import load_dotenv
from state import PipelineState
from gemini_utils import generate_with_retry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
print("JSON Specialist model loaded ✓")

def json_specialist(state: PipelineState) -> PipelineState:
    """
    Agent 4: JSON Specialist
    Uses Gemini to extract schema-compliant JSON from
    invoice and product listing documents.
    """
    log = state.get("pipeline_log", [])
    log.append("JSON Specialist Agent: Extracting structured JSON...")

    extracted_text = state.get("extracted_text", "")
    document_type  = state.get("document_type", "unknown")

    if not extracted_text:
        log.append("JSON Specialist Agent: No extracted text in state")
        return {**state, "pipeline_log": log}

    prompt = f"""Extract the main product/service information from this {document_type} document.
If there are multiple line items, summarize them into ONE single JSON object representing the overall document.

{extracted_text}

Return ONLY this JSON, no markdown, no explanation:
{{"product_name":"string","price":number,"currency":"string","category":"string","attributes":{{}},"in_stock":true/false,"tags":["string"]}}

Rules:
- product_name should describe the overall service/product category
- price should be the TOTAL amount
- price must be a number
- in_stock must be a boolean
- tags must be array of strings
- Output ONLY a single JSON object, never a list"""

    response = generate_with_retry(client, 'gemini-2.5-flash', prompt)

    raw_output = response.text.strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.split("```")[1]
        if raw_output.startswith("json"):
            raw_output = raw_output[4:]
        raw_output = raw_output.strip()

    log.append(f"  ✓ JSON extracted ({len(raw_output)} chars)")
    log.append("JSON Specialist Agent: Complete")

    return {
        **state,
        "raw_json_output": raw_output,
        "pipeline_log": log,
        "current_agent": "validator"
    }