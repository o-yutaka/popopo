# Scripture Everywhere AI
## One Brain. Every Digital Moment.

## Submission links

- Public demo: https://o-yutaka.github.io/popopo/
- Timed 2:59 judge story: https://o-yutaka.github.io/popopo/video.html?autoplay=1
- Public source: https://github.com/o-yutaka/popopo
- Public notebook: https://github.com/o-yutaka/popopo/blob/main/notebooks/scripture_everywhere_submission.ipynb
- Cover image: https://o-yutaka.github.io/popopo/media/cover.png
- Architecture image: https://o-yutaka.github.io/popopo/media/architecture.png
- Video render proof: https://github.com/o-yutaka/popopo/blob/main/evidence/video-render-evidence.json
- Verified API evidence: https://github.com/o-yutaka/popopo/tree/main/evidence

## Kaggle Writeup — under 500 words

Billions of people spend emotionally significant moments inside digital systems: a runner pushing through exhaustion, a player failing for the eighth time, a developer trapped in a debugging loop, a creator facing a hostile live chat, or a community member expressing distress. Scripture is rarely present in those moments because existing products require users to leave the experience and open another app.

**Scripture Everywhere AI** makes Scripture native to the moment. It is one shared context engine serving five frontiers: wearables, gaming, developer IDEs, social communities, and creator tools.

Our hero experience follows a runner approaching a physiological wall. A wearable connector emits a strict typed event containing heart rate, effort, privacy, consent, and an optional pseudonymous cooldown key. A local preflight gate blocks non-consented or crisis events before any sponsor API receives private context. For an eligible event, the backend exchanges Gloo AI Studio Client ID and Secret credentials for a short-lived OAuth2 token, then calls Gloo Completions V2. Gloo returns the human need, a bounded Scripture theme, an appropriate tone, and whether delivery is safe.

The chosen theme is constrained to an allowlist and resolved to a canonical USFM passage ID. YouVersion Platform API retrieves the passage plus Bible-version attribution. A final delivery policy waits for a recovery window, uses a quiet private haptic cue, and enforces a fifteen-minute cooldown without retaining raw biometrics, message text, or a direct identity.

The innovation is not verse recommendation alone. It is **timing, trust, provenance, and native delivery**. Sensitive social moments never auto-post publicly. The system does not diagnose or claim divine certainty. Every API response reports which sponsor calls actually executed, so demo mode cannot be mistaken for live evidence.

The same intelligence and safety layer also powers a respawn-screen moment after repeated game failure, an IDE margin card after a build loop, a private moderator prompt for sensitive community content, and a creator-only grounding overlay during a toxicity spike. New environments need only emit the common context contract.

The public repository contains an interactive demo, a 179-second interaction-first judge video, a FastAPI backend, strict contracts, official Gloo OAuth2 and Completions V2 integration, canonical YouVersion passage retrieval, attribution, cooldown enforcement, automated tests, CI, Docker support, a complete public notebook, upload-ready media, and a workflow that commits redacted live evidence only after both sponsor APIs succeed.

Scripture Everywhere AI demonstrates a future where the right word meets people inside the moment itself.

## Three-minute video structure

| Time | Story beat |
|---|---|
| 0:00–0:12 | Difficult moments happen inside digital environments. |
| 0:12–0:26 | Reveal one shared context-aware brain. |
| 0:26–0:40 | Detect the runner’s wall without interrupting. |
| 0:40–0:55 | Wait for consent-safe recovery timing. |
| 0:55–1:10 | Quiet haptic cue → wrist raise → Scripture reveal. |
| 1:10–1:46 | Local preflight → Gloo OAuth2/V2 → YouVersion → delivery. |
| 1:46–2:10 | Consent, crisis, privacy and no-auto-post safety gates. |
| 2:10–2:28 | Reveal Gaming, IDE, Social and Creator connectors. |
| 2:28–2:46 | Show strict execution provenance, tests and evidence gate. |
| 2:46–2:59 | Public demo CTA and sponsor attribution. |

The renderer enforces a clean 1920×1080 H.264/AAC MP4 under three minutes. Recording mode hides timer, controls, hints and progress UI.

## Final submission gate

### Completed in GitHub

- [x] Public repository
- [x] Working public-demo source
- [x] Automatic GitHub Pages deployment workflow
- [x] 179-second timeline with one-second upload buffer
- [x] Detect → wait → wrist-raise → reveal runner interaction
- [x] Clean recording mode without timer, pause button or keyboard hints
- [x] Public demo CTA and repository link in final frame
- [x] Truthful dynamic live-evidence gate
- [x] Captions, YouTube description, thumbnail, and architecture media package
- [x] Kaggle writeup under 500 words
- [x] Complete public Kaggle notebook
- [x] 1600×900 PNG cover and architecture images
- [x] Official Gloo OAuth2 client-credentials and Completions V2 adapter
- [x] Official YouVersion passage and attribution adapter
- [x] Local consent/crisis preflight before external calls
- [x] Delivery timing and pseudonymous cooldown enforcement
- [x] Automated API, OAuth and submission-quality tests
- [x] Redacted live API evidence workflow

### Requires account credentials or manual upload

- [ ] Confirm GitHub Pages URL loads publicly in a logged-out browser
- [ ] Add `GLOO_CLIENT_ID`, `GLOO_CLIENT_SECRET`, and `YVP_APP_KEY` repository secrets
- [ ] Confirm the selected YouVersion Bible license is available to the App Key
- [ ] Run live-evidence workflow and confirm `evidence/live-api-evidence.json` exists
- [ ] Upload the generated MP4 and `video/captions.srt` to YouTube as public or unlisted
- [ ] Attach the notebook to the Kaggle submission
- [ ] Upload `media/cover.png` and `media/architecture.png` to Media Gallery
- [ ] Add the YouTube URL to the Kaggle writeup
- [ ] Submit the writeup; do not leave it as draft

## Truth rule

Do not state that both sponsor APIs ran live until `evidence/live-api-evidence.json` exists and its `sponsor_calls_executed` value is exactly `["gloo", "youversion"]`. Demo mode is a reproducible product demonstration; the evidence file is the separate execution proof.
