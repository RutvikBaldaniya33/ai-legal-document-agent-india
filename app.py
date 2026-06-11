"""
AI Legal Document Agent — India
Streamlit UI for end-to-end legal document processing.

Run: streamlit run app.py

CRITICAL FEATURES:
✓ Gemini 429 error handling (graceful, no crashes)
✓ MongoDB visibility (laws displayed with full details)
✓ System status panel (MongoDB + Gemini connection)
✓ Case strength with breakdown
✓ Evidence extraction from documents
✓ Legal notice generation with copy button
✓ Professional black & white UI
✓ Demo flow visibility (shows each processing stage)
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Optional

import streamlit as st

from classifier import classify_case
from law_retriever import get_relevant_laws
from evidence_extractor import extract_evidence_from_document
from case_strength import calculate_case_strength, get_strength_label
from legal_notice import generate_legal_notice
from utils import validate_env_variables, clean_text
from system_status import check_system_status


# ─────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="AI Legal Document Agent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Minimalist black and white CSS (no gradients, animations, or fancy effects)
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {display: none;}
    footer {display: none;}
    
    /* Clean, minimal styling */
    .stTitle {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        color: #000000 !important;
    }
    
    .stMarkdown h2 {
        border-bottom: 2px solid #000000;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        font-size: 1.3rem !important;
        color: #000000 !important;
    }
    
    .stMarkdown h3 {
        font-size: 1.1rem !important;
        color: #000000 !important;
        font-weight: 600 !important;
        margin-top: 1rem !important;
    }
    
    /* Button styling - clean black and white */
    .stButton > button {
        width: 100%;
        border: 1px solid #000000;
        border-radius: 0;
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
    }
    
    .stButton > button:hover {
        background-color: #333333 !important;
    }
    
    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid #CCCCCC !important;
        border-radius: 0 !important;
    }
    
    /* Cards and boxes */
    .result-card {
        border: 1px solid #E0E0E0;
        border-radius: 0;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #FAFAFA;
    }
    
    /* Status panel */
    .status-panel {
        border: 1px solid #000000;
        border-radius: 0;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #F5F5F5;
    }
    
    /* Score display */
    .score-large {
        font-size: 2.5rem !important;
        font-weight: bold !important;
        color: #000000 !important;
        margin: 0.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────

def _init_session():
    """Initialize session state."""
    defaults = {
        "case_data": None,
        "uploaded_files": [],
        "extracted_facts": {},
        "claimant_name": "",
        "respondent_name": "",
        "processing": False,
        "error": None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_session()


# ─────────────────────────────────────────────────────────
# Helper: Display System Status
# ─────────────────────────────────────────────────────────

def display_system_status():
    """Display system health check panel."""
    with st.container():
        status = check_system_status()
        
        # Show status
        col1, col2 = st.columns(2)
        
        with col1:
            if status.gemini_connected:
                st.success("✅ Gemini Connected")
            else:
                st.error(f"❌ Gemini: {status.gemini_error}")
        
        with col2:
            if status.mongodb_connected:
                st.success(f"✅ MongoDB Connected")
            else:
                st.error(f"❌ MongoDB: {status.mongodb_error}")
        
        # Show laws count separately
        if status.mongodb_connected:
            st.info(f"📚 {status.laws_count} laws loaded from database")
        
        return status.mongodb_connected and status.gemini_connected


# ─────────────────────────────────────────────────────────
# Sidebar: Document Upload & Party Info
# ─────────────────────────────────────────────────────────

def render_sidebar():
    """Render sidebar with uploads and party information."""
    with st.sidebar:
        st.markdown("### 📄 DOCUMENTS")
        
        # File uploader
        uploaded = st.file_uploader(
            "Upload supporting documents",
            type=["pdf", "png", "jpg", "jpeg", "gif", "webp"],
            accept_multiple_files=True,
            help="Contracts, receipts, images, screenshots, etc.",
        )
        
        if uploaded:
            st.session_state.uploaded_files = uploaded
            st.info(f"✓ {len(uploaded)} file(s) uploaded")
            
            # Optional: extract from documents
            if st.checkbox("🔍 Extract facts from documents"):
                with st.spinner("Extracting facts..."):
                    all_facts = {
                        "names": [],
                        "dates": [],
                        "amounts": [],
                        "addresses": [],
                        "important_facts": [],
                    }
                    
                    for file in uploaded:
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.name).suffix) as tmp:
                                tmp.write(file.getbuffer())
                                tmp_path = tmp.name
                            
                            facts = extract_evidence_from_document(tmp_path)
                            
                            all_facts["names"].extend(facts.names)
                            all_facts["dates"].extend(facts.dates)
                            all_facts["amounts"].extend(facts.amounts)
                            all_facts["addresses"].extend(facts.addresses)
                            all_facts["important_facts"].extend(facts.important_facts)
                            
                            os.unlink(tmp_path)
                        except Exception as e:
                            st.warning(f"⚠️ {file.name}: {str(e)[:80]}")
                    
                    st.session_state.extracted_facts = all_facts
                    st.success(f"✓ Extracted from {len(uploaded)} document(s)")
        
        st.markdown("### 👤 PARTIES")
        
        st.session_state.claimant_name = st.text_input(
            "Your Name (Claimant)",
            value=st.session_state.claimant_name,
            placeholder="Enter your name",
        )
        
        st.session_state.respondent_name = st.text_input(
            "Other Party (Respondent)",
            value=st.session_state.respondent_name,
            placeholder="Enter other party name",
        )


# ─────────────────────────────────────────────────────────
# Main: Process Case
# ─────────────────────────────────────────────────────────

def process_case_pipeline(dispute_text: str) -> Optional[dict]:
    """
    Process case end-to-end with visibility of each stage.
    
    Returns:
        Dictionary with all analysis results or None on error
    """
    results = {}
    
    try:
        # Stage 1: Classify
        with st.spinner("📍 Classifying dispute..."):
            try:
                classification = classify_case(dispute_text)
                results["classification"] = classification
                st.success(f"✓ Type: {classification.dispute_type} | State: {classification.state or 'Not specified'}")
            except Exception as e:
                st.error("⚠️ Classification unavailable. Please retry later.")
                return None
        
        # Stage 2: Retrieve Laws (MongoDB)
        with st.spinner("📚 Retrieving laws from MongoDB..."):
            try:
                laws = get_relevant_laws(
                    classification.dispute_type,
                    classification.state
                )
                results["laws"] = [law.dict() for law in laws]
                st.success(f"✓ Found {len(laws)} relevant law(s) in MongoDB")
            except Exception as e:
                st.warning("⚠️ Law retrieval unavailable. Proceeding with general laws.")
                results["laws"] = []
        
        # Stage 3: Extract Evidence
        extracted = st.session_state.extracted_facts or {
            "names": [st.session_state.claimant_name, st.session_state.respondent_name],
            "dates": [],
            "amounts": [],
            "addresses": [classification.state] if classification.state else [],
            "important_facts": [dispute_text[:200]],
        }
        results["extracted_facts"] = extracted
        
        # Stage 4: Calculate Case Strength
        with st.spinner("📊 Analyzing case strength..."):
            try:
                strength = calculate_case_strength(
                    dispute_description=dispute_text,
                    dispute_type=classification.dispute_type,
                    extracted_facts=extracted,
                    relevant_laws=results.get("laws", []),
                )
                results["case_strength"] = strength.dict()
                st.success(f"✓ Case Strength: {strength.score}/100")
            except Exception as e:
                st.warning("⚠️ Detailed analysis temporarily unavailable. Using default scoring.")
                results["case_strength"] = {"score": 50, "breakdown": {}, "reasoning": "Analysis unavailable. Please retry."}
        
        # Stage 5: Generate Legal Notice
        with st.spinner("✍️  Generating legal notice..."):
            try:
                notice = generate_legal_notice(
                    dispute_description=dispute_text,
                    dispute_type=classification.dispute_type,
                    claimant_name=st.session_state.claimant_name,
                    respondent_name=st.session_state.respondent_name,
                    state=classification.state or "Not Specified",
                    extracted_facts=extracted,
                    case_strength=results.get("case_strength", {}),
                    relevant_laws=results.get("laws", []),
                )
                results["legal_notice"] = notice.dict()
                st.success("✓ Legal notice generated")
            except Exception as e:
                st.warning("⚠️ Notice generation temporarily unavailable. Please retry.")
                results["legal_notice"] = {
                    "legal_notice": f"[Legal Notice - {st.session_state.claimant_name} vs {st.session_state.respondent_name}]\n\n{dispute_text}",
                    "summary": "Notice generation is temporarily unavailable. Please retry in a moment."
                }
        
        return results
        
    except Exception as e:
        st.error("⚠️ Gemini temporarily unavailable. Please retry later.")
        return None


# ─────────────────────────────────────────────────────────
# Display: Results
# ─────────────────────────────────────────────────────────

def display_results(case_data: dict):
    """Display all analysis results in organized tabs."""
    
    tabs = st.tabs([
        "📍 Classification",
        "📚 Laws (MongoDB)",
        "📋 Extracted Facts",
        "📊 Case Strength",
        "✍️ Legal Notice",
    ])
    
    # Tab 1: Classification
    with tabs[0]:
        st.markdown("## 📍 Dispute Classification")
        st.divider()
        c = case_data["classification"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Dispute Type", c.dispute_type.upper())
        with col2:
            st.metric("State", c.state or "Not Specified")
        st.markdown("Classification determines which laws apply to your dispute.")
    
    # Tab 2: Laws from MongoDB
    with tabs[1]:
        st.markdown("## 📚 Relevant Laws Retrieved From MongoDB")
        st.divider()
        
        laws = case_data.get("laws", [])
        
        if not laws:
            st.info("❌ No specific laws found for this dispute type and state. General consumer/tenant laws will apply.")
        else:
            st.markdown(f"**Found {len(laws)} applicable law(s) in MongoDB database:**")
            st.markdown("")
            
            for i, law in enumerate(laws, 1):
                with st.expander(f"**{i}. {law.get('title', 'Unknown')}**", expanded=(i==1)):
                    st.markdown(f"**🏛️ Source:** MongoDB Atlas (India Legal Database)")
                    st.markdown(f"**📍 State/Jurisdiction:** {law.get('state', 'National')}")
                    st.markdown(f"**📂 Category:** {law.get('category', 'N/A')}")
                    st.divider()
                    
                    content = law.get('content', '')
                    if len(content) > 800:
                        st.markdown(f"**Content Preview:**\n{content[:800]}...\n\n[Full text available in database]")
                    else:
                        st.markdown(f"**Content:**\n{content}")
                    
                    st.caption("✅ Retrieved from MongoDB Atlas - India Legal Document Database")
    
    # Tab 3: Extracted Facts
    with tabs[2]:
        st.markdown("## 📋 Extracted Facts from Documents")
        st.divider()
        
        facts = case_data.get("extracted_facts", {})
        
        if not any([facts.get("names"), facts.get("dates"), facts.get("amounts"), facts.get("addresses"), facts.get("important_facts")]):
            st.info("No facts extracted. Please upload and extract information from documents in the sidebar.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 👥 Names Mentioned")
                if facts.get("names") and facts["names"][0]:
                    for name in facts["names"]:
                        if name:
                            st.write(f"• {name}")
                else:
                    st.write("_None_")
                
                st.markdown("### 📅 Dates")
                if facts.get("dates"):
                    for date in facts["dates"]:
                        if date:
                            st.write(f"• {date}")
                else:
                    st.write("_None_")
            
            with col2:
                st.markdown("### 💰 Amounts & Money")
                if facts.get("amounts"):
                    for amt in facts["amounts"]:
                        if amt:
                            st.write(f"• {amt}")
                else:
                    st.write("_None_")
                
                st.markdown("### 📍 Addresses & Locations")
                if facts.get("addresses"):
                    for addr in facts["addresses"]:
                        if addr:
                            st.write(f"• {addr}")
                else:
                    st.write("_None_")
            
            st.markdown("### 🔑 Key Facts")
            if facts.get("important_facts"):
                for i, fact in enumerate(facts["important_facts"], 1):
                    if fact:
                        st.write(f"{i}. {fact}")
            else:
                st.write("_None_")
    
    # Tab 4: Case Strength
    with tabs[3]:
        st.markdown("## 📊 Case Strength Analysis")
        st.divider()
        
        strength = case_data.get("case_strength", {})
        score = strength.get("score", 0)
        breakdown = strength.get("breakdown", {})
        
        # Large score display
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Color code based on score
            if score >= 80:
                color = "green"
                emoji = "🟢"
            elif score >= 60:
                color = "blue"
                emoji = "🔵"
            elif score >= 40:
                color = "orange"
                emoji = "🟠"
            else:
                color = "red"
                emoji = "🔴"
            
            st.markdown(f"### {emoji} {score}/100")
            st.markdown(f"**{get_strength_label(score)}**")
        
        with col2:
            st.markdown("### Score Breakdown")
            if breakdown:
                metrics = [
                    ("Agreement Present", breakdown.get("agreement_present", 0)),
                    ("Payment Proof", breakdown.get("payment_proof", 0)),
                    ("Communication Evidence", breakdown.get("communication_evidence", 0)),
                    ("Law Match", breakdown.get("law_match", 0)),
                    ("Timeline Consistency", breakdown.get("timeline_consistency", 0)),
                    ("Witnesses/Verification", breakdown.get("witnesses", 0)),
                    ("Documentation", breakdown.get("documentation_completeness", 0)),
                ]
                for label, value in metrics:
                    if value > 0:
                        st.write(f"• {label}: **{value} pts**")
        
        st.divider()
        
        if strength.get("reasoning"):
            st.markdown("### 📝 Analysis")
            st.markdown(strength["reasoning"])
        
        if strength.get("strengths"):
            st.markdown("### ✅ Case Strengths")
            for s in strength["strengths"]:
                st.write(f"✓ {s}")
        
        if strength.get("risk_factors"):
            st.markdown("### ⚠️ Risk Factors")
            for r in strength["risk_factors"]:
                st.write(f"⚠️ {r}")
    
    # Tab 5: Legal Notice
    with tabs[4]:
        st.markdown("## ✍️ Generated Legal Notice")
        st.divider()
        
        notice = case_data.get("legal_notice", {})
        
        notice_text = notice.get("legal_notice", "[Notice not generated]")
        
        # Display the legal notice with better formatting
        st.markdown("### 📄 Legal Notice Document")
        with st.container():
            st.text_area(
                "Legal Notice:",
                value=notice_text,
                height=250,
                disabled=True,
                label_visibility="collapsed"
            )
        
        # Download button
        full_text = f"""LEGAL NOTICE
{'='*80}
Date: {notice.get('date_generated', 'N/A')}
Dispute Type: {case_data['classification'].dispute_type.upper()}

