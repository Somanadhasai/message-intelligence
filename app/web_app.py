import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


# ===============================================================
# PROJECT PATHS
# ===============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATE_DIR = BASE_DIR / "templates"


# ===============================================================
# FASTAPI APPLICATION
# ===============================================================

app = FastAPI(
    title="Message Intelligence",
    description="Local message classification and task/event extraction system",
    version="1.0.0",
)

templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


# ===============================================================
# JSON LOADER
# ===============================================================

def load_json(filename):
    """
    Load an output JSON file.

    Returns an empty list when the file does not exist.
    """

    filepath = OUTPUT_DIR / filename

    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return []


# ===============================================================
# SAFE CLOUD DEMO DATA
# ===============================================================

DEMO_CATEGORY_COUNTS = {
    "action_required": 200,
    "general_information": 240,
    "meeting_or_event": 170,
    "personal_information": 90,
    "promotional": 110,
    "sensitive_information": 90,
}


DEMO_MANDATORY_RESULTS = [
    {
        "message_id": "MSG_0001",
        "category": "meeting_or_event",
        "confidence": 0.67,
        "reason": "Classified as meeting or event language based on 2 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0002",
        "category": "action_required",
        "confidence": 0.98,
        "reason": "Classified as action/request language based on 1 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0003",
        "category": "general_information",
        "confidence": 0.98,
        "reason": "Classified as general-information language based on 1 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0004",
        "category": "general_information",
        "confidence": 0.98,
        "reason": "Classified as general-information language based on 2 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0005",
        "category": "sensitive_information",
        "confidence": 0.99,
        "reason": "Sensitive information detected: home_address.",
        "is_sensitive": True,
        "sensitivity_type": "home_address",
        "risk": "medium",
        "recommended_action": "ask_for_confirmation",
    },
    {
        "message_id": "MSG_0006",
        "category": "general_information",
        "confidence": 0.60,
        "reason": "No strong action, meeting, personal, promotional, or sensitive pattern was detected.",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0007",
        "category": "action_required",
        "confidence": 0.67,
        "reason": "Classified as action/request language based on 2 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0009",
        "category": "personal_information",
        "confidence": 0.98,
        "reason": "Classified as personal-information language based on 2 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0012",
        "category": "general_information",
        "confidence": 0.98,
        "reason": "Classified as general-information language based on 1 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0013",
        "category": "sensitive_information",
        "confidence": 0.99,
        "reason": "Sensitive information detected: card_number.",
        "is_sensitive": True,
        "sensitivity_type": "card_number",
        "risk": "high",
        "recommended_action": "do_not_store",
    },
    {
        "message_id": "MSG_0014",
        "category": "promotional",
        "confidence": 0.98,
        "reason": "Classified as promotional language based on 5 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0015",
        "category": "promotional",
        "confidence": 0.98,
        "reason": "Classified as promotional language based on 5 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0016",
        "category": "personal_information",
        "confidence": 0.60,
        "reason": "Classified as personal-information language based on 1 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0024",
        "category": "meeting_or_event",
        "confidence": 0.67,
        "reason": "Classified as meeting or event language based on 2 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
    {
        "message_id": "MSG_0037",
        "category": "general_information",
        "confidence": 0.98,
        "reason": "Classified as general-information language based on 1 matching pattern(s).",
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "recommended_action": None,
    },
]


# ===============================================================
# DASHBOARD
# ===============================================================

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):

    classifications = load_json(
        "classification_results.json"
    )

    tasks_events = load_json(
        "task_event_results.json"
    )

    sensitive = load_json(
        "sensitive_results.json"
    )

    mandatory = load_json(
        "mandatory_results.json"
    )

    # -----------------------------------------------------------
    # Detect whether real local output files are available
    # -----------------------------------------------------------

    cloud_demo_mode = not bool(classifications)

    # -----------------------------------------------------------
    # Use real output data when available
    # Otherwise use safe demonstration statistics.
    #
    # No raw messages or sensitive values are included.
    # -----------------------------------------------------------

    if cloud_demo_mode:

        category_counts = DEMO_CATEGORY_COUNTS

        total_messages = sum(
            DEMO_CATEGORY_COUNTS.values()
        )

        task_count = 150
        event_count = 190
        sensitive_count = 90
        mandatory_count = 15

        low_confidence_count = 326

        mandatory_results = DEMO_MANDATORY_RESULTS

    else:

        # -------------------------------------------------------
        # Category counts
        # -------------------------------------------------------

        category_counts = {}

        for item in classifications:

            category = item.get(
                "category",
                "general_information"
            )

            category_counts[category] = (
                category_counts.get(category, 0) + 1
            )

        # -------------------------------------------------------
        # Task/event counts
        # -------------------------------------------------------

        task_count = sum(
            1
            for item in tasks_events
            if item.get("type") == "task"
        )

        event_count = sum(
            1
            for item in tasks_events
            if item.get("type") == "meeting_or_event"
        )

        # -------------------------------------------------------
        # Low confidence messages
        # -------------------------------------------------------

        low_confidence = [
            item
            for item in classifications
            if float(item.get("confidence", 1)) <= 0.67
        ]

        low_confidence_count = len(
            low_confidence
        )

        total_messages = len(
            classifications
        )

        sensitive_count = len(
            sensitive
        )

        mandatory_count = len(
            mandatory
        )

        mandatory_results = mandatory

    # -----------------------------------------------------------
    # Render dashboard
    # -----------------------------------------------------------

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "total_messages": total_messages,

            "category_counts": category_counts,

            "task_count": task_count,

            "event_count": event_count,

            "sensitive_count": sensitive_count,

            "mandatory_count": mandatory_count,

            "low_confidence_count": low_confidence_count,

            "mandatory_results": mandatory_results,

            "cloud_demo_mode": cloud_demo_mode,
        },
    )


# ===============================================================
# HEALTH CHECK
# ===============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "message-intelligence",
    }