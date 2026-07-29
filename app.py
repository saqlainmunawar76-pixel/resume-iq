"""
ResumeIQ — AI-Powered Resume Feedback Tool (Capstone Project)
Generative AI & Prompt Engineering Internship — NeuroFive Solutions

A professional dashboard-style resume analysis tool:
1. Dashboard — score rings, radar chart, strengths/gaps, skills found/missing
2. Job Match — match % against a pasted job description
3. Improved Resume — AI rewrite + PDF download
4. Cover Letter — tailored cover letter + PDF download
"""

import streamlit as st
import json
import io
import plotly.graph_objects as go
from pypdf import PdfReader
from fpdf import FPDF
from google import genai
from google.genai import types

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(page_title="ResumeIQ | AI Resume Feedback", page_icon="🎯", layout="wide")

# ── Styling — Dashboard theme: deep navy + blue-violet accent ─────
st.markdown("""
<style>
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background: #0B0E1A !important;
    }
    .stApp * { color: #D9DCEE; }
    * { font-family: 'Inter', -apple-system, sans-serif; }

    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 14px 4px 18px 4px; border-bottom: 1px solid #1F2440; margin-bottom: 22px;
    }
    .nav-links { display: flex; gap: 28px; }
    .nav-links span { color: #A6ACC7; font-size: 0.92rem; font-weight: 500; cursor: default; }

    /* Hide the unused native Streamlit sidebar toggle */
    [data-testid="collapsedControl"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }

    .hero-title {
        text-align: center; font-size: 2.6rem; font-weight: 800; color: #F1F3FA;
        margin: 30px 0 10px 0; line-height: 1.15;
    }
    .hero-title span {
        background: linear-gradient(90deg, #6D5AE6, #8FC2FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-sub {
        text-align: center; color: #8B92B0; font-size: 1rem; max-width: 620px;
        margin: 0 auto 34px auto; line-height: 1.6;
    }
    .upload-card {
        background: #12162A; border: 1.5px dashed #2E3358; border-radius: 18px;
        padding: 30px 30px 10px 30px; margin-bottom: 30px;
    }
    .brand { font-size: 1.4rem; font-weight: 800; color: #F1F3FA; }
    .brand span { color: #8B7CF6; }
    .brand-sub { color: #6B7290; font-size: 0.78rem; margin-top: -2px; }
    .greeting { font-size: 1.6rem; font-weight: 800; color: #F1F3FA; margin-bottom: 2px; }
    .greeting-sub { color: #8B92B0; font-size: 0.92rem; margin-bottom: 22px; }

    /* KPI ring cards */
    .kpi-card {
        background: #12162A; border: 1px solid #1F2440; border-radius: 16px;
        padding: 20px 10px 16px 10px; text-align: center; margin-bottom: 14px;
    }
    .kpi-title { color: #A6ACC7; font-size: 0.85rem; font-weight: 600; margin-bottom: 12px; }
    .kpi-caption { color: #6B7290; font-size: 0.78rem; margin-top: 8px; }
    .ring-wrap { display: flex; justify-content: center; }
    .ring {
        width: 108px; height: 108px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
    }
    .ring-inner {
        width: 82px; height: 82px; border-radius: 50%; background: #12162A;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .ring-number { font-size: 1.5rem; font-weight: 800; color: #F1F3FA; line-height: 1; }
    .ring-max { font-size: 0.65rem; color: #6B7290; }

    /* Panels */
    .panel {
        background: #12162A; border: 1px solid #1F2440; border-radius: 16px;
        padding: 20px 22px; margin-bottom: 14px; height: 100%;
    }
    .panel-title { color: #F1F3FA; font-weight: 700; font-size: 1.02rem; margin-bottom: 14px; }
    .summary-text { color: #B4B9D4; font-size: 0.9rem; line-height: 1.6; margin-bottom: 14px; }
    .callout { display: flex; gap: 10px; margin-bottom: 12px; align-items: flex-start; }
    .callout-icon { font-size: 1rem; margin-top: 1px; }
    .callout-label { color: #F1F3FA; font-weight: 700; font-size: 0.88rem; }
    .callout-text { color: #9BA1C0; font-size: 0.85rem; }

    .list-item { color: #C3C8E0; font-size: 0.87rem; margin-bottom: 8px; display: flex; gap: 8px; }
    .list-item.good::before { content: "✓"; color: #5FD68A; font-weight: 700; }
    .list-item.warn::before { content: "•"; color: #E8B84F; font-weight: 700; }

    .chip { display: inline-block; border-radius: 20px; padding: 5px 14px; margin: 4px 4px 0 0; font-size: 0.82rem; }
    .chip-found { background: #14213A; border: 1px solid #2A3F63; color: #8FC2FF; }
    .chip-missing { background: #2E1620; border: 1px solid #5C2A38; color: #FF9CA8; }

    .cta-banner {
        background: linear-gradient(90deg, #6D5AE6 0%, #8B7CF6 100%);
        border-radius: 16px; padding: 22px 26px; display: flex; align-items: center;
        justify-content: space-between; margin-top: 6px;
    }
    .cta-title { color: #FFFFFF; font-weight: 700; font-size: 1.05rem; }
    .cta-sub { color: #E4DFFF; font-size: 0.85rem; margin-top: 2px; }

    .match-hero {
        background: #12162A; border: 1px solid #1F2440; border-radius: 16px;
        padding: 30px; text-align: center;
    }
    .match-number { font-size: 3rem; font-weight: 800; line-height: 1; }
    .content-box {
        background: #12162A; border: 1px solid #1F2440; border-radius: 14px;
        padding: 22px 26px; color: #D9DCEE; font-size: 0.92rem; line-height: 1.75; white-space: pre-wrap;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: #12162A !important; border: 1px solid #1F2440 !important; border-radius: 14px !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] strong {
        color: #E4E7F5 !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] h3 {
        color: #F1F3FA !important;
    }

    section[data-testid="stSidebar"] { background: #0D0F1C !important; border-right: 1px solid #1F2440; }
    section[data-testid="stSidebar"] * { color: #D9DCEE !important; }
    section[data-testid="stSidebar"] h3 { color: #8B7CF6 !important; }
    .stButton button[kind="primary"] { background-color: #6D5AE6 !important; border: none !important; color: #FFFFFF !important; font-weight: 600 !important; }
    .stButton button[kind="secondary"] {
        background-color: #12162A !important; border: 1px solid #2E3358 !important; color: #D9DCEE !important;
    }
    .stButton button[kind="secondary"]:hover { border-color: #6D5AE6 !important; color: #F1F3FA !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent !important; border-bottom: 1px solid #1F2440 !important; }
    .stTabs [data-baseweb="tab"] { color: #8B92B0 !important; background-color: transparent !important; }
    .stTabs [aria-selected="true"] { color: #8B7CF6 !important; }
    .stDownloadButton button { background-color: #1A1F3A !important; color: #F1F3FA !important; border: 1px solid #2E3358 !important; }
    [data-testid="stFileUploaderDropzone"] { background-color: #12162A !important; border: 1.5px dashed #2E3358 !important; }
    [data-testid="stFileUploaderDropzone"] * { color: #B4B9D4 !important; }
    .stTextArea textarea { background-color: #12162A !important; color: #D9DCEE !important; border: 1px solid #2E3358 !important; }
    [data-testid="stAlert"] { background-color: #12162A !important; color: #D9DCEE !important; }
    [data-testid="stAlert"] * { color: #D9DCEE !important; }
    [data-testid="stChatMessage"] { background-color: #12162A !important; border: 1px solid #1F2440 !important; border-radius: 12px !important; }
    [data-testid="stChatMessage"] * { color: #D9DCEE !important; }
    [data-testid="stChatInput"] textarea { background-color: #12162A !important; color: #D9DCEE !important; }
    [data-testid="stChatInput"] { background-color: #0B0E1A !important; border: 1px solid #2E3358 !important; }

    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def ring_color(score: int) -> str:
    if score >= 75:
        return "#5FD68A"
    if score >= 50:
        return "#E8B84F"
    return "#E8615F"


def ring_html(label: str, score: int, caption: str = "") -> str:
    color = ring_color(score)
    pct = max(0, min(score, 100))
    return f'''
    <div class="kpi-card">
        <div class="kpi-title">{label}</div>
        <div class="ring-wrap">
            <div class="ring" style="background: conic-gradient({color} {pct * 3.6}deg, #1F2440 0deg);">
                <div class="ring-inner">
                    <div class="ring-number">{score}</div>
                    <div class="ring-max">/100</div>
                </div>
            </div>
        </div>
        <div class="kpi-caption">{caption}</div>
    </div>
    '''


def radar_chart(sections: list[dict]):
    labels = [s["name"] for s in sections]
    values = [s["score"] for s in sections]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=labels + [labels[0]],
        fill="toself", fillcolor="rgba(139,124,246,0.25)",
        line=dict(color="#8B7CF6", width=2), marker=dict(color="#8B7CF6", size=6),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2E3358", tickfont=dict(color="#6B7290", size=9)),
            angularaxis=dict(gridcolor="#2E3358", tickfont=dict(color="#B4B9D4", size=11)),
        ),
        showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20), height=320,
    )
    return fig


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
        "summary": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "areas_to_improve": {"type": "array", "items": {"type": "string"}},
        "top_suggestion": {"type": "string"},
        "skills_found": {"type": "array", "items": {"type": "string"}},
        "missing_skills": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["overall_score", "sections", "summary", "strengths", "areas_to_improve", "top_suggestion", "skills_found", "missing_skills"],
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
    prompt = f"Analyze this resume and score it. Be honest and specific, not generic.\n\nResume:\n{resume_text}"
    response = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an expert resume reviewer and career coach with 15 years of experience in tech recruiting. Score resumes honestly on a 0-100 scale across four dimensions: Experience, Skills, Formatting, and Impact. Write a 2-sentence summary. List 3-4 genuine strengths, 3-4 areas to improve, one single top-priority suggestion, key skills actually found in the resume, and important skills commonly expected for this candidate's field that appear to be missing.",
            response_mime_type="application/json", response_schema=FEEDBACK_SCHEMA,
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return json.loads(response.text)


def get_match(resume_text: str, jd_text: str) -> dict:
    prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
    response = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an ATS and recruiting expert. Compare the resume against the job description. Calculate a realistic match percentage, list specific important keywords/skills from the JD missing from the resume, and give concrete tailoring suggestions.",
            response_mime_type="application/json", response_schema=MATCH_SCHEMA,
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return json.loads(response.text)


def chat_about_resume(resume_text: str, history: list[dict], question: str) -> str:
    """Stateless resume Q&A: previous turns are folded into the prompt as context."""
    convo = ""
    for turn in history[-6:]:  # keep last 6 turns for context, avoid unbounded growth
        convo += f"User: {turn['q']}\nAssistant: {turn['a']}\n"
    prompt = f"Resume:\n{resume_text}\n\nConversation so far:\n{convo}\nUser: {question}"
    response = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful career assistant. Answer questions about the user's resume using ONLY the resume content provided. If asked something not answerable from the resume (e.g. salary expectations, personal opinions), say so honestly and briefly suggest how they could find that out. Keep answers concise and conversational.",
            thinking_config=types.ThinkingConfig(thinking_level="low"),
        ),
    )
    return response.text


COMPARE_SCHEMA = {
    "type": "object",
    "properties": {
        "winner": {"type": "string", "enum": ["Resume A", "Resume B", "Tie"]},
        "winner_reason": {"type": "string"},
        "differences": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "aspect": {"type": "string"},
                    "resume_a_note": {"type": "string"},
                    "resume_b_note": {"type": "string"},
                },
                "required": ["aspect", "resume_a_note", "resume_b_note"],
            },
        },
        "recommendation": {"type": "string"},
    },
    "required": ["winner", "winner_reason", "differences", "recommendation"],
}


def compare_resumes(resume_a: str, resume_b: str) -> dict:
    prompt = f"Resume A:\n{resume_a}\n\nResume B:\n{resume_b}"
    response = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an expert resume reviewer comparing two versions of a resume (or two candidates). Determine which is stronger overall and why. Break down 3-5 key aspects (e.g. Experience clarity, Skills relevance, Formatting, Impact/metrics) noting how each resume does on that aspect. Give one clear final recommendation.",
            response_mime_type="application/json", response_schema=COMPARE_SCHEMA,
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return json.loads(response.text)


def get_improved_resume(resume_text: str, jd_text: str = "") -> str:
    context = f"\n\nTailor it toward this job description:\n{jd_text}" if jd_text else ""
    prompt = f"Rewrite and improve this resume. Keep the same factual content (don't invent experience), but strengthen bullet points with action verbs, quantify impact where plausible, and improve clarity and structure.{context}\n\nOriginal Resume:\n{resume_text}"
    response = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a professional resume writer. Output ONLY the improved resume text, well-structured with clear section headers. No preamble, no explanation.",
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return response.text


def get_cover_letter(resume_text: str, jd_text: str = "") -> str:
    context = f"for this specific job:\n{jd_text}" if jd_text else "as a general, professional cover letter template"
    prompt = f"Write a compelling, concise cover letter (250-350 words) based on this resume, {context}\n\nResume:\n{resume_text}"
    response = client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a professional cover letter writer. Write in first person, confident but not arrogant tone. Output ONLY the cover letter text, no preamble.",
            thinking_config=types.ThinkingConfig(thinking_level="medium"),
        ),
    )
    return response.text


def _md_clean(s: str) -> str:
    """Strip markdown bold/italic markers and normalize unicode dashes."""
    s = s.replace("**", "").replace("*", "")
    s = s.replace("–", "-").replace("—", "-").replace("\u2013", "-").replace("\u2014", "-")
    return s.encode("latin-1", "replace").decode("latin-1")


def text_to_pdf(text: str, title: str) -> bytes:
    import textwrap

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(30, 30, 40)
    pdf.cell(0, 10, title, ln=True)
    pdf.set_draw_color(120, 110, 200)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 60, pdf.get_y())
    pdf.ln(6)

    def wrapped_cell(txt, width=95, line_h=6):
        for sub in (textwrap.wrap(txt, width=width, break_long_words=True, break_on_hyphens=True) or [""]):
            pdf.cell(0, line_h, sub, ln=True)

    for raw_line in text.split("\n"):
        line = raw_line.strip()

        if not line:
            pdf.ln(3)
            continue

        if line == "---":
            y = pdf.get_y()
            pdf.set_draw_color(210, 210, 220)
            pdf.set_line_width(0.2)
            pdf.line(10, y, 200, y)
            pdf.ln(4)
            continue

        # Markdown headings (# Name, ### SECTION)
        if line.startswith("### "):
            pdf.set_font("Helvetica", "B", 11.5)
            pdf.set_text_color(80, 65, 180)
            wrapped_cell(_md_clean(line[4:]), line_h=7)
            pdf.set_text_color(30, 30, 40)
            pdf.ln(1)
            continue
        if line.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(80, 65, 180)
            wrapped_cell(_md_clean(line[3:]), line_h=7)
            pdf.set_text_color(30, 30, 40)
            pdf.ln(1)
            continue
        if line.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            wrapped_cell(_md_clean(line[2:]), line_h=8)
            pdf.ln(1)
            continue

        # Bullet points
        if line.startswith("* ") or line.startswith("- "):
            content = _md_clean(line[2:])
            pdf.set_font("Helvetica", "", 10)
            pdf.set_x(pdf.l_margin + 4)
            for i, sub in enumerate(textwrap.wrap(content, width=90, break_long_words=True) or [""]):
                prefix = "-  " if i == 0 else "   "
                pdf.set_x(pdf.l_margin + 4)
                pdf.cell(0, 6, prefix + sub, ln=True)
            continue

        # Full-line italic (e.g. *Jan 2022 - Present*)
        if line.startswith("*") and line.endswith("*") and not line.startswith("**"):
            pdf.set_font("Helvetica", "I", 9.5)
            wrapped_cell(_md_clean(line))
            pdf.set_font("Helvetica", "", 10)
            continue

        # Full-line bold (job titles / company names with **)
        if line.startswith("**"):
            pdf.set_font("Helvetica", "B", 10.5)
            wrapped_cell(_md_clean(line))
            pdf.set_font("Helvetica", "", 10)
            continue

        # Regular paragraph text
        pdf.set_font("Helvetica", "", 10)
        wrapped_cell(_md_clean(line))
    return bytes(pdf.output())


# ── Session state ──────────────────────────────────────────────────
for key in ["resume_text", "resume_name", "feedback", "match", "improved_resume", "cover_letter", "jd_text"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "compare_result" not in st.session_state:
    st.session_state.compare_result = None

# ── Top navbar (functional) ───────────────────────────────────────
nav_left, nav_r1, nav_r2, nav_r3 = st.columns([5, 1, 1.4, 1])
with nav_left:
    st.markdown('<div><div class="brand">Resume<span>IQ</span></div><div class="brand-sub">AI-Powered Resume Analyzer</div></div>', unsafe_allow_html=True)
with nav_r1:
    if st.button("Home", key="nav_home", use_container_width=True):
        st.session_state.nav_page = "home"
        st.rerun()
with nav_r2:
    if st.button("How It Works", key="nav_how", use_container_width=True):
        st.session_state.nav_page = "how"
        st.rerun()
with nav_r3:
    if st.button("About", key="nav_about", use_container_width=True):
        st.session_state.nav_page = "about"
        st.rerun()
st.markdown('<hr style="border-color:#1F2440; margin: 10px 0 24px 0;">', unsafe_allow_html=True)

# ── How It Works page ──────────────────────────────────────────────
if st.session_state.nav_page == "how":
    st.markdown('<div class="hero-title">How <span>ResumeIQ</span> Works</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">From upload to a polished, tailored application kit — in four steps.</div>', unsafe_allow_html=True)
    steps = [
        ("1", "Upload Your Resume", "Upload your resume as a PDF. Optionally paste a job description to unlock job-matching and a tailored cover letter."),
        ("2", "AI Analysis", "Gemini analyzes your resume across four dimensions — Experience, Skills, Formatting, and Impact — using a structured scoring schema, not a vague chat reply."),
        ("3", "Structured Feedback", "Get an overall score, a radar breakdown, concrete strengths and gaps, and skills found vs. commonly expected but missing."),
        ("4", "Improved Output", "Generate an AI-rewritten resume and a tailored cover letter, both ready to download as polished PDFs."),
    ]
    cols = st.columns(4)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f'<div class="panel" style="min-height:190px;"><div style="color:#8B7CF6; font-weight:800; font-size:1.3rem;">{num}</div><div class="panel-title" style="margin-top:6px;">{title}</div><div class="summary-text">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home"):
        st.session_state.nav_page = "home"
        st.rerun()

# ── About page ─────────────────────────────────────────────────────
elif st.session_state.nav_page == "about":
    st.markdown('<div class="hero-title">About <span>ResumeIQ</span></div>', unsafe_allow_html=True)
    st.markdown('''
    <div class="panel" style="max-width:720px; margin: 0 auto;">
        <div class="summary-text" style="font-size:0.95rem;">
        ResumeIQ was built to solve a simple problem: most people never get real, specific feedback
        on their resume before it's rejected by an ATS filter or skimmed past by a recruiter.
        <br><br>
        Instead of generic advice like "use action verbs," ResumeIQ reads your actual resume and gives
        structured, honest feedback — a score breakdown, a job-match analysis against a real posting,
        an AI-rewritten version, and a tailored cover letter — all in under a minute.
        <br><br>
        Built using Google's Gemini API with structured JSON outputs, so every score and suggestion is
        generated from a defined schema, not a loosely parsed chat reply.
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    _, bcol, _ = st.columns([2, 1, 2])
    with bcol:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.nav_page = "home"
            st.rerun()

# ── Home page ──────────────────────────────────────────────────────
else:
    # Hero upload card (main page, no sidebar)
    if not st.session_state.resume_text:
        st.markdown('<div class="hero-title">Get AI-Powered <span>Resume Feedback</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Upload your resume and get an instant, structured AI review — score breakdown, job match, an improved rewrite, and a ready-to-send cover letter.</div>', unsafe_allow_html=True)

        _, mid, _ = st.columns([1, 2.2, 1])
        with mid:
            st.markdown('<div class="upload-card">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload your resume (PDF)", type="pdf", label_visibility="visible")
            jd_input = st.text_area("Paste a job description (optional) — unlocks Job Match & a tailored cover letter", height=130, placeholder="Paste the job posting here...")
            analyze_clicked = st.button("Analyze Resume", type="primary", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file and analyze_clicked:
            st.session_state.resume_text = extract_text(io.BytesIO(uploaded_file.read()))
            st.session_state.resume_name = uploaded_file.name
            st.session_state.jd_text = jd_input
            with st.spinner("Analyzing your resume..."):
                st.session_state.feedback = get_feedback(st.session_state.resume_text)
            if jd_input.strip():
                with st.spinner("Comparing against the job description..."):
                    st.session_state.match = get_match(st.session_state.resume_text, jd_input)
            else:
                st.session_state.match = None
            st.session_state.improved_resume = None
            st.session_state.cover_letter = None
            st.rerun()

    if st.session_state.resume_text:
        _, ctrl, _ = st.columns([1, 2.2, 1])
        with ctrl:
            if st.button("⬅ Analyze a different resume", use_container_width=True):
                for key in ["resume_text", "resume_name", "feedback", "match", "improved_resume", "cover_letter", "jd_text"]:
                    st.session_state[key] = None
                st.rerun()

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Dashboard", "🎯 Job Match", "✨ Improved Resume", "✉️ Cover Letter", "💬 Ask My Resume", "🔀 Compare Versions"])

        # ── Tab 1: Dashboard ──
        with tab1:
            fb = st.session_state.feedback
            sections = {s["name"]: s for s in fb["sections"]}

            st.markdown(f'<div class="greeting">Resume Analysis Complete ✅</div><div class="greeting-sub">{st.session_state.resume_name}</div>', unsafe_allow_html=True)

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(ring_html("Overall Score", fb["overall_score"], "Keep improving 🎯"), unsafe_allow_html=True)
            with c2:
                exp = sections.get("Experience", {}).get("score", 0)
                st.markdown(ring_html("Experience", exp), unsafe_allow_html=True)
            with c3:
                sk = sections.get("Skills", {}).get("score", 0)
                st.markdown(ring_html("Skills", sk), unsafe_allow_html=True)
            with c4:
                fmt = sections.get("Formatting", {}).get("score", 0)
                st.markdown(ring_html("Formatting", fmt), unsafe_allow_html=True)

            col_left, col_right = st.columns([1.1, 1])
            with col_left:
                st.markdown('<div class="panel"><div class="panel-title">Score Overview</div>', unsafe_allow_html=True)
                st.plotly_chart(radar_chart(fb["sections"]), use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)
            with col_right:
                callouts = f'''
                <div class="panel">
                    <div class="panel-title">Summary</div>
                    <div class="summary-text">{fb["summary"]}</div>
                    <div class="callout"><span class="callout-icon">💡</span><div><span class="callout-label">Top Suggestion</span><br><span class="callout-text">{fb["top_suggestion"]}</span></div></div>
                </div>
                '''
                st.markdown(callouts, unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                items = "".join(f'<div class="list-item good">{s}</div>' for s in fb["strengths"])
                st.markdown(f'<div class="panel"><div class="panel-title">✅ Strengths</div>{items}</div>', unsafe_allow_html=True)
            with c2:
                items = "".join(f'<div class="list-item warn">{s}</div>' for s in fb["areas_to_improve"])
                st.markdown(f'<div class="panel"><div class="panel-title">⚠️ Areas to Improve</div>{items}</div>', unsafe_allow_html=True)
            with c3:
                found = "".join(f'<span class="chip chip-found">{s}</span>' for s in fb["skills_found"])
                missing = "".join(f'<span class="chip chip-missing">{s}</span>' for s in fb["missing_skills"])
                st.markdown(f'<div class="panel"><div class="panel-title">🔎 Skills</div><div style="margin-bottom:10px;">{found}</div><div class="panel-title" style="font-size:0.85rem;color:#9BA1C0;">Missing</div>{missing}</div>', unsafe_allow_html=True)

            st.markdown('''
            <div class="cta-banner">
                <div><div class="cta-title">✨ Improve Your Resume with AI</div><div class="cta-sub">Let AI rewrite and optimize your resume to make it recruiter-friendly.</div></div>
            </div>
            ''', unsafe_allow_html=True)

        # ── Tab 2: JD Match ──
        with tab2:
            if st.session_state.match:
                m = st.session_state.match
                pct = m["match_percentage"]
                color = ring_color(pct)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f'<div class="match-hero"><div class="match-number" style="color:{color};">{pct}%</div><div class="kpi-caption">Match Score</div></div>', unsafe_allow_html=True)
                with col2:
                    chips = "".join(f'<span class="chip chip-missing">{k}</span>' for k in m["missing_keywords"])
                    st.markdown(f'<div class="panel"><div class="panel-title">Missing Keywords / Skills</div>{chips}</div>', unsafe_allow_html=True)
                st.markdown('<div class="panel-title" style="margin-top:16px;">Tailoring Suggestions</div>', unsafe_allow_html=True)
                for sug in m["tailoring_suggestions"]:
                    st.markdown(f'<div class="list-item warn">{sug}</div>', unsafe_allow_html=True)
            else:
                st.info("Paste a job description above and re-analyze to see your match score.")

        # ── Tab 3: Improved Resume ──
        with tab3:
            if st.session_state.improved_resume is None:
                if st.button("Generate Improved Resume", type="primary"):
                    with st.spinner("Rewriting your resume..."):
                        jd_for_improve = st.session_state.jd_text if st.session_state.jd_text and st.session_state.jd_text.strip() else ""
                        st.session_state.improved_resume = get_improved_resume(st.session_state.resume_text, jd_for_improve)
                    st.rerun()
            else:
                with st.container(border=True):
                    st.markdown(st.session_state.improved_resume)
                pdf_bytes = text_to_pdf(st.session_state.improved_resume, "Improved Resume")
                st.download_button("⬇ Download Improved Resume (PDF)", data=pdf_bytes, file_name="improved_resume.pdf", mime="application/pdf")

        # ── Tab 4: Cover Letter ──
        with tab4:
            if st.session_state.cover_letter is None:
                if st.button("Generate Cover Letter", type="primary"):
                    with st.spinner("Writing your cover letter..."):
                        jd_for_letter = st.session_state.jd_text if st.session_state.jd_text and st.session_state.jd_text.strip() else ""
                        st.session_state.cover_letter = get_cover_letter(st.session_state.resume_text, jd_for_letter)
                    st.rerun()
            else:
                with st.container(border=True):
                    st.markdown(st.session_state.cover_letter)
                pdf_bytes = text_to_pdf(st.session_state.cover_letter, "Cover Letter")
                st.download_button("⬇ Download Cover Letter (PDF)", data=pdf_bytes, file_name="cover_letter.pdf", mime="application/pdf")

        # ── Tab 5: Resume Chatbot ──
        with tab5:
            st.markdown('<div class="panel-title">💬 Ask questions about your resume</div>', unsafe_allow_html=True)
            for turn in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.markdown(turn["q"])
                with st.chat_message("assistant"):
                    st.markdown(turn["a"])

            question = st.chat_input("e.g. What's my strongest project? How many years of Python experience do I have?")
            if question:
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        answer = chat_about_resume(st.session_state.resume_text, st.session_state.chat_history, question)
                    st.markdown(answer)
                st.session_state.chat_history.append({"q": question, "a": answer})

            if st.session_state.chat_history:
                if st.button("🗑️ Clear chat"):
                    st.session_state.chat_history = []
                    st.rerun()

        # ── Tab 6: Version Compare ──
        with tab6:
            st.markdown('<div class="panel-title">🔀 Compare against another resume version</div>', unsafe_allow_html=True)
            st.caption("Upload a second resume (a different draft, or another candidate) to see which is stronger and why.")
            second_file = st.file_uploader("Upload Resume B (PDF)", type="pdf", key="compare_upload")

            if second_file and st.button("Compare Resumes", type="primary"):
                with st.spinner("Comparing both resumes..."):
                    resume_b_text = extract_text(io.BytesIO(second_file.read()))
                    st.session_state.compare_result = compare_resumes(st.session_state.resume_text, resume_b_text)

            if st.session_state.compare_result:
                cr = st.session_state.compare_result
                winner_color = "#5FD68A" if cr["winner"] != "Tie" else "#E8B84F"
                st.markdown(f'''
                <div class="match-hero">
                    <div class="match-number" style="color:{winner_color}; font-size:1.8rem;">{cr["winner"]}</div>
                    <div class="kpi-caption">{cr["winner_reason"]}</div>
                </div>
                ''', unsafe_allow_html=True)

                st.markdown('<div class="panel-title" style="margin-top:18px;">Side-by-Side Breakdown</div>', unsafe_allow_html=True)
                for d in cr["differences"]:
                    st.markdown(f'''
                    <div class="panel">
                        <div class="section-card-title" style="margin-bottom:8px;">{d["aspect"]}</div>
                        <div style="display:flex; gap:20px;">
                            <div style="flex:1;"><b style="color:#8FC2FF;">Resume A (yours):</b><br><span class="summary-text">{d["resume_a_note"]}</span></div>
                            <div style="flex:1;"><b style="color:#C9B8FF;">Resume B:</b><br><span class="summary-text">{d["resume_b_note"]}</span></div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown(f'<div class="callout"><span class="callout-icon">💡</span><div><span class="callout-label">Recommendation</span><br><span class="callout-text">{cr["recommendation"]}</span></div></div>', unsafe_allow_html=True)

    else:
        st.info("👈 Upload your resume above and click 'Analyze Resume' to get started.")

