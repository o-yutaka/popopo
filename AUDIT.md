# First-Place Submission Audit

## Verdict

The repository is a **CI-verified and visually inspected judge-ready technical, safety, notebook, video, and media package**. Remaining open gates require sponsor credentials or external account actions and must not be represented as complete until their public evidence exists.

## Hard gates

| Gate | Requirement | Status | Evidence |
|---|---|---:|---|
| G1 | Public working product/demo | VERIFY | Open `https://o-yutaka.github.io/popopo/` logged out |
| G2 | Gloo OAuth2 token exchange | OPEN | Live evidence must show `gloo_auth_mode=oauth2_client_credentials` |
| G3 | Gloo Completions V2 live call | OPEN | Evidence must show executed `gloo` call |
| G4 | YouVersion live passage call | OPEN | Evidence must show `source=youversion` |
| G5 | Both APIs in one end-to-end request | OPEN | `sponsor_calls_executed=["gloo","youversion"]` |
| G6 | Complete public notebook artifact | PASS | `notebooks/scripture_everywhere_submission.ipynb` |
| G7 | Notebook attached inside Kaggle | OPEN | Kaggle attachment required |
| G8 | Clean video package under three minutes | PASS | 179.000s, H.264/AAC, 1920×1080 |
| G9 | Runner interaction visibly demonstrated | PASS | detect → wait → wrist raise → reveal |
| G10 | Recording controls absent | PASS | Renderer assertion and visual inspection |
| G11 | Public CTA visible | PASS | Final frame shows Pages and repository URLs |
| G12 | Live/demo claims visually separated | PASS | “verified only when” condition plus dynamic evidence gate |
| G13 | Public YouTube video | OPEN | Public/unlisted YouTube URL required |
| G14 | Upload-safe 1600×900 PNG media | PASS | `media/cover.png`, `media/architecture.png` |
| G15 | Cover title and verse not clipped | PASS | Final PNG visual inspection |
| G16 | Media attached inside Kaggle | OPEN | Kaggle Media Gallery upload required |
| G17 | Kaggle writeup ≤500 words | PASS | CI word-count gate |
| G18 | Kaggle writeup finally submitted | OPEN | Non-draft submission state required |
| G19 | Gloo official OAuth scope | PASS | `grant_type=client_credentials`, `scope=api/access` |
| G20 | Gloo current endpoint | PASS | `/ai/v2/chat/completions` |
| G21 | YouVersion canonical passage route | PASS | `/v1/bibles/{id}/passages/{usfm}` |
| G22 | YouVersion attribution | PASS | Bible metadata, copyright and attribution URL returned |
| G23 | Local consent/crisis preflight before APIs | PASS | Blocked events execute zero sponsor calls |
| G24 | No partial live pipeline | PASS | Both credentials required before external calls |
| G25 | Public-social auto-post prohibited | PASS | Private moderator route and human review |
| G26 | Pseudonymous cooldown enforcement | PASS | SHA-256 key ledger; no raw identity retained |
| G27 | Strict API contract | PASS | Unknown fields rejected with 422 |
| G28 | Final CI green | PASS | CI #105; 18 tests and compileall passed |
| G29 | Final render green | PASS | Render #5; all ten workflow stages passed |

## Final verified records

### CI

- Run ID: `30658367828`
- Run number: `105`
- Result: `success`
- Tests: `18 passed`
- Python compilation: `success`

### Video

- Run ID: `30658367441`
- Run number: `5`
- Artifact ID: `8804262751`
- Duration: `179.000000 seconds`
- Resolution: `1920×1080`
- Video: `H.264`, 25 fps
- Audio: `AAC`, mean `-20.5 dB`, maximum `-1.4 dB`
- MP4 SHA-256: `a86696e85956d89cd7b859c2ed208d83e8b112613f7bfc5574935976bfedf13c`
- Artifact SHA-256: `7becbc1fec8fcb3de37219ef65b1dae9aa5bffae4b682f3af25ea4c15b87cbf7`
- Detailed evidence: `evidence/video-render-evidence.json`

### Visual inspection

```text
BLACK_FRAMES                 NONE
RECORDING_CONTROLS           HIDDEN
RUNNER_DETECT                PASS
RUNNER_WAIT                  PASS
RUNNER_WRIST_RAISE           PASS
SCRIPTURE_REVEAL             PASS
DEMO_EXCERPT_LABEL           PASS
LIVE_EVIDENCE_WORDING        PASS
TEST_COUNT_DISPLAY           PASS
FINAL_CTA                    PASS
COVER_TITLE_CLIPPING         NONE
COVER_VERSE_CLIPPING         NONE
CAPTIONS_END                 02:59
```

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
- **“Public deployed product”** after G1 is opened logged out.
- **“Kaggle Notebook attached”** only after G7.
- **“YouTube demo published”** only after G13.

Until then, use:

> CI-verified, visually inspected credential-free prototype with official live adapters, strict execution provenance, and a public verification workflow.

## External completion order

1. Verify the Pages URL logged out.
2. Add `GLOO_CLIENT_ID`, `GLOO_CLIENT_SECRET`, and `YVP_APP_KEY`.
3. Run `Capture verified live API evidence` and confirm the JSON commit.
4. Upload the final MP4, captions, and thumbnail to YouTube.
5. Attach the notebook and both PNGs in Kaggle.
6. Paste the writeup and all public links.
7. Submit and capture the final non-draft state.
