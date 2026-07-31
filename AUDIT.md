# First-Place Submission Audit

## Verdict

The repository is now a **CI-verified judge-ready technical, safety, notebook, video, and media package**. Remaining open gates require sponsor credentials or external account actions and must not be represented as complete until public evidence exists.

## Hard gates

| Gate | Requirement | Status | Evidence |
|---|---|---:|---|
| G1 | Public working product/demo | VERIFY | `.github/workflows/pages.yml`; open `https://o-yutaka.github.io/popopo/` logged out |
| G2 | Gloo OAuth2 token exchange | OPEN | live evidence must show `gloo_auth_mode=oauth2_client_credentials` |
| G3 | Gloo Completions V2 live call | OPEN | evidence must show API v2 and executed `gloo` call |
| G4 | YouVersion live passage call | OPEN | evidence must show `source=youversion` |
| G5 | Both APIs in one end-to-end request | OPEN | `sponsor_calls_executed=["gloo","youversion"]` |
| G6 | Complete public notebook artifact | PASS | `notebooks/scripture_everywhere_submission.ipynb` |
| G7 | Notebook attached inside Kaggle | OPEN | Kaggle notebook URL or attachment screenshot |
| G8 | Exact 180-second video package | PASS | timeline assertion, renderer, narration and captions |
| G9 | Public YouTube video ≤3:00 | OPEN | public/unlisted YouTube URL |
| G10 | Upload-safe 1600×900 PNG media | PASS | `media/cover.png`, `media/architecture.png` |
| G11 | Media attached inside Kaggle | OPEN | Kaggle Media Gallery screenshot |
| G12 | Kaggle writeup ≤500 words | PASS | 401 words in `SUBMISSION.md` |
| G13 | Kaggle writeup finally submitted | OPEN | non-draft submission state |
| G14 | Gloo official OAuth scope | PASS | `grant_type=client_credentials`, `scope=api/access` |
| G15 | Gloo current endpoint | PASS | `/ai/v2/chat/completions` |
| G16 | YouVersion canonical passage route | PASS | `/v1/bibles/{id}/passages/{usfm}` |
| G17 | YouVersion attribution | PASS | Bible metadata, copyright and attribution URL returned |
| G18 | Local consent/crisis preflight before APIs | PASS | `sponsor_calls_executed=[]` regression tests |
| G19 | No partial live pipeline | PASS | both credentials required before any external call |
| G20 | Public-social auto-post prohibited | PASS | private moderator route and human review |
| G21 | Pseudonymous cooldown enforcement | PASS | SHA-256 key ledger, no raw identity retained |
| G22 | Strict API contract | PASS | unknown fields rejected with 422 |
| G23 | Submission-asset regression gates | PASS | GitHub Actions validated 180 seconds, notebook JSON, 500-word cap, media size and required files |
| G24 | CI green | PASS | GitHub Actions CI run #71: 16 tests passed; Python compileall passed |

## Verified CI record

- Audit PR: https://github.com/o-yutaka/popopo/pull/1
- Result: closed without merge because it contained audit-only trigger files
- GitHub Actions run: `CI #71`
- Runtime: Python 3.12 on Ubuntu 24.04
- Test result: `16 passed in 0.42s`
- Compilation result: all backend scripts and tests compiled successfully
- First run exposed an import-path defect; `backend/tests/conftest.py` fixed it on `main`, then the full audit passed

## Real execution order

```text
context
→ local consent/crisis/cooldown preflight
→ Gloo OAuth2 token exchange
→ Gloo Completions V2 discernment
→ bounded theme allowlist
→ canonical USFM passage ID
→ YouVersion passage + Bible attribution
→ timing/privacy/cooldown delivery policy
→ native surface
```

## Judge-proof claims

Only claim:

- **“Live Gloo OAuth2 + Completions V2 inference”** after G2 and G3 pass.
- **“Live YouVersion passage retrieval with attribution”** after G4 passes.
- **“Live end-to-end sponsor API pipeline”** after G5 passes.
- **“Public deployed product”** after G1 is opened in a logged-out browser.
- **“Kaggle Notebook attached”** only after G7.
- **“Three-minute YouTube demo”** only after G9.

Until then, use:

> CI-verified credential-free prototype with official live adapters, strict execution provenance, and a public verification workflow.

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
  -d '{"source":"wearable","moment_type":"effort_peak","metrics":{"heart_rate":170,"effort":0.85,"minutes":18},"privacy":"private","user_opted_in":true,"delivery_key":"demo-runner-001"}'
```

Required response fields:

```text
context
discernment
scripture
delivery_surface
delivery_timing
cooldown_seconds
cooldown_remaining_seconds
cooldown_enforced
suppressed
suppression_reason
mode
sponsor_calls_executed
pipeline
```

## External completion order

1. Verify the Pages URL in a logged-out browser.
2. Follow `SPONSOR_SETUP.md` and add the three secrets.
3. Run `Capture verified live API evidence`.
4. Confirm `evidence/live-api-evidence.json` was committed.
5. Run `Render three-minute submission video` and download the artifact.
6. Upload MP4, captions, and `media/cover.png` to YouTube.
7. Attach the notebook and both PNGs in Kaggle.
8. Paste the writeup and every public link.
9. Submit and capture the final non-draft state.
