import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


# ---------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "outputs"
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


# ---------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------

app = FastAPI(
    title="Message Intelligence",
    description="Local message classification and task/event extraction system",
    version="1.0.0",
)


# ---------------------------------------------------------------
# Serve static files
# ---------------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)


templates = Jinja2Templates(
    directory=str(TEMPLATE_DIR)
)


# ---------------------------------------------------------------
# JSON loader
# ---------------------------------------------------------------

def load_json(filename):
    filepath = OUTPUT_DIR / filename

    if not filepath.exists():
        return []

    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------

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
    # Category counts
    # -----------------------------------------------------------

    category_counts = {}

    for item in classifications:

        category = item["category"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    # -----------------------------------------------------------
    # Task/event counts
    # -----------------------------------------------------------

    task_count = sum(
        1
        for item in tasks_events
        if item["type"] == "task"
    )

    event_count = sum(
        1
        for item in tasks_events
        if item["type"] == "meeting_or_event"
    )

    # -----------------------------------------------------------
    # Low confidence messages
    # -----------------------------------------------------------

    low_confidence = [
        item
        for item in classifications
        if item["confidence"] <= 0.67
    ]

    # -----------------------------------------------------------
    # Render dashboard
    # -----------------------------------------------------------

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "total_messages": len(classifications),
            "category_counts": category_counts,
            "task_count": task_count,
            "event_count": event_count,
            "sensitive_count": len(sensitive),
            "mandatory_count": len(mandatory),
            "low_confidence_count": len(low_confidence),
            "mandatory_results": mandatory,
        },
    )


# ---------------------------------------------------------------
# Health check
# ---------------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "message-intelligence",
    }