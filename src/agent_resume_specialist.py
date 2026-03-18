import google.genai as genai
import os
from dotenv import load_dotenv
from state import PipelineState
from gemini_utils import generate_with_retry

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def resume_specialist(state: PipelineState) -> PipelineState:
    """
    Agent 4e: Resume/CV Specialist
    Uses Gemini to extract structured JSON from resume documents.
    Schema: name, email, phone, location, summary, skills,
            experience, education
    """
    log = state.get("pipeline_log", [])
    log.append("Resume Specialist Agent: Extracting structured JSON...")

    extracted_text = state.get("extracted_text", "")

    if not extracted_text:
        log.append("Resume Specialist Agent: No extracted text in state")
        return {**state, "pipeline_log": log}

    prompt = f"""You are a JSON extraction API. Extract resume/CV information from this document.

Document text:
{extracted_text}

Return ONLY a valid JSON object matching this exact schema — no markdown, no explanation, no extra text:
{{
    "name": "string",
    "email": "string",
    "phone": "string",
    "location": "string",
    "summary": "string",
    "skills": ["string"],
    "experience": [
        {{
            "company": "string",
            "role": "string",
            "duration": "string",
            "description": "string"
        }}
    ],
    "education": [
        {{
            "institution": "string",
            "degree": "string",
            "year": "string"
        }}
    ]
}}

Rules:
- skills must be an array of strings
- experience and education must be arrays of objects
- duration format: "MMM YYYY - MMM YYYY" e.g. "Jan 2020 - Mar 2023"
- If currently working, duration ends with "Present" e.g. "Jan 2020 - Present"
- If a value is not found, use null for strings and empty array [] for arrays
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
    log.append("Resume Specialist Agent: Complete")

    return {
        **state,
        "raw_json_output": raw_output,
        "pipeline_log": log,
        "current_agent": "validator"
    }