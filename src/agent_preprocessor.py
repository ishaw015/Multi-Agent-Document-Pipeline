import cv2
import numpy as np
import os
from state import PipelineState

def preprocess_document(state: PipelineState) -> PipelineState:
    """
    Agent 1: Preprocessor
    Takes a raw document image and applies:
    - Grayscale conversion
    - Denoising
    - Contrast enhancement (CLAHE)
    - Deskewing
    Saves the processed image and updates state.
    """
    log = state.get("pipeline_log", [])
    log.append("Preprocessor Agent: Starting image preprocessing...")

    image_path = state["image_path"]

    # read image
    image = cv2.imread(image_path)
    if image is None:
        log.append("Preprocessor Agent: Could not read image")
        return {**state, "pipeline_log": log}

    # step 1 — convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    log.append("Converted to grayscale")

    # step 2 — denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    log.append("Applied denoising")

    # step 3 — enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    log.append("Enhanced contrast with CLAHE")

    # step 4 — deskew
    coords = np.column_stack(np.where(enhanced > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        if abs(angle) > 0.5:  # only rotate if skew is significant
            (h, w) = enhanced.shape
            center = (w // 2, h // 2)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            deskewed = cv2.warpAffine(
                enhanced, rotation_matrix, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            log.append(f"Deskewed image (angle: {angle:.2f}°)")
        else:
            deskewed = enhanced
            log.append("No deskewing needed (angle < 0.5°)")
    else:
        deskewed = enhanced

    # step 5 — save processed image
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(image_path)
    processed_path = os.path.join(output_dir, f"processed_{filename}")
    cv2.imwrite(processed_path, deskewed)
    log.append(f"  ✓ Saved processed image to {processed_path}")
    log.append("Preprocessor Agent: Complete")

    return {
        **state,
        "processed_image_path": processed_path,
        "pipeline_log": log,
        "current_agent": "extractor"
    }