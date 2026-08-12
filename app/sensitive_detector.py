import re


SENSITIVE_PATTERNS = {
    "password": re.compile(
        r"\bpassword\s+(?:is\s+)?([^\s]+)",
        re.IGNORECASE
    ),

    "one_time_password": re.compile(
        r"\b(?:OTP|one[-\s]?time password)\s*(?:is|:)?\s*([A-Za-z0-9-]+)",
        re.IGNORECASE
    ),

    "bank_account": re.compile(
        r"\bbank account number\s+(?:is\s+)?([0-9][0-9-]*)",
        re.IGNORECASE
    ),

    "card_number": re.compile(
        r"\bcard number\s+(?:is\s+)?([0-9][0-9 -]{10,})",
        re.IGNORECASE
    ),

    "account_recovery_code": re.compile(
        r"\baccount recovery code\s+(?:is\s+)?(RC-[A-Za-z0-9-]+)",
        re.IGNORECASE
    ),

    "access_token": re.compile(
        r"\b(?:temporary access token|access token)\s+(?:is\s+)?(tok_[A-Za-z0-9_-]+)",
        re.IGNORECASE
    ),

    "identification_number": re.compile(
        r"\bidentification number\s+(?:is\s+)?([A-Za-z0-9-]+)",
        re.IGNORECASE
    ),

    "phone_number": re.compile(
        r"\b(\d{5}\s?\d{5}(?:-\d+)?)\b",
        re.IGNORECASE
    ),

    "home_address": re.compile(
        r"\bhome address is\s+(.+?)(?=\s*$)",
        re.IGNORECASE
    ),
}


RISK_LEVELS = {
    "password": "high",
    "one_time_password": "high",
    "bank_account": "high",
    "card_number": "high",
    "account_recovery_code": "high",
    "access_token": "high",
    "identification_number": "high",
    "phone_number": "medium",
    "home_address": "medium",
}


RECOMMENDED_ACTIONS = {
    "password": "do_not_store",
    "one_time_password": "do_not_store",
    "bank_account": "do_not_store",
    "card_number": "do_not_store",
    "account_recovery_code": "do_not_store",
    "access_token": "do_not_store",
    "identification_number": "ask_for_confirmation",
    "phone_number": "ask_for_confirmation",
    "home_address": "ask_for_confirmation",
}


def mask_value(value: str) -> str:
    """Replace a sensitive value completely with asterisks."""
    return "*" * max(4, len(value.strip()))


def detect_sensitive_information(message: str) -> dict:
    """
    Detect and mask sensitive information locally.

    Raw sensitive values are never returned in the masked output.
    """

    for sensitivity_type, pattern in SENSITIVE_PATTERNS.items():

        match = pattern.search(message)

        if not match:
            continue

        sensitive_value = match.group(1)

        masked_value = mask_value(sensitive_value)

        masked_message = (
            message[:match.start(1)]
            + masked_value
            + message[match.end(1):]
        )

        return {
            "is_sensitive": True,
            "sensitivity_type": sensitivity_type,
            "risk": RISK_LEVELS[sensitivity_type],
            "masked_text": masked_message,
            "recommended_action": RECOMMENDED_ACTIONS[sensitivity_type],
        }

    return {
        "is_sensitive": False,
        "sensitivity_type": None,
        "risk": None,
        "masked_text": message,
        "recommended_action": "safe_to_process_locally",
    }