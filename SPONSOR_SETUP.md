# Sponsor API setup and live proof

This is the shortest path from the repository's deterministic demo to verified live sponsor evidence.

## 1. Gloo AI Studio

1. Open Gloo AI Studio and create or join an organization.
2. Enable API access for the account as required by the hackathon or the current Studio plan.
3. Open **API Credentials**.
4. Create credentials and copy:
   - Client ID
   - Client Secret
5. The implementation exchanges them at:

```text
POST https://platform.ai.gloo.com/oauth2/token
Authorization: Basic base64(client_id:client_secret)
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
scope=api/access
```

6. The resulting short-lived bearer token is used at:

```text
POST https://platform.ai.gloo.com/ai/v2/chat/completions
```

Default model: `gloo-openai-gpt-5-mini`.

## 2. YouVersion Platform

1. Create a developer account and register this application.
2. Create/copy the App Key.
3. Confirm the configured Bible is available to the App Key and accept any required license terms.
4. Default Bible ID: `3034`.
5. The implementation sends:

```text
X-YVP-App-Key: <app key>
```

and retrieves:

```text
GET https://api.youversion.com/v1/bibles/{bible_id}/passages/{usfm_passage_id}
GET https://api.youversion.com/v1/bibles/{bible_id}
```

The second request supplies Bible title, abbreviation, copyright, and attribution metadata.

## 3. Add GitHub repository secrets

In `o-yutaka/popopo`:

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Create exactly:

```text
GLOO_CLIENT_ID
GLOO_CLIENT_SECRET
YVP_APP_KEY
```

Optional repository variables:

```text
GLOO_MODEL=gloo-openai-gpt-5-mini
YOUVERSION_BIBLE_ID=3034
```

Do not put credentials in `.env.example`, source code, issues, screenshots, video, notebook, or the Kaggle writeup.

## 4. Generate verified evidence

```text
GitHub repository
→ Actions
→ Capture verified live API evidence
→ Run workflow
```

The workflow fails unless all of the following are true:

- all three secrets exist
- Gloo OAuth2 token exchange succeeds with `scope=api/access`
- Gloo Completions V2 succeeds
- YouVersion passage retrieval succeeds
- Bible copyright/attribution is returned
- response mode is `live`
- partial configuration is false
- `sponsor_calls_executed` is exactly `["gloo", "youversion"]`
- pseudonymous cooldown enforcement is active

On success it commits:

```text
evidence/live-api-evidence.json
```

The file contains hashes and contracts, but no Client Secret, App Key, bearer token, raw delivery key, or full licensed passage text.

## 5. Generate the video package

```text
GitHub repository
→ Actions
→ Render three-minute submission video
→ Run workflow
→ Download scripture-everywhere-youtube-package
```

Upload:

- `scripture-everywhere-3min.mp4`
- `captions.srt`
- `media/cover.png` as thumbnail

## 6. Kaggle final attachment

Attach or upload:

- `notebooks/scripture_everywhere_submission.ipynb`
- `media/cover.png`
- `media/architecture.png`
- YouTube URL
- public demo URL
- GitHub repository URL
- live evidence URL

Before submission, open every link in a logged-out browser and confirm the Kaggle writeup is submitted rather than left as a draft.
