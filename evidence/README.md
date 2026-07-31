# Verified live API evidence

This directory intentionally does **not** contain fabricated API output.

To create public, redacted proof that both sponsor APIs were used:

1. Add repository Actions secrets:
   - `GLOO_CLIENT_ID`
   - `GLOO_CLIENT_SECRET`
   - `YVP_APP_KEY`
2. Optional repository variables:
   - `GLOO_MODEL` (defaults to `gloo-openai-gpt-5-mini`)
   - `YOUVERSION_BIBLE_ID` (defaults to `3034`)
3. Run the **Capture verified live API evidence** workflow.
4. The workflow exchanges the Gloo Client ID and Secret for a short-lived OAuth2 bearer token using `scope=api/access`.
5. It starts the real backend, submits the wearable hero event, requires `mode=live`, requires `gloo_auth_mode=oauth2_client_credentials`, requires `scripture.source=youversion`, removes the licensed passage text, and commits `live-api-evidence.json`.

The committed proof contains:

- UTC capture timestamp
- redacted request and response contracts
- Gloo/YouVersion configured flags
- Gloo auth mode and API version
- selected theme and canonical passage ID
- SHA-256 and length of the returned passage text
- no Client Secret, App Key, bearer token, authorization headers, or full licensed Scripture text

A missing `live-api-evidence.json` means the live proof gate is still open.
