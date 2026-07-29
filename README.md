# 🎯 ResumeIQ — AI-Powered Resume Feedback Tool

**Capstone Project — Generative AI & Prompt Engineering Internship, NeuroFive Solutions**

An AI-powered mini-app that gives job seekers honest, structured feedback on their resume — a score breakdown, a job-description match analysis, an AI-rewritten version, and a tailored cover letter, all in one place.

🔗 **Live demo:** [Insert your Streamlit app link here after deploying]
🎥 **Video walkthrough:** [Insert your LinkedIn video link here]

---

## The Problem

Most people never get real feedback on their resume before it's rejected by an ATS filter or a recruiter's 6-second scan. Career advice online is generic ("use action verbs!") and doesn't look at *your* actual resume. ResumeIQ solves this by giving specific, structured, actionable feedback in under a minute — and goes a step further by generating an improved version and a matching cover letter, so the user leaves with usable output, not just criticism.

---

## Core Flow

1. **Input:** User uploads a resume (PDF) and optionally pastes a job description
2. **Output:** Six AI-generated views, organized into tabs:
   - **Dashboard** — overall score (0-100) + section-by-section breakdown (Experience, Skills, Formatting, Impact) with a radar chart, strengths, gaps, and skills found vs. missing
   - **Job Match** — match percentage against the pasted job description, missing keywords, and tailoring suggestions
   - **Improved Resume** — a rewritten version with stronger language and structure, downloadable as a PDF
   - **Cover Letter** — a tailored cover letter (or a generic professional one if no job description was provided), downloadable as a PDF
   - **Ask My Resume** — a chat interface to ask natural-language questions about your own resume ("What's my strongest project?"), answered strictly from the resume content
   - **Compare Versions** — upload a second resume to see a structured side-by-side comparison, a declared winner, and a recommendation

---

## Why This App, and What Makes It More Than a Wrapper

Structured JSON output is the load-bearing technique here, not a bolt-on. The feedback and job-match features **require** structured output — a score, a list of section objects, an array of missing keywords — because the UI renders them as distinct visual elements (score cards, keyword chips, section breakdowns). A plain paragraph response from the model couldn't power this UI; the schema *is* the interface. The improved-resume and cover-letter features intentionally use free-text generation instead, because the entire point of a schema was to constrain and shape data, not creative long-form writing — using the right tool for each sub-problem rather than forcing one pattern everywhere.

---

## Tech Stack

| Component | Choice | Why |
|---|---|---|
| LLM | `gemini-3.5-flash-lite` | Fast, current, generous free tier |
| Structured output | Gemini JSON mode (`response_schema`) | Guarantees parseable, UI-ready data for scores and match analysis |
| PDF parsing | `pypdf` | Extracts resume text from uploaded PDF |
| PDF generation | `fpdf2` | Generates downloadable improved resume / cover letter |
| SDK | `google-genai` | Official current SDK |
| UI | Streamlit | Fast to build, easy to deploy, good for a dashboard-style app |

---

## Running Locally

```bash
pip install -r requirements.txt
```

Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your_key_here"
```

Run:
```bash
streamlit run app.py
```

---

## Deploying (Streamlit Community Cloud)

1. Push this repo to GitHub (public)
2. [share.streamlit.io](https://share.streamlit.io) → New app → select this repo → main file `app.py`
3. Advanced settings → Secrets → add `GEMINI_API_KEY`
4. Deploy

---

## Test Results (3-5 realistic inputs)

*(Fill in after testing with real resumes — note any rough edges found and fixed)*

| # | Input | Result | Notes |
|---|-------|--------|-------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

---

## What I'd Improve With More Time

- **Persistent history** — currently each session is stateless; a logged-in version could save past resume versions and track score improvement over time
- **Multi-format export** — currently PDF-only for downloads; adding a `.docx` export would match what most job seekers actually need to edit further
- **Finer-grained ATS simulation** — the job-match feature estimates a percentage via the LLM's judgment; a production version could add a real keyword-frequency/embedding-similarity layer alongside the LLM's qualitative read, for a more defensible score
- **Section-level rewriting** — right now the "Improved Resume" rewrites the whole document at once; letting users regenerate just one section (e.g. only the Experience bullet points) would give more control

---

## Project Structure

```
resume-iq/
├── app.py              # Full app (UI + all 4 AI features)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

**Submitted as part of the Generative AI & Prompt Engineering Internship at NeuroFive Solutions**
