# Scripture Everywhere AI

**One Brain. Every Digital Moment.**

A working hackathon prototype for **Scripture in New Frontiers**. It detects meaningful moments across gaming, wearables, coding, social spaces, and creator tools, then uses **Gloo AI Studio** to understand the human need and **YouVersion Platform API** to retrieve Scripture that fits the moment.

## Why this matters

People already live inside games, workouts, IDEs, social feeds, and creator tools. Scripture Everywhere AI does not interrupt those spaces with a generic pop-up. It turns live context into a quiet, native moment of encouragement.

## Demo experiences

- Gaming: repeated failure or team conflict → perseverance and patience
- Wearables / fitness: peak effort, recovery, or high stress → strength and peace
- Developer IDE: repeated build failures and long focus sessions → endurance and wisdom
- Social: harmful or distressed conversation → safe, non-preachy support
- Creator / streaming: pressure or toxic chat → private grounding for the creator

## Architecture

```text
Connector Event
  ↓
Context Normalizer
  ↓
Gloo AI Studio: need/theme/safety inference
  ↓
YouVersion Platform API: Scripture retrieval
  ↓
Delivery Policy: timing, tone, cooldown, privacy
  ↓
Native UI card / wearable cue / IDE margin / creator overlay
```

## Run locally

```bash
python -m http.server 8000
```

Open `http://localhost:8000`.

For the API service:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload
```

## API configuration

```env
GLOO_API_KEY=replace_me
GLOO_BASE_URL=https://api.gloo.ai
GLOO_MODEL=replace_with_available_model
YOUVERSION_API_KEY=replace_me
YOUVERSION_BASE_URL=https://api.youversion.com
YOUVERSION_BIBLE_ID=replace_with_bible_id
```

The repository contains a deterministic demo fallback so judges can experience the product even when API credentials are not configured. Live mode is enabled only when both required API keys are present.

## Repository map

```text
index.html                 interactive public demo
app.js                     five-frontier simulation and API client
styles.css                 responsive UI
backend/app.py             FastAPI orchestration service
backend/clients.py         Gloo + YouVersion adapters
backend/models.py          typed contracts
backend/requirements.txt   backend dependencies
notebooks/demo.ipynb       public Kaggle notebook starter
SUBMISSION.md              writeup and 3-minute video script
```

## Safety and privacy

- No diagnosis or spiritual certainty claims
- No public intervention for sensitive social content by default
- Rate limits and cooldowns prevent notification fatigue
- Raw biometrics and private text are not retained by the demo
- Gloo safety result can suppress delivery
- Users can dismiss, pause, or disable every connector

## Hackathon proof

The backend calls both required APIs in sequence:

1. Gloo AI Studio converts normalized context into a structured need, theme, tone, and safety decision.
2. YouVersion Platform retrieves Scripture using that theme and configured Bible/language.
3. A delivery policy selects the correct native presentation.

See [`SUBMISSION.md`](SUBMISSION.md) for the Kaggle writeup draft and video shot list.

## License

MIT. Scripture text and API-provided content remain subject to the respective platform terms.
