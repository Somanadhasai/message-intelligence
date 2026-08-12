import re
from datetime import datetime


# -------------------------------------------------------------------
# Date and time patterns
# -------------------------------------------------------------------

DATE_PATTERN = re.compile(
    r"\b(20\d{2}-\d{2}-\d{2})\b"
)

TIME_PATTERN = re.compile(
    r"\b([01]?\d|2[0-3]):([0-5]\d)\b"
)


# -------------------------------------------------------------------
# Person extraction
# -------------------------------------------------------------------

PERSON_PATTERN = re.compile(
    r"\b(?:with|for|from|asked by|contact)\s+"
    r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
)


# -------------------------------------------------------------------
# Priority signals
# -------------------------------------------------------------------

HIGH_PRIORITY_KEYWORDS = [
    "urgent",
    "immediately",
    "as soon as possible",
    "critical",
    "important",
    "deadline",
    "due",
]

LOW_PRIORITY_KEYWORDS = [
    "optional",
    "if possible",
    "whenever",
    "when you are free",
]


# -------------------------------------------------------------------
# Task signals
# -------------------------------------------------------------------

TASK_PATTERNS = [
    r"please\s+(?:submit|send|reply|review|complete|confirm|call|update|upload|verify)\b",
    r"don't forget to\s+(.+?)(?=;|\.|$)",
    r"do not forget to\s+(.+?)(?=;|\.|$)",
    r"i need you to\s+(.+?)(?=\.|$)",
    r"can you\s+(?:send|update|complete|review|submit|call)\b",
    r"you need to\s+(.+?)(?=\.|$)",
    r"remember to\s+(.+?)(?=\.|$)",
    r"\brenew\s+.+?\s+by\s+20\d{2}-\d{2}-\d{2}",
]


# -------------------------------------------------------------------
# Meeting/event signals
# -------------------------------------------------------------------

EVENT_PATTERNS = [
    "meeting",
    "meet",
    "appointment",
    "orientation",
    "workshop",
    "seminar",
    "webinar",
    "sprint planning",
    "project review",
    "product demo",
    "team stand-up",
    "calendar update",
    "family dinner",
    "interview",
]


def extract_date(text: str):
    """Extract an explicit YYYY-MM-DD date."""

    match = DATE_PATTERN.search(text)

    if match:
        return match.group(1)

    return None


def extract_time(text: str):
    """Extract an explicit HH:MM time."""

    match = TIME_PATTERN.search(text)

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))

        return f"{hour:02d}:{minute:02d}"

    return None


def extract_person(text: str):
    """Extract a person name when explicitly associated with the task/event."""

    match = PERSON_PATTERN.search(text)

    if match:
        return match.group(1)

    return None


def determine_priority(text: str):
    """
    Determine priority from explicit urgency or deadline signals.

    We do not invent priority when there is no clear signal.
    """

    lower_text = text.lower()

    # Explicit high-priority signals
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in lower_text:
            return "high"

    # A specific explicit deadline is a strong priority signal.
    if re.search(
        r"\b(?:by|before|due(?:\s+on)?)\s+20\d{2}-\d{2}-\d{2}\b",
        lower_text
    ):
        return "high"

    # Explicit low-priority signals
    for keyword in LOW_PRIORITY_KEYWORDS:
        if keyword in lower_text:
            return "low"

    return "medium"


def extract_task_title(text: str):
    """Generate a short task title from common task wording."""

    patterns = [
        r"please\s+(submit|send|reply|review|complete|confirm|call|update|upload|verify)\s+(.+?)(?:\s+by\s+20\d{2}-\d{2}-\d{2}|\.|$)",
        r"don't forget to\s+(.+?)(?:;|\s+deadline|\s+by\s+20\d{2}-\d{2}-\d{2}|\.|$)",
        r"do not forget to\s+(.+?)(?:;|\s+deadline|\s+by\s+20\d{2}-\d{2}-\d{2}|\.|$)",
        r"i need you to\s+(.+?)(?:\s+by\s+20\d{2}-\d{2}-\d{2}|\.|$)",
        r"remember to\s+(.+?)(?:\s+by\s+20\d{2}-\d{2}-\d{2}|\.|$)",
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            continue

        groups = match.groups()

        if len(groups) == 2:
            action = groups[0]
            target = groups[1]

            return f"{action.capitalize()} {target.strip()}"

        return groups[0].strip().capitalize()

    return "Task"


def extract_event_title(text: str):
    """Generate a simple event title based on explicit event wording."""

    lower_text = text.lower()

    title_patterns = [
        ("project review", "Project Review"),
        ("product demo", "Product Demo"),
        ("sprint planning", "Sprint Planning"),
        ("doctor appointment", "Doctor Appointment"),
        ("internship orientation", "Internship Orientation"),
        ("ai workshop", "AI Workshop"),
        ("team stand-up", "Team Stand-up"),
        ("college seminar", "College Seminar"),
        ("placement briefing", "Placement Briefing"),
        ("family dinner", "Family Dinner"),
        ("webinar", "Webinar"),
        ("meeting", "Meeting"),
        ("meet", "Meeting"),
        ("appointment", "Appointment"),
    ]

    for keyword, title in title_patterns:

        if keyword in lower_text:
            return title

    return "Event"


def is_task(text: str):
    """Determine whether a message contains an actionable task."""

    lower_text = text.lower()

    for pattern in TASK_PATTERNS:

        if re.search(pattern, lower_text, re.IGNORECASE):
            return True

    return False


def is_event(text: str):
    """Determine whether a message contains a meeting/event."""

    lower_text = text.lower()

    return any(
        keyword in lower_text
        for keyword in EVENT_PATTERNS
    )


def extract_item(
    message_id: str,
    timestamp: str,
    sender: str,
    message: str
):
    """
    Extract a task or event from one message.

    Returns None when the message does not contain
    a recognizable task or event.
    """

    task = is_task(message)
    event = is_event(message)

    # ---------------------------------------------------------------
    # Event
    # ---------------------------------------------------------------

    if event:

        date = extract_date(message)
        time = extract_time(message)
        person = extract_person(message)

        return {
            "item_id": None,
            "type": "meeting_or_event",
            "title": extract_event_title(message),
            "description": message,
            "date": date,
            "deadline": None,
            "time": time,
            "person": person,
            "priority": determine_priority(message),
            "source_message_id": message_id,
        }

    # ---------------------------------------------------------------
    # Task
    # ---------------------------------------------------------------

    if task:

        date = extract_date(message)
        time = extract_time(message)
        person = extract_person(message)

        return {
            "item_id": None,
            "type": "task",
            "title": extract_task_title(message),
            "description": message,
            "date": None,
            "deadline": date,
            "time": time,
            "person": person,
            "priority": determine_priority(message),
            "source_message_id": message_id,
        }

    return None