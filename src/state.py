from typing import TypedDict, Optional, List

class PipelineState(TypedDict):
    # input
    image_path: str

    # after preprocessor agent
    processed_image_path: str

    # after extractor agent
    extracted_text: str

    # after classifier agent
    document_type: str

    # after any specialist agent
    raw_json_output: str

    # after validator agent
    validated_json: Optional[dict]
    validation_status: str
    validation_errors: List[str]

    # pipeline metadata
    pipeline_log: List[str]
    current_agent: str