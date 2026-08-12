from pathlib import Path
import json

from app.classifier import classify_message
from app.extractor import extract_item
from app.sensitive_detector import detect_sensitive_information


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"


def test_sensitive_detection():
    result = detect_sensitive_information("Your OTP is 123456")

    assert result["is_sensitive"] is True
    assert result["sensitivity_type"] == "one_time_password"
    assert "123456" not in result["masked_text"]


def test_classifier_action():
    result = classify_message(
        "Please submit the weekly report by 2026-09-10.",
        "Aarav"
    )

    assert result["category"] == "action_required"
    assert result["confidence"] >= 0.6


def test_classifier_sensitive():
    result = classify_message(
        "Your OTP is 123456.",
        "Ananya"
    )

    assert result["category"] == "sensitive_information"


def test_task_extraction():
    result = extract_item(
        "TEST_001",
        "2026-08-12 10:00:00",
        "Aarav",
        "Please submit the weekly report by 2026-09-10."
    )

    assert result is not None
    assert result["type"] == "task"
    assert result["deadline"] == "2026-09-10"
    assert result["title"] == "Submit the weekly report"


def test_event_extraction():
    result = extract_item(
        "TEST_002",
        "2026-08-12 10:00:00",
        "Aarav",
        "The project review is scheduled for 2026-09-12 at 15:00 in Meeting Room A."
    )

    assert result is not None
    assert result["type"] == "meeting_or_event"
    assert result["date"] == "2026-09-12"
    assert result["time"] == "15:00"


def test_output_files_exist():
    required_files = [
        "classification_results.json",
        "task_event_results.json",
        "sensitive_results.json",
        "mandatory_results.json",
    ]

    for filename in required_files:
        filepath = OUTPUT_DIR / filename
        assert filepath.exists(), f"Missing output: {filename}"


def test_output_counts():
    classification = json.load(
        open(OUTPUT_DIR / "classification_results.json", encoding="utf-8")
    )

    task_events = json.load(
        open(OUTPUT_DIR / "task_event_results.json", encoding="utf-8")
    )

    sensitive = json.load(
        open(OUTPUT_DIR / "sensitive_results.json", encoding="utf-8")
    )

    mandatory = json.load(
        open(OUTPUT_DIR / "mandatory_results.json", encoding="utf-8")
    )

    assert len(classification) == 900
    assert len(task_events) == 340
    assert len(sensitive) == 90
    assert len(mandatory) == 15