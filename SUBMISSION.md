# Scripture Everywhere AI
## One Brain. Every Digital Moment.

## Submission links

- Public demo: https://o-yutaka.github.io/popopo/
- Timed three-minute experience: https://o-yutaka.github.io/popopo/video.html?autoplay=1
- Public source: https://github.com/o-yutaka/popopo
- Public notebook: https://github.com/o-yutaka/popopo/blob/main/notebooks/scripture_everywhere_submission.ipynb
- Cover image: https://o-yutaka.github.io/popopo/media/cover.svg
- Architecture image: https://o-yutaka.github.io/popopo/media/architecture.svg
- Verified API evidence: https://github.com/o-yutaka/popopo/tree/main/evidence

## Kaggle Writeup — under 500 words

Billions of people spend emotionally significant moments inside digital systems: a runner pushing through exhaustion, a player failing for the eighth time, a developer trapped in a debugging loop, a creator facing a hostile live chat, or a community member expressing distress. Scripture is rarely present in those moments because existing products require users to leave the experience and open another app.

**Scripture Everywhere AI** makes Scripture native to the moment. It is one shared context engine serving five frontiers: wearables, gaming, developer IDEs, social communities, and creator tools.

Our hero experience follows a runner approaching a physiological wall. A wearable connector emits a typed event containing heart rate, effort, timing, privacy, and consent. Gloo AI Studio converts that context into a structured decision: the human need, a bounded Scripture theme, an appropriate tone, and whether delivery is safe. The chosen theme is constrained to an allowlist and resolved to a canonical USFM passage ID. YouVersion Platform API then retrieves the Scripture passage in the configured Bible and language. A final delivery policy waits for a recovery window and uses a quiet private haptic cue rather than interrupting the run.

The innovation is not verse recommendation alone. It is **timing, trust, and native delivery**. Explicit opt-in is required. Crisis signals suppress normal automated delivery and route to human support. Sensitive social moments never auto-post publicly. The system does not diagnose or claim divine certainty, and cooldowns prevent notification fatigue.

The same intelligence and safety layer also powers a respawn-screen moment after repeated game failure, an IDE margin card after a build loop, a private moderator prompt for sensitive community content, and a creator-only grounding overlay during a toxicity spike. New environments need only emit the common context contract.

The public repository contains a responsive interactive demo, an exact three-minute recording experience, a FastAPI backend, typed contracts, separate Gloo and YouVersion clients, tests, CI, Docker support, a complete public notebook, and a workflow that records redacted live evidence only after both sponsor APIs succeed.

Scripture Everywhere AI demonstrates a future where people do not have to leave the spaces they love to encounter Scripture. The right word can meet them inside the moment itself.

## Three-minute video structure

| Time | Story beat |
|---|---|
| 0:00–0:15 | Difficult moments happen inside digital environments. |
| 0:15–0:35 | Reveal one shared context-aware brain. |
| 0:35–1:20 | Runner reaches the wall; safe recovery delivery appears. |
| 1:20–2:00 | Context → Gloo → YouVersion → Delivery technical proof. |
| 2:00–2:25 | Consent, crisis, privacy and no-auto-post safety gates. |
| 2:25–2:45 | Reveal Gaming, IDE, Social and Creator connectors. |
| 2:45–2:55 | Show backend, tests, notebook and evidence. |
| 2:55–3:00 | “The right word, inside the moment.” |

Use [`VIDEO_RECORDING.md`](VIDEO_RECORDING.md) and record `video.html?autoplay=1`.

## Final submission gate

### Completed in GitHub

- [x] Public repository
- [x] Working public-demo source
- [x] Automatic GitHub Pages deployment workflow
- [x] Exact 180-second video experience
- [x] Kaggle writeup under 500 words
- [x] Complete public Kaggle notebook
- [x] 1600×900 cover image
- [x] Architecture Media Gallery image
- [x] FastAPI backend using both sponsor adapters
- [x] Automated tests and CI
- [x] Consent, crisis and public-social safety gates
- [x] Redacted live API evidence workflow

### Requires account credentials or manual upload

- [ ] Confirm GitHub Pages URL loads publicly
- [ ] Add Gloo and YouVersion repository secrets
- [ ] Run live-evidence workflow and confirm `evidence/live-api-evidence.json` exists
- [ ] Record the supplied 180-second experience
- [ ] Upload video to YouTube as public or unlisted
- [ ] Create or open the Kaggle writeup
- [ ] Attach the notebook to the Kaggle submission
- [ ] Upload `media/cover.svg` and `media/architecture.svg` to Media Gallery
- [ ] Replace submission video placeholder with the YouTube URL
- [ ] Submit the writeup; do not leave it as draft

## Truth rule

Do not state that both sponsor APIs ran live until `evidence/live-api-evidence.json` exists. Demo mode is a reproducible product demonstration; the evidence file is the separate execution proof.
