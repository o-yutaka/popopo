# Verified live API evidence

This directory intentionally does **not** contain fabricated API output.

To create public, redacted proof that both sponsor APIs were used:

1. Add repository Actions secrets: `GLOO_API_KEY`, `GLOO_BASE_URL`, `GLOO_MODEL`, optional `GLOO_CHAT_PATH`, `YVP_APP_KEY`, `YOUVERSION_BASE_URL`, and `YOUVERSION_BIBLE_ID`.
2. Run the **Capture verified live API evidence** workflow.
3. The workflow starts the real backend, submits the wearable hero event, requires `mode=live`, requires `scripture.source=youversion`, removes the licensed passage text, and commits `live-api-evidence.json`.

The committed proof contains:

- UTC capture timestamp
- redacted request and response contracts
- Gloo/YouVersion configured flags
- selected theme and passage ID
- SHA-256 and length of the returned passage text
- no API keys, authorization headers, or full licensed Scripture text

A missing `live-api-evidence.json` means the live proof gate is still open.
