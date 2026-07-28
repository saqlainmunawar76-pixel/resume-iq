"""
ResumeIQ — AI-Powered Resume Feedback Tool (Capstone Project)
Generative AI & Prompt Engineering Internship — NeuroFive Solutions

Features:
1. Resume Feedback & Scoring (structured JSON output)
2. Job Description Match Analysis
3. Improved Resume Generation + PDF Download
4. Tailored Cover Letter Generation + Download
"""

import streamlit as st
import json
import io
from pypdf import PdfReader
from fpdf import FPDF
from google import genai
from google.genai import types

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(page_title="ResumeIQ | AI Resume Feedback", page_icon="🎯", layout="wide")

# ── Styling — Dashboard theme: deep navy + blue-violet accent ─────
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0B0E1A 0%, #131729 100%); }
    .main-title {
        font-size: 2.3rem; font-weight: 800; color: #F1F3FA !important;
        margin-bottom: 0;
    }
    .main-title span { color: #7C6FF0; }
    .subtitle { color: #8B92B0 !important; font-size: 0.95rem; margin-top: 2px; margin-bottom: 1.5rem; }

    .score-card {
        background: linear-gradient(135deg, #1A1F3A 0%, #1E2340 100%);
        border: 1px solid #2E3358; border-radius: 14px; padding: 28px 24px;
        text-align: center; margin-bottom: 16px;
    }
    .score-number { font-size: 3.2rem; font-weight: 800; color: #7C6FF0 !important; line-height: 1; }
    .score-label { color: #8B92B0 !important; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 6px; }

    .section-card {
        background: #161A30; border: 1px solid #2E3358; border-radius: 10px;
        padding: 16px 20px; margin-bottom: 12px;
    }
    .section-card-title { color: #F1F3FA !important; font-weight: 700; font-size: 1rem; margin-bottom: 4px; }
    .section-card-score { color: #7C6FF0 !important; font-weight: 700; font-size: 1.1rem; float: right; }
    .section-card-comment { color: #B4B9D4 !important; font-size: 0.9rem; margin-top: 6px; }

    .suggestion-item {
        background: #161A30; border-left: 3px solid #7C6FF0; border-radius: 6px;
        padding: 12px 16px; margin-bottom: 8px; color: #D9DCEE !important; font-size: 0.92rem;
    }
    .match-card {
        background: linear-gradient(135deg, #1A1F3A 0%, #1E2340 100%);
        border: 1px solid #2E3358; border-radius: 14px; padding: 24px; text-align: center;
    }
    .match-number { font-size: 2.8rem; font-weight: 800; line-height: 1; }
    .keyword-chip {
        display: inline-block; background: #2A2145; border: 1px solid #4A3D7A; color: #C9B8FF !important;
        border-radius: 20px; padding: 4px 14px; margin: 4px; font-size: 0.85rem;
    }
    .content-box {
        background: #161A30; border: 1px solid #2E3358; border-radius: 10px;
        padding: 20px 24px; color: #D9DCEE !important; font-size: 0.92rem; line-height: 1.7;
        white-space: pre-wrap;
    }

    section[data-testid="stSidebar"] { background: #0D0F1C !important; border-right: 1px solid #2E3358; }
    section[data-testid="stSidebar"] * { color: #D9DCEE !important; }
    section[data-testid="stSidebar"] h3 { color: #7C6FF0 !important; }

    .stButton button[kind="primary"] { background-color: #7C6FF0 !important; border: none !important; font-weight: 600 !important; }
    .stDownloadButton button { background-color: #1E2340 !important; color: #F1F3FA !important; border: 1px solid #4A3D7A !important; }
    [data-testid="stFileUploaderDropzone"] { background-color: #161A30 !important; border: 1.5px dashed #2E3358 !important; }
    [data-testid="stFileUploaderDropzone"] * { color: #B4B9D4 !important; }
    .stTextArea textarea { background-color: #161A30 !important; color: #D9DCEE !important; border: 1px solid #2E3358 !important; }
    [data-testid="stAlert"] { background-color: #161A30 !important; color: #D9DCEE !important; }
    [data-testid="stAlert"] * { color: #D9DCEE !important; }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Backend ────────────────────────────────────────────────────────
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.5-flash-lite"


def extract_text(file) -> str:
    reader = PdfReader(file)
    return "\n".join((page.extract_text() or "") for page in reader.pages)


FEEDBACK_SCHEMA = {
    "type": "object",
    "properties": {
        "overall_score": {"type": "integer"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "enum": ["Experience", "Skills", "Formatting", "Impact"]},
                    "score": {"type": "integer"},
                    "comment": {"type": "string"},
                },
                "required": ["name", "score", "comment"],
            },
        },
        "top_suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["overall_score", "sections", "top_suggestions"],
}

MATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "match_percentage": {"type": "integer"},
        "missing_keywords": {"type": "array", "items": {"type": "string"}},
        "tailoring_suggestions": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["match_percentage", "missing_keywords", "tailoring_suggestions"],
}


def get_feedback(resume_text: str) -> dict:
    prompt = f"""Analyze this resume and score it. Be honest and specific, not generic.

Resume:
{resume_text}"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an expert resume reviewer and career coach with 15 years of experience in tech recruiting. Score resumes honestly on a 0-100 scale across four dimensions: Experience (how well accomplishments are conveyed), Skills (relevance and clarity), Formatting (structure, scannability), and Impact (use of metrics, action verbs, results-oriented language). Give specific, actionable suggestions, not generic advice.",
            response_mime_type="application/json",
            response_schema=FEEDBACK_SCHEMA,
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return json.loads(response.text)


def get_match(resume_text: str, jd_text: str) -> dict:
    prompt = f"""Resume:
{resume_text}

Job Description:
{jd_text}"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an ATS (Applicant Tracking System) and recruiting expert. Compare the resume against the job description. Calculate a realistic match percentage, list specific important keywords/skills from the JD that are missing from the resume, and give concrete suggestions for tailoring the resume to this specific job.",
            response_mime_type="application/json",
            response_schema=MATCH_SCHEMA,
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return json.loads(response.text)


def get_improved_resume(resume_text: str, jd_text: str = "") -> str:
    context = f"\n\nTailor it toward this job description:\n{jd_text}" if jd_text else ""
    prompt = f"Rewrite and improve this resume. Keep the same factual content (don't invent experience), but strengthen bullet points with action verbs, quantify impact where plausible, and improve clarity and structure.{context}\n\nOriginal Resume:\n{resume_text}"
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a professional resume writer. Output ONLY the improved resume text, well-structured with clear section headers. No preamble, no explanation, just the resume content.",
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return response.text


def get_cover_letter(resume_text: str, jd_text: str = "") -> str:
    context = f"for this specific job:\n{jd_text}" if jd_text else "as a general, professional cover letter template"
    prompt = f"Write a compelling, concise cover letter (250-350 words) based on this resume, {context}\n\nResume:\n{resume_text}"
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a professional cover letter writer. Write in first person, confident but not arrogant tone. Output ONLY the cover letter text, no preamble.",
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return response.text


def text_to_pdf(text: str, title: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, title, ln=True)
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10.5)
    clean_text = text.encode("latin-1", "replace").decode("latin-1")
    for line in clean_text.split("\n"):
        pdf.multi_cell(0, 6, line)
    return bytes(pdf.output())


# ── Session state ──────────────────────────────────────────────────
for key in ["resume_text", "feedback", "match", "improved_resume", "cover_letter"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Sidebar ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 ResumeIQ")
    st.caption("AI-powered resume feedback, in seconds.")
    st.markdown("---")

    uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf")
    jd_text = st.text_area("Paste a job description (optional)", height=160, placeholder="Paste the job posting here to unlock JD match and tailored cover letter...")

    analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("Built for the **Generative AI & Prompt Engineering Internship** @ NeuroFive Solutions")

# ── Main ───────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🎯 Resume<span>IQ</span></p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload your resume for an honest, structured AI review — score, job match, an improved rewrite, and a ready-to-send cover letter.</p>', unsafe_allow_html=True)

if uploaded_file and analyze_clicked:
    st.session_state.resume_text = extract_text(io.BytesIO(uploaded_file.read()))
    with st.spinner("Scoring your resume..."):
        st.session_state.feedback = get_feedback(st.session_state.resume_text)
    if jd_text.strip():
        with st.spinner("Comparing against the job description..."):
            st.session_state.match = get_match(st.session_state.resume_text, jd_text)
    else:
        st.session_state.match = None
    st.session_state.improved_resume = None
    st.session_state.cover_letter = None

if st.session_state.resume_text:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Feedback & Score", "🎯 Job Match", "✨ Improved Resume", "✉️ Cover Letter"])

    # ── Tab 1: Feedback ──
    with tab1:
        fb = st.session_state.feedback
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f'<div class="score-card"><div class="score-number">{fb["overall_score"]}</div><div class="score-label">Overall Score / 100</div></div>', unsafe_allow_html=True)
        with col2:
            for s in fb["sections"]:
                st.markdown(f'<div class="section-card"><span class="section-card-title">{s["name"]}</span><span class="section-card-score">{s["score"]}/100</span><div class="section-card-comment">{s["comment"]}</div></div>', unsafe_allow_html=True)

        st.markdown("#### Top Suggestions")
        for sug in fb["top_suggestions"]:
            st.markdown(f'<div class="suggestion-item">{sug}</div>', unsafe_allow_html=True)

    # ── Tab 2: JD Match ──
    with tab2:
        if st.session_state.match:
            m = st.session_state.match
            pct = m["match_percentage"]
            color = "#5FD68A" if pct >= 70 else "#E8B84F" if pct >= 40 else "#E8615F"
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f'<div class="match-card"><div class="match-number" style="color:{color};">{pct}%</div><div class="score-label">Match Score</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown("**Missing Keywords / Skills**")
                st.markdown("".join(f'<span class="keyword-chip">{k}</span>' for k in m["missing_keywords"]), unsafe_allow_html=True)
            st.markdown("#### Tailoring Suggestions")
            for sug in m["tailoring_suggestions"]:
                st.markdown(f'<div class="suggestion-item">{sug}</div>', unsafe_allow_html=True)
        else:
            st.info("Paste a job description in the sidebar and re-analyze to see your match score.")

    # ── Tab 3: Improved Resume ──
    with tab3:
        if st.session_state.improved_resume is None:
            if st.button("Generate Improved Resume", type="primary"):
                with st.spinner("Rewriting your resume..."):
                    jd_for_improve = jd_text if jd_text.strip() else ""
                    st.session_state.improved_resume = get_improved_resume(st.session_state.resume_text, jd_for_improve)
                st.rerun()
        else:
            st.markdown(f'<div class="content-box">{st.session_state.improved_resume}</div>', unsafe_allow_html=True)
            pdf_bytes = text_to_pdf(st.session_state.improved_resume, "Improved Resume")
            st.download_button("⬇ Download Improved Resume (PDF)", data=pdf_bytes, file_name="improved_resume.pdf", mime="application/pdf")

    # ── Tab 4: Cover Letter ──
    with tab4:
        if st.session_state.cover_letter is None:
            if st.button("Generate Cover Letter", type="primary"):
                with st.spinner("Writing your cover letter..."):
                    jd_for_letter = jd_text if jd_text.strip() else ""
                    st.session_state.cover_letter = get_cover_letter(st.session_state.resume_text, jd_for_letter)
                st.rerun()
        else:
            st.markdown(f'<div class="content-box">{st.session_state.cover_letter}</div>', unsafe_allow_html=True)
            pdf_bytes = text_to_pdf(st.session_state.cover_letter, "Cover Letter")
            st.download_button("⬇ Download Cover Letter (PDF)", data=pdf_bytes, file_name="cover_letter.pdf", mime="application/pdf")

else:
    st.info("👈 Upload your resume in the sidebar and click 'Analyze Resume' to get started.")
