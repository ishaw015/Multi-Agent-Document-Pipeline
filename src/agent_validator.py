import json
from jsonschema import validate, ValidationError
from state import PipelineState

# ── schemas ────────────────────────────────────────────────────────────────

PRODUCT_SCHEMA = {
    "type": "object",
    "required": ["product_name", "price", "currency", "category",
                 "attributes", "in_stock", "tags"],
    "properties": {
        "product_name": {"type": "string"},
        "price":        {"type": "number"},
        "currency":     {"type": "string"},
        "category":     {"type": "string"},
        "attributes":   {"type": "object"},
        "in_stock":     {"type": "boolean"},
        "tags":         {"type": "array", "items": {"type": "string"}}
    },
    "additionalProperties": False
}

INVOICE_SCHEMA = {
    "type": "object",
    "required": ["product_name", "price", "currency", "category",
                 "attributes", "in_stock", "tags"],
    "properties": {
        "product_name": {"type": "string"},
        "price":        {"type": "number"},
        "currency":     {"type": "string"},
        "category":     {"type": "string"},
        "attributes":   {"type": "object"},
        "in_stock":     {"type": "boolean"},
        "tags":         {"type": "array", "items": {"type": "string"}}
    },
    "additionalProperties": False
}

RECEIPT_SCHEMA = {
    "type": "object",
    "required": ["merchant_name", "date", "items", "subtotal",
                 "tax", "total", "currency", "payment_method"],
    "properties": {
        "merchant_name":  {"type": ["string", "null"]},
        "date":           {"type": ["string", "null"]},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name":  {"type": "string"},
                    "price": {"type": "number"}
                }
            }
        },
        "subtotal":       {"type": "number"},
        "tax":            {"type": "number"},
        "total":          {"type": "number"},
        "currency":       {"type": ["string", "null"]},
        "payment_method": {"type": ["string", "null"]}
    },
    "additionalProperties": False
}

PURCHASE_ORDER_SCHEMA = {
    "type": "object",
    "required": ["po_number", "date", "vendor", "buyer", "items",
                 "subtotal", "tax", "total", "currency", "status"],
    "properties": {
        "po_number": {"type": ["string", "null"]},
        "date":      {"type": ["string", "null"]},
        "vendor":    {"type": ["string", "null"]},
        "buyer":     {"type": ["string", "null"]},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity":    {"type": "number"},
                    "unit_price":  {"type": "number"},
                    "total":       {"type": "number"}
                }
            }
        },
        "subtotal": {"type": "number"},
        "tax":      {"type": "number"},
        "total":    {"type": "number"},
        "currency": {"type": ["string", "null"]},
        "status":   {"type": ["string", "null"]}
    },
    "additionalProperties": False
}

BANK_STATEMENT_SCHEMA = {
    "type": "object",
    "required": ["bank_name", "account_holder", "account_number",
                 "statement_period", "opening_balance", "closing_balance",
                 "currency", "transactions"],
    "properties": {
        "bank_name":        {"type": ["string", "null"]},
        "account_holder":   {"type": ["string", "null"]},
        "account_number":   {"type": ["string", "null"]},
        "statement_period": {"type": ["string", "null"]},
        "opening_balance":  {"type": "number"},
        "closing_balance":  {"type": "number"},
        "currency":         {"type": ["string", "null"]},
        "transactions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "date":        {"type": "string"},
                    "description": {"type": "string"},
                    "amount":      {"type": "number"},
                    "type":        {"type": "string", "enum": ["credit", "debit"]}
                }
            }
        }
    },
    "additionalProperties": False
}

RESUME_SCHEMA = {
    "type": "object",
    "required": ["name", "email", "phone", "location", "summary",
                 "skills", "experience", "education"],
    "properties": {
        "name":     {"type": ["string", "null"]},
        "email":    {"type": ["string", "null"]},
        "phone":    {"type": ["string", "null"]},
        "location": {"type": ["string", "null"]},
        "summary":  {"type": ["string", "null"]},
        "skills":   {"type": "array", "items": {"type": "string"}},
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company":     {"type": "string"},
                    "role":        {"type": "string"},
                    "duration":    {"type": "string"},
                    "description": {"type": "string"}
                }
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "institution": {"type": "string"},
                    "degree":      {"type": "string"},
                    "year":        {"type": "string"}
                }
            }
        }
    },
    "additionalProperties": False
}

# ── schema map ─────────────────────────────────────────────────────────────

SCHEMA_MAP = {
    "product_listing": PRODUCT_SCHEMA,
    "invoice":         INVOICE_SCHEMA,
    "receipt":         RECEIPT_SCHEMA,
    "purchase_order":  PURCHASE_ORDER_SCHEMA,
    "bank_statement":  BANK_STATEMENT_SCHEMA,
    "resume":          RESUME_SCHEMA,
}

# ── validator agent ────────────────────────────────────────────────────────

def validate_output(state: PipelineState) -> PipelineState:
    """
    Agent 5: Validator
    Validates the JSON output from any specialist agent
    against the correct schema for the document type.
    No LLM needed — pure Python.
    """
    log = state.get("pipeline_log", [])
    log.append("Validator Agent: Validating JSON output...")

    raw_json      = state.get("raw_json_output", "")
    document_type = state.get("document_type", "unknown")
    errors        = []
    validated_json    = None
    validation_status = ""

    if not raw_json:
        log.append("Validator Agent: No JSON output found in state")
        return {**state, "pipeline_log": log}

    # check 1 — is it valid JSON at all?
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {str(e)}")
        validation_status = "Invalid JSON"
        log.append(f"  ✗ JSON parsing failed: {e}")
        return {
            **state,
            "validated_json":    None,
            "validation_status": validation_status,
            "validation_errors": errors,
            "pipeline_log":      log,
            "current_agent":     "complete"
        }

    # check 2 — is it a safety refusal?
    if "error" in parsed:
        validation_status = "Safety Refusal"
        validated_json = parsed
        log.append(f"  ⚠ Safety refusal detected: {parsed.get('field', 'unknown field')}")
        log.append("Validator Agent: Complete")
        return {
            **state,
            "validated_json":    validated_json,
            "validation_status": validation_status,
            "validation_errors": [],
            "pipeline_log":      log,
            "current_agent":     "complete"
        }

    # check 3 — pick the right schema
    schema = SCHEMA_MAP.get(document_type)

    if not schema:
        validation_status = "No Schema Found"
        validated_json = parsed
        log.append(f"  ⚠ No schema found for document type: {document_type}")
        log.append("Validator Agent: Complete")
        return {
            **state,
            "validated_json":    validated_json,
            "validation_status": validation_status,
            "validation_errors": [],
            "pipeline_log":      log,
            "current_agent":     "complete"
        }

    # check 4 — does it match the schema?
    try:
        validate(instance=parsed, schema=schema)
        validation_status = "Valid — Schema Compliant"
        validated_json = parsed
        log.append("  ✓ JSON is schema compliant")
    except ValidationError as e:
        errors.append(f"Schema error: {e.message}")
        validation_status = "Schema Error"
        validated_json = parsed
        log.append(f"  ✗ Schema error: {e.message}")

    log.append("Validator Agent: Complete")

    return {
        **state,
        "validated_json":    validated_json,
        "validation_status": validation_status,
        "validation_errors": errors,
        "pipeline_log":      log,
        "current_agent":     "complete"
    }