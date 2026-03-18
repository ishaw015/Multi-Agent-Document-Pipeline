import requests
import os
from dotenv import load_dotenv
from state import PipelineState

load_dotenv()

MISTRAL_API_URL = os.getenv("MISTRAL_API_URL")
print("JSON Specialist model loaded ✓")

def run_json_extraction(text_input: str) -> str:
    """Call the fine-tuned Mistral model running on Colab T4 GPU via ngrok"""
    try:
        response = requests.post(
            MISTRAL_API_URL,
            json={"text": text_input},
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("output", "")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("❌ Colab API is not running. Start the Colab notebook first.")
    except requests.exceptions.Timeout:
        raise RuntimeError("❌ Colab API timed out. Model may still be loading.")

def json_specialist(state: PipelineState) -> PipelineState:
    """
    Agent 4: JSON Specialist
    Calls fine-tuned Mistral-7B (SFT) running on Colab T4 GPU via ngrok.
    """
    log = state.get("pipeline_log", [])
    log.append("JSON Specialist Agent: Extracting structured JSON...")

    extracted_text = state.get("extracted_text", "")
    document_type  = state.get("document_type", "unknown")

    if not extracted_text:
        log.append("JSON Specialist Agent: No extracted text in state")
        return {**state, "pipeline_log": log}

    model_input = f"""Document type: {document_type}
Extract the main product/item information from this document text:

{extracted_text}"""

    raw_output = run_json_extraction(model_input)

    log.append(f"JSON extracted ({len(raw_output)} chars)")
    log.append("JSON Specialist Agent: Complete")

    return {
        **state,
        "raw_json_output": raw_output,
        "pipeline_log": log,
        "current_agent": "validator"
    }