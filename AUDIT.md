# First-Place Submission Audit

## Verdict

The repository is now a **judge-ready technical and media package**. The remaining open gates require external credentials or account-level submission actions; they must not be represented as complete until public evidence exists.

## Hard gates

| Gate | Requirement | Status | Evidence |
|---|---|---:|---|
| G1 | Public working product/demo | DEPLOYING | `.github/workflows/pages.yml`; verify `https://o-yutaka.github.io/popopo/` |
| G2 | Gloo AI Studio live call | OPEN | `evidence/live-api-evidence.json` after secret-backed workflow |
| G3 | YouVersion live passage call | OPEN | same redacted evidence file with `source=youversion` |
| G4 | Both APIs in one end-to-end request | OPEN | one `/v1/experience` response with `mode=live` |
| G5 | Complete public notebook artifact | PASS | `notebooks/scripture_everywhere_submission.ipynb` |
| G6 | Notebook attached inside Kaggle submission | OPEN | Kaggle notebook URL or attachment screenshot |
| G7 | Exact video experience and narration package | PASS | `video.html`, narration, captions and render workflow |
| G8 | Public YouTube video ≤3:00 | OPEN | YouTube URL after uploading rendered MP4 |
| G9 | Cover and architecture Media Gallery sources | PASS | `media/cover.svg`, `media/architecture.svg` |
| G10 | Upload-safe PNG media | GENERATING | `.github/workflows/media-assets.yml` commits PNG files |
| G11 | Media attached inside Kaggle submission | OPEN | Kaggle Media Gallery screenshot |
| G12 | Kaggle writeup ≤500 words | PASS | `SUBMISSION.md` |
| G13 | Kaggle writeup finally submitted | OPEN | submitted-state screenshot, not draft |
| G14 | Public repository and setup reproducible | PASS | README, Dockerfile, tests and workflows |
| G15 | Consent/crisis/public-social safety | PASS | `backend/policy.py` and automated tests |
| G16 | YouVersion canonical passage route | PASS | `backend/clients.py` |
| G17 | Strict API contract rejects unknown fields | PASS | `ConfigDict(extra="forbid")` |
| G18 | CI green | PENDING | successful Actions run visible on GitHub |

## Product differentiation

Scripture Everywhere AI is one context-to-Scripture operating layer with five native delivery surfaces:

1. Wearable haptic cue
2. Game respawn surface
3. IDE margin card
4. Private social moderator prompt
5. Creator-only stream overlay

Shared pipeline:

```text
context
→ Gloo discernment
→ bounded theme
→ canonical passage ID
→ YouVersion passage
→ consent/safety/timing/privacy policy
→ native surface
```

## Judge-proof claims

Only claim:

- **“Live Gloo AI Studio inference”** after G2 passes.
- **“Live YouVersion retrieval”** after G3 passes.
- **“Live end-to-end sponsor API pipeline”** after G4 passes.
- **“Public deployed product”** after G1 is opened in a logged-out browser.
- **“Kaggle Notebook attached”** only after G6.
- **“Three-minute YouTube demo”** only after G8.

Until then, use: **“working credential-free prototype with implemented live adapters and a public verification workflow.”**

## Local acceptance

```bash
cd backend
pip install -r requirements.txt
pytest -q
uvicorn app:app --host 0.0.0.0 --port 8000
```

```bash
curl -s http://localhost:8000/v1/experience \
  -H 'Content-Type: application/json' \
  -d '{"source":"wearable","moment_type":"effort_peak","metrics":{"heart_rate":170,"effort":0.85,"minutes":18},"privacy":"private","user_opted_in":true}'
```

Required response fields:

```text
context
discernment
scripture
delivery_surface
suppressed
suppression_reason
mode
pipeline
```

## External completion order

1. Verify the Pages URL logged out.
2. Add sponsor API secrets and run `Capture verified live API evidence`.
3. Confirm the evidence JSON was committed.
4. Run `Render three-minute submission video` and download the artifact.
5. Upload MP4, captions and PNG thumbnail to YouTube.
6. Attach the notebook and both PNGs in Kaggle.
7. Paste the writeup and all public links.
8. Submit and capture the final non-draft state.
