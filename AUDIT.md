# First-Place Submission Audit

## Verdict

The repository now contains a functional, auditable prototype. It is **not submission-complete** until every HARD GATE below is evidenced with a public URL or artifact.

## HARD GATES

| Gate | Requirement | Status | Evidence required |
|---|---|---:|---|
| G1 | Public working product/demo | OPEN | HTTPS URL, no login |
| G2 | Gloo AI Studio live call | OPEN | redacted success JSON + timestamp |
| G3 | YouVersion live passage call | OPEN | redacted success JSON + timestamp |
| G4 | Both APIs used in one end-to-end request | OPEN | `/v1/experience` response with `mode=live` |
| G5 | Public Kaggle Notebook attached | OPEN | notebook URL |
| G6 | Public YouTube video ≤3:00 | OPEN | direct video URL |
| G7 | Kaggle cover image/media gallery | OPEN | attached cover screenshot |
| G8 | Kaggle Writeup ≤500 words submitted | OPEN | final submitted state screenshot |
| G9 | Public repository and setup reproducible | PASS | repository + Dockerfile + README |
| G10 | Consent/crisis/public-social safety | PASS | automated tests |
| G11 | Documented YouVersion passage endpoint | PASS | `backend/clients.py` |
| G12 | CI green | PENDING | GitHub Actions run |

## Product differentiation

Scripture Everywhere AI is not five unrelated mockups. It is one context-to-Scripture operating layer with five delivery surfaces:

1. Wearable haptic cue
2. Game respawn surface
3. IDE margin card
4. Private social moderator prompt
5. Creator-only stream overlay

The shared pipeline is:

`context → Gloo discernment → bounded theme → YouVersion passage → consent/safety/delivery policy`

## Judge-proof technical claims

Only claim the following after evidence exists:

- “Live Gloo AI Studio inference” requires G2.
- “Live YouVersion retrieval” requires G3.
- “Working end-to-end product” requires G1 and G4.
- “Public Notebook” requires G5.

Until then, call the system a **working credential-free prototype with live adapters implemented**.

## Final acceptance command

```bash
cd backend
pip install -r requirements.txt
pytest -q
uvicorn app:app --host 0.0.0.0 --port 8000
```

Then POST a sample event and verify:

```bash
curl -s http://localhost:8000/v1/experience \
  -H 'Content-Type: application/json' \
  -d '{"source":"wearable","moment_type":"breakthrough_wall","metrics":{"heart_rate":170,"effort_pct":0.85},"privacy":"private","user_opted_in":true}'
```

Expected minimum fields: `discernment`, `scripture`, `delivery_surface`, `mode`, `pipeline`.
