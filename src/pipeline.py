from langgraph.graph import StateGraph, END
from state import PipelineState
from agent_preprocessor import preprocess_document
from agent_extractor import extract_text
from agent_classifier import classify_document
from agent_router import route_document
from agent_json_specialist import json_specialist
from agent_receipt_specialist import receipt_specialist
from agent_po_specialist import po_specialist
from agent_bank_specialist import bank_specialist
from agent_resume_specialist import resume_specialist
from agent_validator import validate_output


def build_pipeline():
    """
    Build and compile the LangGraph pipeline.
    Connects all agents with conditional routing based on document type.
    """

    # create the graph with our shared state
    graph = StateGraph(PipelineState)

    # add each agent as a node
    graph.add_node("preprocessor",      preprocess_document)
    graph.add_node("extractor",         extract_text)
    graph.add_node("classifier",        classify_document)
    graph.add_node("json_specialist",   json_specialist)
    graph.add_node("receipt_specialist", receipt_specialist)
    graph.add_node("po_specialist",     po_specialist)
    graph.add_node("bank_specialist",   bank_specialist)
    graph.add_node("resume_specialist", resume_specialist)
    graph.add_node("validator",         validate_output)

    # fixed edges — first three agents always run in sequence
    graph.set_entry_point("preprocessor")
    graph.add_edge("preprocessor", "extractor")
    graph.add_edge("extractor",    "classifier")

    # conditional edge — router decides which specialist to run
    graph.add_conditional_edges(
        "classifier",
        route_document,
        {
            "json_specialist":    "json_specialist",
            "receipt_specialist": "receipt_specialist",
            "po_specialist":      "po_specialist",
            "bank_specialist":    "bank_specialist",
            "resume_specialist":  "resume_specialist",
        }
    )

    # all specialists lead to validator
    graph.add_edge("json_specialist",    "validator")
    graph.add_edge("receipt_specialist", "validator")
    graph.add_edge("po_specialist",      "validator")
    graph.add_edge("bank_specialist",    "validator")
    graph.add_edge("resume_specialist",  "validator")
    graph.add_edge("validator",          END)

    # compile and return
    pipeline = graph.compile()
    return pipeline


def run_pipeline(image_path: str) -> PipelineState:
    """
    Run the full pipeline on a document image.
    Returns the final state with all agent outputs.
    """
    pipeline = build_pipeline()

    # initial state
    initial_state: PipelineState = {
        "image_path":            image_path,
        "processed_image_path":  "",
        "extracted_text":        "",
        "document_type":         "",
        "raw_json_output":       "",
        "validated_json":        None,
        "validation_status":     "",
        "validation_errors":     [],
        "pipeline_log":          [],
        "current_agent":         "preprocessor"
    }

    print(f"\nRunning pipeline on: {image_path}")
    print("=" * 50)

    final_state = pipeline.invoke(initial_state)

    # print pipeline log
    for entry in final_state["pipeline_log"]:
        print(entry)

    print("=" * 50)
    print(f"Document type:      {final_state['document_type']}")
    print(f"Validation status:  {final_state['validation_status']}")

    return final_state


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = run_pipeline(sys.argv[1])
    else:
        print("Usage: python pipeline.py <image_path>")