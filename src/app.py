import mimetypes

import streamlit as st
import json
import os
import requests
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "https://multi-agentdocument-pipeline-production.up.railway.app")

st.set_page_config(
    page_title="DocPipeline AI",
    page_icon="🤖",
    layout="wide"
)

# ── Session state ─────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    * { font-family: 'DM Sans', sans-serif; }
    .stApp { background-color: #080B14; }
    #MainMenu, footer, header { visibility: hidden; }

    .stat-card {
        background: #0D1117;
        border: 1px solid #1E2D40;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .stat-num {
        font-family: 'Space Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #2E86AB;
    }
    .stat-label {
        font-size: 0.78rem;
        color: #5A6A7A;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }
    .section-title {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        font-weight: 700;
        color: #2E86AB;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 16px;
    }
    .stTextInput > div > div > input {
        background: #161B22 !important;
        border: 1px solid #1E2D40 !important;
        border-radius: 8px !important;
        color: #E0E0E0 !important;
        font-size: 0.9rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #2E86AB !important;
        box-shadow: 0 0 0 2px rgba(46,134,171,0.15) !important;
    }
    .stButton > button {
        background: #2E86AB !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.55rem 1.5rem !important;
        width: 100%;
        transition: background 0.2s !important;
    }
    .stButton > button:hover { background: #236888 !important; }
    .stTabs [data-baseweb="tab-list"] {
        background: #0D1117;
        border-radius: 8px;
        gap: 4px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #5A6A7A;
        border-radius: 6px;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: #2E86AB !important;
        color: white !important;
    }
    [data-testid="stFileUploader"] {
        background: #0D1117;
        border: 2px dashed #1E2D40;
        border-radius: 12px;
        padding: 12px;
    }
    [data-testid="stSidebar"] { display: none; }
    section[data-testid="stSidebarContent"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── API helpers ───────────────────────────────────────────────────────────────
def check_api_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        return r.status_code == 200
    except:
        return False

def login(username, password):
    try:
        r = requests.post(
            f"{API_URL}/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if r.status_code == 200:
            return r.json().get("access_token"), None
        return None, r.json().get("detail", "Login failed")
    except Exception as e:
        return None, str(e)

def register(username, email, password):
    try:
        r = requests.post(
            f"{API_URL}/auth/register",
            json={"username": username, "email": email, "password": password},
            timeout=10
        )
        if r.status_code == 201:
            return True, None
        return False, r.json().get("detail", "Registration failed")
    except Exception as e:
        return False, str(e)

def process_document(file_bytes, filename):
    mime_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    try:
        r = requests.post(
            f"{API_URL}/documents/process",
            files={"file": (filename, file_bytes, mime_type)},
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=120
        )
        if r.status_code in (200, 201):
            return r.json(), None
        return None, r.json().get("detail", "Processing failed")
    except Exception as e:
        return None, str(e)

def get_document_history():
    try:
        r = requests.get(
            f"{API_URL}/documents/",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=10
        )
        return r.json() if r.status_code == 200 else []
    except:
        return []

def get_stats():
    try:
        r = requests.get(
            f"{API_URL}/documents/stats/summary",
            headers={"Authorization": f"Bearer {st.session_state.token}"},
            timeout=10
        )
        return r.json() if r.status_code == 200 else {}
    except:
        return {}

# ════════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ════════════════════════════════════════════════════════════════════════════════
if not st.session_state.token:

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("""
        <div style="text-align:center; padding-top:48px; margin-bottom:32px;">
            <div style="font-family:'Space Mono',monospace; font-size:2rem; font-weight:700; color:#2E86AB;">
                ⬡ DocPipeline
            </div>
            <div style="font-size:0.9rem; color:#5A6A7A; margin-top:8px;">
                Multi-Agent Document Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        if check_api_health():
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            if st.button("Login", key="toggle_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
        with col_t2:
            if st.button("Register", key="toggle_register"):
                st.session_state.auth_mode = "register"
                st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.session_state.auth_mode == "login":
            st.markdown("#### 🔐 Welcome back")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login →")
                if submitted:
                    if not username or not password:
                        st.error("Please fill in all fields.")
                    else:
                        with st.spinner("Logging in..."):
                            token, err = login(username, password)
                        if token:
                            st.session_state.token = token
                            st.session_state.username = username
                            st.rerun()
                        else:
                            st.error(f"❌ {err}")
        else:
            st.markdown("#### 📝 Create account")
            with st.form("register_form"):
                username = st.text_input("Username", placeholder="choose a username")
                email    = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Create Account →")
                if submitted:
                    if not username or not email or not password:
                        st.error("Please fill in all fields.")
                    else:
                        with st.spinner("Creating account..."):
                            ok, err = register(username, email, password)
                        if ok:
                            st.success("✅ Account created! Please login.")
                            st.session_state.auth_mode = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {err}")

        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center;'>
            <div style='font-size:0.75rem; color:#2E3A4A; margin-bottom:12px;'>POWERED BY</div>
            <div style='display:flex; justify-content:center; gap:16px; flex-wrap:wrap;'>
                <span style='font-size:0.78rem; color:#3A4A5A;'>⬡ LangGraph</span>
                <span style='font-size:0.78rem; color:#3A4A5A;'>◈ Gemini Vision</span>
                <span style='font-size:0.78rem; color:#3A4A5A;'>▣ OpenCV</span>
                <span style='font-size:0.78rem; color:#3A4A5A;'>⬢ FastAPI</span>
                <span style='font-size:0.78rem; color:#3A4A5A;'>◎ PostgreSQL</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# ════════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════════

# ── Top bar ───────────────────────────────────────────────────────────────────
col_logo, col_space, col_user = st.columns([1, 2, 1])
with col_logo:
    st.markdown("""
    <div style="font-family:'Space Mono',monospace; font-size:1.1rem;
                font-weight:700; color:#2E86AB; padding-top:8px;">
        ⬡ DocPipeline
    </div>""", unsafe_allow_html=True)
with col_user:
    cu1, cu2 = st.columns([2, 1])
    with cu1:
        st.markdown(f"""
        <div style="font-size:0.85rem; color:#5A6A7A; padding-top:10px; text-align:right;">
            👤 {st.session_state.username}
        </div>""", unsafe_allow_html=True)
    with cu2:
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()

st.markdown("<hr style='border-color:#1E2D40; margin:8px 0 24px 0;'>", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
stats = get_stats()
c1, c2, c3, c4 = st.columns(4)

# Calculate successful/failed from validation status
by_status = stats.get("by_validation_status", {})
successful = sum(v for k, v in by_status.items() if "Valid" in k or "Compliant" in k)
failed = sum(v for k, v in by_status.items() if "Valid" not in k and "Compliant" not in k)
doc_types_count = len(stats.get("by_type", {}) or {})

with c1:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-num">{stats.get("total_documents", 0)}</div>
        <div class="stat-label">Total Processed</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-num">{successful}</div>
        <div class="stat-label">Successful</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-num">{failed}</div>
        <div class="stat-label">Failed</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="stat-card">
        <div class="stat-num">{doc_types_count}</div>
        <div class="stat-label">Doc Types Seen</div>
    </div>""", unsafe_allow_html=True)


st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Main tabs ─────────────────────────────────────────────────────────────────
tab_process, tab_history, tab_agents = st.tabs([
    "🚀  Process Documents",
    "📚  History",
    "⚙️  Pipeline Info"
])

# ── PROCESS TAB ──────────────────────────────────────────────────────────────
with tab_process:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="section-title">Upload Documents</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} file(s) ready**")
            for f in uploaded_files:
                st.caption(f"📎 {f.name}")
            st.image(uploaded_files[0],
                     caption=f"Preview: {uploaded_files[0].name}",
                     use_container_width=True)
            if len(uploaded_files) > 1:
                st.caption(f"+ {len(uploaded_files) - 1} more file(s)")
            st.markdown("")
            run_btn = st.button("🚀 Run Pipeline", type="primary")
        else:
            st.markdown("""
            <div style='background:#0D1117; border:1px solid #1E2D40; border-radius:12px;
                        padding:24px; color:#5A6A7A; font-size:0.88rem; line-height:2;'>
                📌 <b style='color:#8899AA'>Supported:</b> Invoices · Receipts · Purchase Orders
                · Bank Statements · Resumes · Product Listings<br>
                🔁 <b style='color:#8899AA'>Flow:</b> Upload → Preprocess → OCR → Classify
                → Specialist → Validate → 💾 Save<br>
                💡 <b style='color:#8899AA'>Tip:</b> Upload multiple files at once!
            </div>
            """, unsafe_allow_html=True)
            run_btn = False

    with col2:
        st.markdown('<div class="section-title">Pipeline Execution</div>', unsafe_allow_html=True)

        if uploaded_files and run_btn:
            total   = len(uploaded_files)
            results = []
            progress_bar = st.progress(0)
            status_text  = st.empty()

            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"⏳ Processing {uploaded_file.name} ({i+1}/{total})...")
                result, err = process_document(uploaded_file.getvalue(), uploaded_file.name)
                if result:
                    result["_filename"] = uploaded_file.name
                    result["_success"]  = True
                else:
                    result = {"_filename": uploaded_file.name, "_success": False, "_error": err}
                results.append(result)
                progress_bar.progress((i + 1) / total)

            progress_bar.progress(1.0)
            successful = sum(1 for r in results if r.get("_success"))
            status_text.markdown(f"✅ **Done! {successful}/{total} processed — saved to database**")

            st.markdown("")
            mc1, mc2, mc3 = st.columns(3)
            with mc1: st.metric("Total", total)
            with mc2: st.metric("✅ Success", successful)
            with mc3: st.metric("❌ Failed", total - successful)

            if successful > 0:
                st.markdown("")
                type_counts = Counter(
                    r.get("document_type", "unknown")
                    for r in results if r.get("_success")
                )
                tcols = st.columns(len(type_counts))
                for idx, (doc_type, count) in enumerate(type_counts.items()):
                    with tcols[idx]:
                        st.metric(doc_type.replace("_", " ").title(), count)

            st.markdown("")
            for i, result in enumerate(results):
                filename = result.get("_filename", f"Document {i+1}")
                success  = result.get("_success", False)
                doc_type = result.get("document_type", "unknown")

                with st.expander(
                    f"{'✅' if success else '❌'}  {filename}  —  {doc_type.upper().replace('_', ' ')}",
                    expanded=(i == 0)
                ):
                    if not success:
                        st.error(f"Error: {result.get('_error', 'Unknown')}")
                        continue

                    ra, rb, rc = st.columns(3)
                    with ra: st.metric("Type", doc_type.replace("_", " ").title())
                    with rb: st.metric("Validation", result.get("validation_status", "—"))
                    with rc: st.metric("Saved", "✅ Yes")

                    t1, t2 = st.tabs(["JSON Output", "Extracted Text"])
                    with t1:
                        vj = result.get("validated_json")
                        st.json(vj if vj else result.get("raw_json_output", {}))
                    with t2:
                        st.text(result.get("extracted_text", "No text extracted"))

        elif not uploaded_files:
            st.info("⬅️ Upload documents to start.")

# ── HISTORY TAB ──────────────────────────────────────────────────────────────
with tab_history:
    hc1, hc2 = st.columns([3, 1])
    with hc1:
        st.markdown('<div class="section-title">Previously Processed Documents</div>', unsafe_allow_html=True)
    with hc2:
        if st.button("🔄 Refresh"):
            st.rerun()

    history = get_document_history()

    if not history:
        st.info("No documents yet. Process some to see them here!")
    else:
        st.markdown(f"**{len(history)} document(s) in database**")
        st.markdown("")
        for doc in history:
            doc_type = doc.get("document_type", "unknown")
            filename = doc.get("filename", "Unknown")
            status   = doc.get("validation_status", "unknown")
            created  = doc.get("created_at", "")[:19].replace("T", " ") if doc.get("created_at") else ""

            with st.expander(f"📄  {filename}  —  {doc_type.upper().replace('_', ' ')}  —  {created}"):
                da, db, dc = st.columns(3)
                with da: st.metric("Type", doc_type.replace("_", " ").title())
                with db: st.metric("Status", status)
                with dc: st.metric("ID", doc.get("id", "—"))

                result_json = doc.get("result_json")
                if result_json:
                    st.markdown("**Extracted JSON:**")
                    if isinstance(result_json, str):
                        try: st.json(json.loads(result_json))
                        except: st.code(result_json, language="json")
                    else:
                        st.json(result_json)

# ── AGENTS TAB ────────────────────────────────────────────────────────────────
with tab_agents:
    st.markdown('<div class="section-title">Pipeline Architecture</div>', unsafe_allow_html=True)

    agents = [
        ("🔧", "Preprocessor",       "OpenCV",        "Grayscale → Denoise → CLAHE → Deskew"),
        ("👁",  "Extractor",          "Gemini Vision", "OCR — extracts raw text from image"),
        ("🏷",  "Classifier",         "Gemini Flash",  "Identifies document type"),
        ("🔀", "Router",             "LangGraph",     "Routes to correct specialist agent"),
        ("🤖", "JSON Specialist",    "Gemini Flash",  "Extracts invoice / product JSON"),
        ("🧾", "Receipt Specialist",  "Gemini Flash",  "Extracts receipt structured data"),
        ("📦", "PO Specialist",      "Gemini Flash",  "Extracts purchase order data"),
        ("🏦", "Bank Specialist",    "Gemini Flash",  "Extracts bank statement data"),
        ("📄", "Resume Specialist",  "Gemini Flash",  "Extracts resume / CV data"),
        ("✔",  "Validator",          "jsonschema",    "Validates output against schema"),
    ]

    ac1, ac2 = st.columns(2)
    for i, (icon, name, tech, desc) in enumerate(agents):
        with (ac1 if i % 2 == 0 else ac2):
            st.markdown(f"""
            <div style='background:#0D1117; border:1px solid #1E2D40; border-radius:10px;
                        padding:16px 20px; margin-bottom:10px;'>
                <div style='display:flex; align-items:center; gap:10px; margin-bottom:6px;'>
                    <span style='font-size:1.2rem;'>{icon}</span>
                    <span style='font-weight:600; color:#E0E0E0; font-size:0.95rem;'>{name}</span>
                    <span style='margin-left:auto; font-size:0.72rem; color:#2E86AB;
                                 background:rgba(46,134,171,0.1); border:1px solid rgba(46,134,171,0.2);
                                 padding:2px 8px; border-radius:4px; font-family:monospace;'>{tech}</span>
                </div>
                <div style='font-size:0.82rem; color:#5A6A7A;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Supported Document Types</div>', unsafe_allow_html=True)
    doc_types = [
        ("🧾", "Invoice"), ("🛒", "Receipt"), ("📦", "Purchase Order"),
        ("🏦", "Bank Statement"), ("📄", "Resume / CV"), ("🏷", "Product Listing"),
    ]
    dtcols = st.columns(6)
    for i, (icon, label) in enumerate(doc_types):
        with dtcols[i]:
            st.markdown(f"""
            <div style='background:#0D1117; border:1px solid #1E2D40; border-radius:10px;
                        padding:16px 12px; text-align:center;'>
                <div style='font-size:1.5rem;'>{icon}</div>
                <div style='font-size:0.78rem; color:#8899AA; margin-top:6px;'>{label}</div>
            </div>
            """, unsafe_allow_html=True)