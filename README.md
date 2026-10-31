# NexusCV — AI CV & Cover Letter Generator

A fully functional Streamlit SaaS app that creates and improves CVs and cover letters with the OpenAI API, runs deterministic ATS scoring, and exports PDF/DOCX files.

## Features

- **Landing page** with secure OpenAI API key validation (session-only; never logged or written to disk)
- **Create CV from Scratch** — multi-entry forms for contact, summary, education, experience, internships, projects, skills, certifications, achievements, languages, portfolio links, and target job details
- **Improve Existing CV** — PDF/DOCX upload, real text extraction, OpenAI analysis, side-by-side original vs recommended content, improved CV + cover letter
- **Deterministic ATS analysis** — transparent keyword, formatting, skills, experience, and completeness scores (estimates, not employer ATS guarantees)
- **Templates** — Classic ATS, Modern Violet, Minimal Clean
- **Live preview** and separate **PDF / DOCX** downloads for CV and cover letter
- **Premium dark UI** — navy/charcoal surfaces with violet and electric-blue accents

## Requirements

- Python 3.10+
- An OpenAI API key

## Setup

```bash
cd "D:\Huawei AI\CV Chatbot"
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # optional model defaults
```

## Run

```bash
streamlit run app.py
```

Open the URL shown in the terminal (typically http://localhost:8501).

1. Paste your OpenAI API key on the landing page and click **Validate & Enter Studio**.
2. Choose **Create from Scratch** or **Improve Existing CV**.
3. Review/edit generated content, inspect ATS scores, and download PDF/DOCX files.

## Configuration

| Variable | Description |
|----------|-------------|
| `OPENAI_MODEL` | Optional default model (e.g. `gpt-4o-mini`) |
| `MAX_UPLOAD_MB` | Optional upload limit hint (Streamlit also uses `.streamlit/config.toml`) |

API keys are entered in the UI and stored only in Streamlit `session_state` on the server process. They are never printed to logs.

## Project structure

```
app.py                 # Streamlit entrypoint
src/
  openai_client.py     # Key validation + structured chat helpers
  schemas.py           # Pydantic models
  document_parser.py   # PDF/DOCX extraction
  document_export.py   # PDF/DOCX generation
  ats_analyzer.py      # Deterministic ATS scoring
  cv_generator.py      # Create-from-scratch AI pipeline
  cv_improver.py       # Analyze + improve pipeline
  ui/                  # Pages, styles, preview/export
.streamlit/config.toml
requirements.txt
.env.example
```

## Security notes

- API keys are not committed, logged, or embedded in client-side assets.
- Uploaded documents are processed in memory for the current session.
- The model is instructed never to invent qualifications, experience, or achievements.
- ATS scores are rule-based estimates with an explicit disclaimer.

## Troubleshooting

- **Authentication failed** — verify the key at [platform.openai.com](https://platform.openai.com).
- **PDF extraction empty** — scanned/image-only PDFs are not supported; use a text PDF or DOCX.
- **Rate limits** — wait and retry, or switch to a different model on the landing page.
