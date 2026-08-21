# 🔁 AI Content Repurposing & Marketing Automation

Paste one long-form piece of content — a blog post, article, product
brief, or campaign brief — and get back a full set of ready-to-use
marketing assets in one structured AI call: a LinkedIn post, a short
video/Reel script, a summary, campaign ideas, hooks, CTAs, and email
subject lines.

**🔗 Live demo:** _add your Streamlit Cloud link here after deployment_

---

## Problem statement

Marketers routinely rewrite the same core idea into 6-7 different formats
for different platforms — a task that's repetitive, time-consuming, and
easy to do inconsistently across formats. This tool takes that first-draft
work down to one paste-and-generate step, while keeping a human
approval step before anything is treated as final.

## Features

- Paste any long-form content and repurpose it into 7 asset types in a single AI call
- Strict JSON output from the LLM, parsed and validated safely
- Input validation with clear, friendly error messages
- Approve / Reject workflow with optional revision notes
- Every generation logged locally (timestamp, inputs, outputs, approval status)
- Clean modular codebase — no single giant file
- Ready to deploy on Streamlit Community Cloud

## Architecture

```
User pastes content (app.py)
        │
        ▼
validators.py     → rejects empty/too-short input before any API call
        │
        ▼
prompts.py        → builds one prompt requesting a strict JSON schema
        │
        ▼
ai_engine.py       → calls Groq, handles all network/API failure modes
        │
        ▼
output_parser.py    → safely parses + validates the JSON response
        │
        ▼
app.py displays each asset in its own card
        │
        ▼
User clicks Approve/Reject → logger.py updates the log entry
```

Each file has exactly one responsibility, which maps to one failure mode:
bad input, bad prompt, bad network/API call, or bad JSON. This separation
is what makes the codebase easy to explain and easy to extend.

## Tech stack

| Layer | Tool |
|---|---|
| UI | Streamlit |
| LLM | Groq (model name is a single constant in `ai_engine.py`, easy to swap) |
| Structured output | JSON, via Groq's `response_format: json_object` |
| Logging | Local JSON file (`generation_log.json`) |
| Hosting | Streamlit Community Cloud |

## Project structure

```
ai-content-repurposing/
├── app.py              # UI only — wires everything together
├── ai_engine.py         # The only file that talks to the Groq API
├── prompts.py            # Builds the structured JSON-requesting prompt
├── validators.py           # Input validation before any API call
├── output_parser.py          # Safely parses/validates the LLM's JSON reply
├── logger.py                  # Local JSON logging + approval status updates
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## How the structured JSON output works

Instead of making 7 separate API calls (one per asset type), the app
sends **one** prompt that explicitly repeats the exact JSON schema it
wants back, and sets `response_format: {"type": "json_object"}` on the
Groq request. This is both cheaper and keeps every asset consistent with
the same context. `output_parser.py` then:
1. Strips accidental markdown code fences (some models add them anyway)
2. Parses the text as JSON, catching decode errors
3. Confirms every required key is present
4. Returns a clean Python dict, or raises a clear error the UI can display

## Approval workflow

Every generation is logged immediately with `approval_status: "pending"`.
After reviewing the output, you can:
- **Approve** — marks the same log entry as `approved`
- **Reject** — marks it `rejected`, optionally with revision notes

This models a real content-review process: nothing is "final" just
because the AI generated it.

## Logging workflow

Every record in `generation_log.json` contains:
```json
{
  "id": "gen_1_1755781234",
  "timestamp": "2026-08-21T10:30:00+00:00",
  "brand": "...",
  "target_audience": "...",
  "source_type": "...",
  "outputs": { ...the full generated JSON... },
  "approval_status": "pending | approved | rejected",
  "revision_notes": ""
}
```
It's plain JSON on purpose — readable, diffable, and trivial to swap for
a real database (Postgres, SQLite, Airtable) later without changing any
other module.

## Future n8n integration (not yet built)

The architecture is deliberately ready for this, but **it is not wired up
yet**. The plan: after `logger.log_generation()` runs, optionally POST the
same record to an n8n webhook URL, which could then push approved content
to a scheduling tool, Slack, or a Google Sheet. Because logging is already
isolated in `logger.py`, adding this later is a small, contained change —
not a rewrite.

## Interview talking points

- **"Why one JSON call instead of separate calls per asset?"** → Cheaper,
  faster, and keeps every generated asset grounded in the same context —
  the LinkedIn post and video script come from the same understanding of
  the source content.
- **"What happens if the model returns bad JSON?"** → `output_parser.py`
  catches it, the user sees a clear "try again" message — the app never
  crashes on a malformed AI response.
- **"Why log locally instead of a database?"** → Right-sized for the
  project stage; the log format is designed so swapping in a real
  database only touches `logger.py`.
- **"What would you add next?"** → The n8n webhook connection, a database
  instead of the JSON file, and user auth if this became multi-user.

## Future improvements

- Wire up the n8n webhook described above
- Swap local JSON logging for a real database
- Add user accounts so approval history is per-user
- Add regeneration of a single asset (e.g. "just redo the hooks") instead of the whole set

---

## Setup instructions

See the step-by-step section below for exact commands (macOS, local run
only — no GitHub or deployment yet).
