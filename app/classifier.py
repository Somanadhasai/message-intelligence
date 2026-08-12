import re

from app.sensitive_detector import detect_sensitive_information


# -------------------------------------------------------------------
# Keyword groups used by the local explainable classifier
# -------------------------------------------------------------------

ACTION_KEYWORDS = [
    "please submit",
    "please send",
    "please reply",
    "please review",
    "please complete",
    "please confirm",
    "please call",
    "please update",
    "please upload",
    "please verify",
    "don't forget",
    "do not forget",
    "i need you to",
    "can you send",
    "can you update",
    "can you complete",
    "renew",
    "deadline",
    "due on",
    "before",
    "by 2026",
]

MEETING_KEYWORDS = [
    "meeting",
    "meet",
    "scheduled for",
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
    "interview slot",
]

PROMOTIONAL_KEYWORDS = [
    "sale",
    "discount",
    "offer",
    "limited-time",
    "cashback",
    "coupon",
    "reward points",
    "save",
    "buy one",
    "get one free",
    "upgrade your subscription",
    "you may like our new",
]

PERSONAL_KEYWORDS = [
    "my favourite",
    "my favorite",
    "my t-shirt size",
    "i prefer",
    "i usually",
    "i am vegetarian",
    "i'm vegetarian",
    "i drink",
    "my emergency contact",
    "for my profile",
    "i live near",
    "dark mode",
]

GENERAL_KEYWORDS = [
    "quick update",
    "for today",
    "fyi",
    "just checking",
    "one more thing",
    "the new python version",
    "training material",
    "report template",
    "webinar recording",
    "office wi-fi",
    "building entrance",
    "weather forecast",
    "shuttle leaves",
    "public holiday",
]


def count_keyword_matches(text: str, keywords: list[str]) -> int:
    """Count how many keyword/phrase patterns occur in the message."""

    text = text.lower()

    return sum(1 for keyword in keywords if keyword in text)


def classify_message(message: str, sender: str = "") -> dict:
    """
    Classify a message into one of the six assignment categories.

    Sensitive information has highest priority.
    The remaining categories use transparent keyword scoring.
    """

    # ---------------------------------------------------------------
    # 1. Sensitive information has highest priority
    # ---------------------------------------------------------------

    sensitive_result = detect_sensitive_information(message)

    if sensitive_result["is_sensitive"]:
        return {
            "category": "sensitive_information",
            "confidence": 0.99,
            "reason": (
                f"Sensitive information detected: "
                f"{sensitive_result['sensitivity_type']}."
            ),
        }

    # ---------------------------------------------------------------
    # 2. Calculate scores for normal categories
    # ---------------------------------------------------------------

    scores = {
        "action_required": count_keyword_matches(
            message,
            ACTION_KEYWORDS
        ),

        "meeting_or_event": count_keyword_matches(
            message,
            MEETING_KEYWORDS
        ),

        "promotional": count_keyword_matches(
            message,
            PROMOTIONAL_KEYWORDS
        ),

        "personal_information": count_keyword_matches(
            message,
            PERSONAL_KEYWORDS
        ),

        "general_information": count_keyword_matches(
            message,
            GENERAL_KEYWORDS
        ),
    }

    # ---------------------------------------------------------------
    # 3. Sender-based promotional signal
    # ---------------------------------------------------------------

    if sender.strip().lower() == "promotions":
        scores["promotional"] += 3

    # ---------------------------------------------------------------
    # 4. Choose the category with the highest score
    # ---------------------------------------------------------------

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    # ---------------------------------------------------------------
    # 5. No strong signal → General Information
    # ---------------------------------------------------------------

    if best_score == 0:
        return {
            "category": "general_information",
            "confidence": 0.60,
            "reason": (
                "No strong action, meeting, personal, promotional, "
                "or sensitive pattern was detected."
            ),
        }

    # ---------------------------------------------------------------
    # 6. Calculate explainable confidence
    # ---------------------------------------------------------------

    total_score = sum(scores.values())

    confidence = best_score / total_score

    # Keep confidence within a sensible range.
    confidence = max(0.60, min(0.98, confidence))

    # ---------------------------------------------------------------
    # 7. Build explanation
    # ---------------------------------------------------------------

    category_names = {
        "action_required": "action/request language",
        "meeting_or_event": "meeting or event language",
        "promotional": "promotional language",
        "personal_information": "personal-information language",
        "general_information": "general-information language",
    }

    reason = (
        f"Classified as {category_names[best_category]} "
        f"based on {best_score} matching pattern(s)."
    )

    return {
        "category": best_category,
        "confidence": round(confidence, 2),
        "reason": reason,
    }