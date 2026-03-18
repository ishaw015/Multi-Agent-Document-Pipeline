from state import PipelineState

def route_document(state: PipelineState) -> str:
    """
    Router: Reads the document type from state and returns
    the name of the next agent node to run.
    Used by LangGraph's conditional edges.
    """
    document_type = state.get("document_type", "unknown")

    route_map = {
        "product_listing": "json_specialist",
        "invoice":         "json_specialist",
        "receipt":         "receipt_specialist",
        "purchase_order":  "po_specialist",
        "bank_statement":  "bank_specialist",
        "resume":          "resume_specialist",
        "unknown":         "json_specialist",  # fallback
    }

    next_agent = route_map.get(document_type, "json_specialist")
    return next_agent
  
  
#LangGraph uses this function in pipeline.py via add_conditional_edges — instead of a fixed edge from classifier → one agent, it will call route_document() to decide dynamically.