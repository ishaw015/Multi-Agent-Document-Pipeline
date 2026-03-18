import streamlit as st
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(__file__))
from pipeline import run_pipeline

st.set_page_config(
    page_title="Document Processing Pipeline",
    page_icon="🤖",
    layout="wide"
)

# custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0F1117; }
    h1 { 
        font-size: 2.2rem !important; 
        font-weight: 700 !important;
        color: #FFFFFF !important;
        padding-bottom: 0.2rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
        color: #E0E0E0 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 6px;
        margin-bottom: 16px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        color: #A0A0A0 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.3rem !important;
        color: #2E86AB !important;
        font-weight: 700 !important;
    }
    [data-testid="stFileUploader"] {
        background: #1A1D27;
        border: 2px dashed #2E86AB;
        border-radius: 12px;
        padding: 16px;
    }
    .agent-card {
        background: #1A1D27;
        border-left: 3px solid #2E86AB;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 10px;
        font-size: 0.85rem;
    }
    .agent-name {
        font-weight: 700;
        color: #FFFFFF;
        font-size: 0.9rem;
    }
    .agent-desc {
        color: #888888;
        font-size: 0.78rem;
    }
    .doc-badge {
        display: inline-block;
        background: #1A1D27;
        border: 1px solid #2E86AB;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 4px;
        font-size: 0.78rem;
        color: #2E86AB;
    }
    .result-card {
        background: #1A1D27;
        border: 1px solid #2E2E3A;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .pipeline-info {
        background: #1A1D27;
        border: 1px solid #2E2E3A;
        border-radius: 10px;
        padding: 20px;
        margin-top: 10px;
    }
    .pipeline-info p {
        color: #CCCCCC;
        font-size: 0.9rem;
        line-height: 1.8;
    }
    hr { border-color: #2E2E3A !important; }
    .stJson {
        background: #1A1D27 !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background: #2E86AB !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 2rem !important;
        width: 100%;
    }
    .stButton > button:hover {
        background: #1A6A8A !important;
    }
    [data-testid="stSidebar"] {
        background: #13151F !important;
        border-right: 1px solid #2E2E3A;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        border-bottom: 1px solid #2E2E3A !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Mistral API health check ──────────────────────────────────────────────────
import requests
from dotenv import load_dotenv
load_dotenv()

mistral_url = os.getenv("MISTRAL_API_URL", "").replace("/extract", "/health")
if mistral_url:
    try:
        r = requests.get(mistral_url, timeout=5)
        if r.json().get("status") == "ok":
            st.sidebar.success("🟢 Mistral API: Online")
        else:
            st.sidebar.error("🔴 Mistral API: Offline")
    except:
        st.sidebar.error("🔴 Mistral API: Offline — run Colab notebook")
else:
    st.sidebar.warning("⚠ MISTRAL_API_URL not set in .env")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🤖 Intelligent Document Processing Pipeline")
st.markdown("**Multi-Agent System** — OpenCV + Gemini Vision + Fine-tuned Mistral-7B")
st.markdown("---")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Pipeline Agents")
    agents = [
        ("🔧", "Preprocessor",       "OpenCV — deskew, denoise, CLAHE"),
        ("👁",  "Extractor",          "Gemini Vision — OCR"),
        ("🏷",  "Classifier",         "Gemini Flash — doc type"),
        ("🔀", "Router",             "Conditional — picks specialist"),
        ("🤖", "JSON Specialist",    "Fine-tuned Mistral-7B (invoice/product)"),
        ("🧾", "Receipt Specialist",  "Gemini Flash"),
        ("📦", "PO Specialist",      "Gemini Flash"),
        ("🏦", "Bank Specialist",    "Gemini Flash"),
        ("📄", "Resume Specialist",  "Gemini Flash"),
        ("✔",  "Validator",          "jsonschema — Python"),
    ]
    for icon, name, desc in agents:
        st.markdown(f"""
        <div class="agent-card">
            <div class="agent-name">{icon} {name}</div>
            <div class="agent-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📄 Supported Documents")
    doc_types = ["🧾 Invoice", "🛒 Receipt", "📦 Purchase Order",
                 "🏦 Bank Statement", "📄 Resume/CV", "🏷 Product Listing"]
    for doc in doc_types:
        st.markdown(f'<span class="doc-badge">{doc}</span>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔗 Model")
    st.markdown("[mistral-json-specialist](https://huggingface.co/Isha0408/mistral-json-specialist)")
    st.caption("Mistral-7B fine-tuned with QLoRA + SFT")

    st.markdown("---")
    st.markdown("### 📊 Model Performance")
    metrics = {
        "JSON Valid":       "100%",
        "Schema Compliant": "100%",
        "Zero Extra Text":  "100%",
        "Safety Compliant": "100%",
    }
    for k, v in metrics.items():
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            st.caption(k)
        with col_m2:
            st.markdown(f"**{v}**")

# ── helper — process one file ─────────────────────────────────────────────────
def process_single_file(uploaded_file):
    """Process a single uploaded file through the pipeline"""
    temp_path = f"outputs/temp_{uploaded_file.name}"
    os.makedirs("outputs", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    try:
        result = run_pipeline(temp_path)
        result["_filename"] = uploaded_file.name
        result["_success"] = True
        return result
    except Exception as e:
        return {
            "_filename": uploaded_file.name,
            "_success": False,
            "_error": str(e)
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ── helper — render one result ────────────────────────────────────────────────
def render_result(result, index):
    """Render pipeline result for one document"""
    filename = result.get("_filename", f"Document {index+1}")
    success  = result.get("_success", False)

    with st.expander(
        f"📄 {filename} — "
        f"{result.get('document_type', 'unknown').upper().replace('_', ' ')} "
        f"{'✅' if success else '❌'}",
        expanded=index == 0  # expand first result by default
    ):
        if not success:
            st.error(f"Pipeline error: {result.get('_error', 'Unknown error')}")
            return

        # metrics
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Document Type",
                      result.get("document_type", "—").upper().replace("_", " "))
        with col_b:
            st.metric("Validation", result.get("validation_status", "—"))
        with col_c:
            st.metric("Text Extracted",
                      f"{len(result.get('extracted_text', ''))} chars")

        # validation errors
        if result.get("validation_errors"):
            st.warning("Validation errors: " +
                       ", ".join(result["validation_errors"]))

        # tabs for different views
        tab1, tab2, tab3 = st.tabs(["🔧 JSON Output", "📝 Extracted Text", "🗂 Agent Log"])

        with tab1:
            validated_json = result.get("validated_json")
            if validated_json:
                st.json(validated_json)
            else:
                st.code(result.get("raw_json_output", "No output"), language="json")

        with tab2:
            st.text(result.get("extracted_text", "No text extracted"))

        with tab3:
            for entry in result.get("pipeline_log", []):
                if "✗" in entry or "❌" in entry:
                    st.error(entry)
                elif "✅" in entry:
                    st.success(entry)
                elif "⚠" in entry:
                    st.warning(entry)
                elif "✓" in entry:
                    st.caption(entry)
                else:
                    st.text(entry)

        # preprocessed image
        processed_path = result.get("processed_image_path")
        if processed_path and os.path.exists(processed_path):
            st.markdown("**🔧 Preprocessed Image**")
            st.image(processed_path,
                     caption="After deskew + denoise + CLAHE",
                     use_container_width=True)

# ── Main Layout ───────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📄 Upload Documents")

    uploaded_files = st.file_uploader(
        "Drag and drop or browse — supports multiple files",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,    # ← multi-file enabled
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
        for f in uploaded_files:
            st.caption(f"📎 {f.name}")

        st.markdown("")

        # show preview of first image
        st.image(
            uploaded_files[0],
            caption=f"Preview: {uploaded_files[0].name}",
            use_container_width=True
        )
        if len(uploaded_files) > 1:
            st.caption(f"+ {len(uploaded_files) - 1} more file(s)")

        st.markdown("")
        run_btn = st.button("🚀 Run Pipeline", type="primary")
    else:
        st.markdown("""
        <div class="pipeline-info">
            <p>
            📌 <b>Supported documents:</b><br>
            &nbsp;&nbsp;• 🧾 Invoices<br>
            &nbsp;&nbsp;• 🛒 Receipts<br>
            &nbsp;&nbsp;• 📦 Purchase Orders<br>
            &nbsp;&nbsp;• 🏦 Bank Statements<br>
            &nbsp;&nbsp;• 📄 Resumes / CVs<br>
            &nbsp;&nbsp;• 🏷 Product Listings<br><br>
            🔁 <b>Pipeline flow:</b><br>
            &nbsp;&nbsp;Upload → Preprocess → Extract Text<br>
            &nbsp;&nbsp;→ Classify → Route → Specialist<br>
            &nbsp;&nbsp;→ Validate → Structured JSON<br><br>
            💡 <b>Tip:</b> You can upload multiple files at once!
            </p>
        </div>
        """, unsafe_allow_html=True)
        run_btn = False

with col2:
    st.markdown("### ⚙️ Pipeline Execution")

    if uploaded_files and run_btn:
        total   = len(uploaded_files)
        results = []

        # progress tracking
        progress_bar = st.progress(0)
        status_text  = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(
                f"⏳ Processing {uploaded_file.name} ({i+1}/{total})..."
            )
            result = process_single_file(uploaded_file)
            results.append(result)
            progress_bar.progress((i + 1) / total)

        progress_bar.progress(1.0)

        # summary metrics
        successful = sum(1 for r in results if r.get("_success"))
        failed     = total - successful

        status_text.text(
            f"✅ Done! {successful}/{total} documents processed successfully"
        )

        st.markdown("---")

        # overall summary
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Total Processed", total)
        with col_s2:
            st.metric("Successful", successful)
        with col_s3:
            st.metric("Failed", failed)

        st.markdown("---")

        # document type breakdown
        if successful > 0:
            from collections import Counter
            type_counts = Counter(
                r.get("document_type", "unknown")
                for r in results if r.get("_success")
            )
            st.markdown("**📊 Document Types Found:**")
            type_cols = st.columns(len(type_counts))
            for idx, (doc_type, count) in enumerate(type_counts.items()):
                with type_cols[idx]:
                    st.metric(
                        doc_type.replace("_", " ").title(),
                        count
                    )

        st.markdown("---")
        st.markdown("**📋 Results:**")

        # render each result
        for i, result in enumerate(results):
            render_result(result, i)

    elif not uploaded_files:
        st.info("⬅️ Upload document images to start the pipeline.")