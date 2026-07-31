# Three-minute video recording

Use the dedicated page, not the general product page:

- Interactive: `https://o-yutaka.github.io/popopo/video.html?autoplay=1`
- Clean recording mode: `https://o-yutaka.github.io/popopo/video.html?autoplay=1&record=1`
- Local: `python -m http.server 8000`

The page contains ten scenes totaling exactly **179 seconds**, leaving a one-second buffer under the three-minute limit:

| Time | Scene | Visible proof |
|---|---|---|
| 0:00–0:12 | Problem | Difficult moments happen inside digital environments. |
| 0:12–0:26 | Reveal | One shared context engine, not five disconnected apps. |
| 0:26–0:40 | Detect | Heart rate 170, effort 85%, signal detected. No verse yet. |
| 0:40–0:55 | Wait | Consent, privacy and cooldown gate; waiting for recovery. |
| 0:55–1:10 | Reveal | Quiet haptic cue, wrist raise, Scripture card and attribution label. |
| 1:10–1:46 | Technical proof | Local preflight, Gloo OAuth2/V2, YouVersion passage + attribution, native delivery. |
| 1:46–2:10 | Safety | Opt-in, crisis routing, no public auto-posting, no diagnosis or certainty claim. |
| 2:10–2:28 | Scale | Wearable, Gaming, IDE, Social and Creator connectors. |
| 2:28–2:46 | Inspectable proof | Sponsor-call provenance, tests, CI and truthful live-evidence gate. |
| 2:46–2:59 | CTA | Public demo URL, source repository and sponsor names. |

## Recording modes

Interactive mode keeps controls for manual review:

- `Space`: play or pause
- `Left/Right`: move between scenes
- `R`: restart

Recording mode (`record=1`) automatically hides:

- countdown timer
- play/pause button
- keyboard hints
- progress bar

The automated renderer asserts those controls are not visible before recording.

## Capture checklist

- Record at 1920×1080.
- Use `?autoplay=1&record=1` for final capture.
- Confirm the runner sequence visibly progresses through detect → wait → wrist raise → reveal.
- Confirm the final frame shows `o-yutaka.github.io/popopo`.
- Confirm the verse says `Demo excerpt` unless live Bible attribution is available.
- Keep the final upload at 2:59.
- Upload `video/captions.srt`.
- Do not claim live API success until `evidence/live-api-evidence.json` exists.
