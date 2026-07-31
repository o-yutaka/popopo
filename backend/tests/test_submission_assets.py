import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_video_timeline_is_under_three_minutes_with_buffer():
    html = (ROOT / "video.html").read_text(encoding="utf-8")
    durations = [int(value) for value in re.findall(r'data-duration="(\d+)"', html)]
    assert len(durations) == 10
    assert sum(durations) == 179
    assert "if(total!==179)" in html
    assert "02:59" in html


def test_video_has_native_interaction_and_clean_record_mode():
    html = (ROOT / "video.html").read_text(encoding="utf-8")
    assert "SIGNAL DETECTED" in html
    assert "WAITING<br>FOR RECOVERY" in html
    assert "WRIST RAISED" in html
    assert "record-mode" in html
    assert ".record-mode .timer" in html
    assert ".record-mode .bottom" in html
    assert "o-yutaka.github.io/popopo" in html
    assert "Demo excerpt" in html


def test_video_proof_is_truthful_and_provenance_aware():
    html = (ROOT / "video.html").read_text(encoding="utf-8")
    assert "verified only when:" in html
    assert 'sponsor_calls_executed = ["gloo", "youversion"]' in html
    assert "18 tests passed" in html
    assert "LIVE SPONSOR PIPELINE VERIFIED" in html
    assert "evidence/live-api-evidence.json" in html
    assert "Demo mode remains visibly separate" in html


def test_kaggle_notebook_is_valid_v4_json():
    path = ROOT / "notebooks" / "scripture_everywhere_submission.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) >= 10
    joined = "\n".join(
        line
        for cell in notebook["cells"]
        for line in cell.get("source", [])
    )
    assert "Gloo AI Studio" in joined
    assert "YouVersion Platform" in joined
    assert "user_opted_in" in joined


def test_kaggle_writeup_is_under_500_words():
    text = (ROOT / "SUBMISSION.md").read_text(encoding="utf-8")
    writeup = text.split("## Kaggle Writeup — under 500 words", 1)[1].split(
        "## Three-minute video structure", 1
    )[0]
    words = re.findall(r"\b[\w’'-]+\b", writeup)
    assert 250 <= len(words) <= 500, len(words)


def test_media_gallery_sources_are_1600_by_900():
    for name in ("cover.svg", "architecture.svg"):
        svg = (ROOT / "media" / name).read_text(encoding="utf-8")
        assert 'width="1600"' in svg
        assert 'height="900"' in svg
        assert "<title" in svg
        assert "<desc" in svg
    cover = (ROOT / "media" / "cover.svg").read_text(encoding="utf-8")
    assert "Every Digital\n" not in cover
    assert "in the Lord will renew" not in cover
    assert "in the Lord will" in cover
    assert "renew their strength." in cover
    assert "Demo excerpt" in cover


def test_judge_links_and_truth_gate_exist():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    submission = (ROOT / "SUBMISSION.md").read_text(encoding="utf-8")
    assert "https://o-yutaka.github.io/popopo/" in readme
    assert "evidence/live-api-evidence.json" in submission
    assert "Do not state that both sponsor APIs ran live" in submission


def test_required_submission_files_exist():
    required = [
        "index.html",
        "video.html",
        "README.md",
        "SUBMISSION.md",
        "AUDIT.md",
        "VIDEO_RECORDING.md",
        "video/captions.srt",
        "video/narration.txt",
        "media/cover.svg",
        "media/architecture.svg",
        "notebooks/scripture_everywhere_submission.ipynb",
        ".github/workflows/pages.yml",
        ".github/workflows/render-video.yml",
        ".github/workflows/live-evidence.yml",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing, missing