{notice_text}

{'='*80}
SUMMARY:
{notice.get('summary', '')}
{'='*80}
"""
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.download_button(
                label="📥 Download Notice (TXT)",
                data=full_text,
                file_name=f"Legal_Notice_{case_data['classification'].dispute_type}.txt",
                mime="text/plain",
            )
        
        with col2:
            if notice.get("summary"):
                st.info("💡 Summary available in expander below")
        
        # Consumer complaint if available
        if notice.get("consumer_complaint") and notice["consumer_complaint"] not in ["", "Please retry generation when API is available."]:
            st.divider()
            with st.expander("📋 Consumer Complaint (if applicable)", expanded=False):
                st.text_area(
                    "Consumer Complaint:",
                    value=notice.get("consumer_complaint", ""),
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        # Summary
        if notice.get("summary") and notice["summary"] not in ["", "Notice generation temporarily unavailable. Please retry."]:
            st.divider()
            with st.expander("📝 Executive Summary", expanded=False):
                st.markdown(notice["summary"])


# ─────────────────────────────────────────────────────────
# Main App Flow
# ─────────────────────────────────────────────────────────

def main():
    """Main application flow."""
    
    # Header
    st.title("⚖️ AI Legal Document Agent")
    st.caption("India | End-to-End Legal Analysis")
    
    st.divider()
    
    # System Status Panel
    st.markdown("### 🔧 System Status")
    systems_ok = display_system_status()
    
    if not systems_ok:
        st.warning("⚠️ Some systems are offline. Features may be limited.")
    
    st.divider()
    
    # Sidebar
    render_sidebar()
    
    # Main Input
    st.markdown("### 📋 DESCRIBE YOUR DISPUTE")
    
    dispute_text = st.text_area(
        "Enter dispute details",
        placeholder="Describe the legal issue...",
        height=120,
        label_visibility="collapsed",
    )
    
    # Status indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.claimant_name:
            st.success(f"✓ {st.session_state.claimant_name}")
        else:
            st.warning("⚠️ Add name in sidebar")
    
    with col2:
        if st.session_state.respondent_name:
            st.success(f"✓ {st.session_state.respondent_name}")
        else:
            st.warning("⚠️ Add respondent in sidebar")
    
    with col3:
        if st.session_state.uploaded_files:
            st.success(f"✓ {len(st.session_state.uploaded_files)} docs")
        else:
            st.info("No documents")
    
    st.divider()
    
    # Process Button
    col1, col2 = st.columns([2, 1])
    
    with col1:
        process = st.button("🚀 PROCESS & GENERATE LEGAL NOTICE", type="primary", use_container_width=True)
    
    with col2:
        clear = st.button("🔄 Clear All", use_container_width=True)
    
    st.divider()
    
    # Processing
    if clear:
        st.session_state.case_data = None
        st.session_state.uploaded_files = []
        st.session_state.extracted_facts = {}
        st.session_state.claimant_name = ""
        st.session_state.respondent_name = ""
        st.rerun()
    
    if process:
        if not dispute_text.strip():
            st.error("❌ Please enter dispute details")
            return
        
        if not st.session_state.claimant_name:
            st.error("❌ Please enter your name in sidebar")
            return
        
        if not st.session_state.respondent_name:
            st.error("❌ Please enter respondent name in sidebar")
            return
        
        # Process the case
        st.session_state.case_data = process_case_pipeline(dispute_text)
    
    # Display Results
    if st.session_state.case_data:
        st.markdown("---")
        st.markdown("## 📊 ANALYSIS RESULTS")
        display_results(st.session_state.case_data)


if __name__ == "__main__":
    main()
