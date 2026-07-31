# Scripture Everywhere AI
## One Brain. Every Digital Moment.

### Kaggle Writeup Draft

Billions of people spend their most emotionally charged moments inside digital systems: a runner pushing through exhaustion, a player failing for the eighth time, a developer stuck in a three-hour debugging loop, a creator facing a hostile live chat, or a community member expressing distress. Scripture is rarely present in those moments because existing products require users to leave the environment and open a separate Bible app.

Scripture Everywhere AI makes Scripture native to the moment. It is a shared context engine that receives signals from five frontiers—gaming, wearables, developer IDEs, social communities, and creator tools—then converts them into one normalized event contract.

The backend uses Gloo AI Studio to infer four things: the human need, a Scripture theme, an appropriate tone, and whether delivery is safe. That structured output is passed to the YouVersion Platform API, which retrieves Scripture in the configured Bible and language. A final delivery policy chooses the correct surface: a respawn screen after combat, a quiet wearable cue during recovery, an IDE margin card after a failed build, a private moderator prompt for sensitive social content, or a creator-only overlay during a stream.

The key innovation is not verse recommendation alone. It is timing, privacy, and native delivery. The system avoids diagnosis, never claims divine certainty, suppresses unsafe output, applies cooldowns, and defaults sensitive social moments to private human review instead of public auto-posting.

Our interactive demo shows the same AI brain adapting across all five environments. The repository includes a working FastAPI orchestration service, typed data contracts, separate Gloo and YouVersion clients, deterministic credential-free fallback for judging, and a responsive public demo. When both API keys are configured, the service switches automatically from demo mode to live mode.

This architecture is designed for scale: any new frontier only needs a connector that emits the common context schema. The intelligence, safety, Scripture retrieval, and delivery policy remain shared.

Scripture Everywhere AI demonstrates a future where people do not have to leave the spaces they love to encounter Scripture. The right word can meet them inside the moment itself.

### Three-Minute Video Script

**0:00–0:18 — Problem**
Show rapid cuts: runner, failed game, red build output, toxic chat, streamer under pressure. Voiceover: “People already live here. But when the moment gets hard, Scripture is somewhere else.”

**0:18–0:38 — Reveal**
Open the demo hero. “Scripture Everywhere AI is one context-aware brain for every digital frontier.”

**0:38–1:45 — Product Story**
Use “Play full story.” Show all five scenes. Pause briefly on wearable, gaming, IDE, social privacy suppression, and creator overlay.

**1:45–2:20 — Technical Proof**
Show the live trace: Context → Gloo AI → YouVersion → Delivery. Cut to `backend/clients.py`, `backend/app.py`, and `/health` response.

**2:20–2:42 — Safety**
Show private social delivery, cooldown, user control, no diagnosis, and suppression gate.

**2:42–3:00 — Vision**
Show connector expansion: Minecraft, Discord, VS Code, Apple Watch, OBS. End: “Scripture should not wait in another app. It should meet people where life is already happening.”

### Submission Checklist

- [ ] Public Kaggle Writeup under 500 words
- [ ] Cover image attached
- [ ] Public Kaggle Notebook attached
- [ ] YouTube demo, 3 minutes or less
- [ ] Public project link: https://github.com/o-yutaka/popopo
- [ ] Final Writeup submitted, not left as draft
