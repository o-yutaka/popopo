from __future__ import annotations

import asyncio
import os
from pathlib import Path

import edge_tts

TEXT = Path(os.getenv("NARRATION_TEXT", "video/narration.txt"))
OUTPUT = Path(os.getenv("NARRATION_AUDIO", "build/narration.mp3"))
VOICE = os.getenv("NARRATION_VOICE", "en-US-GuyNeural")
RATE = os.getenv("NARRATION_RATE", "-10%")


async def run() -> None:
    text = TEXT.read_text(encoding="utf-8").strip()
    if not text:
        raise RuntimeError("Narration text is empty")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    await edge_tts.Communicate(text=text, voice=VOICE, rate=RATE).save(str(OUTPUT))
    if not OUTPUT.exists() or OUTPUT.stat().st_size == 0:
        raise RuntimeError("Narration generation produced no audio")
    print(f"Generated {OUTPUT} using {VOICE}")


if __name__ == "__main__":
    asyncio.run(run())
