import json
from pathlib import Path

import pandas as pd

from app.classifier import classify_message
from app.extractor import extract_item
from app.sensitive_detector import detect_sensitive_information


# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

MESSAGES_FILE = DATA_DIR / "messages.csv"
MANDATORY_IDS_FILE = DATA_DIR / "mandatory_demo_ids.csv"


# -------------------------------------------------------------------
# Helper function
# -------------------------------------------------------------------

def save_json(data, filepath):
    """Save structured data as formatted JSON."""

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


# -------------------------------------------------------------------
# Main processing pipeline
# -------------------------------------------------------------------

def process_dataset():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ---------------------------------------------------------------
    # Read dataset
    # ---------------------------------------------------------------

    df = pd.read_csv(MESSAGES_FILE)

    # Explicitly sort chronologically.
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df = df.sort_values(
        by="timestamp",
        kind="stable"
    ).reset_index(drop=True)

    # ---------------------------------------------------------------
    # Read mandatory message IDs
    # ---------------------------------------------------------------

    mandatory_df = pd.read_csv(
        MANDATORY_IDS_FILE
    )

    mandatory_ids = set(
        mandatory_df["message_id"].astype(str)
    )

    # ---------------------------------------------------------------
    # Output containers
    # ---------------------------------------------------------------

    classification_results = []
    task_event_results = []
    sensitive_results = []
    mandatory_results = []

    task_counter = 0
    event_counter = 0

    # ---------------------------------------------------------------
    # Process messages chronologically
    # ---------------------------------------------------------------

    for _, row in df.iterrows():

        message_id = str(row["message_id"])
        timestamp = str(row["timestamp"])
        sender = str(row["sender"])
        message = str(row["message"])

        # -----------------------------------------------------------
        # Sensitive detection
        # -----------------------------------------------------------

        sensitive = detect_sensitive_information(
            message
        )

        # -----------------------------------------------------------
        # Classification
        # -----------------------------------------------------------

        classification = classify_message(
            message=message,
            sender=sender
        )

        classification_record = {
            "message_id": message_id,
            "category": classification["category"],
            "confidence": classification["confidence"],
            "reason": classification["reason"],
        }

        classification_results.append(
            classification_record
        )

        # -----------------------------------------------------------
        # Sensitive output
        # -----------------------------------------------------------

        if sensitive["is_sensitive"]:

            sensitive_record = {
                "message_id": message_id,
                "sensitivity_type": sensitive[
                    "sensitivity_type"
                ],
                "risk": sensitive["risk"],
                "masked_text": sensitive["masked_text"],
                "recommended_action": sensitive[
                    "recommended_action"
                ],
            }

            sensitive_results.append(
                sensitive_record
            )

        # -----------------------------------------------------------
        # Task / Event extraction
        # -----------------------------------------------------------

        item = extract_item(
            message_id=message_id,
            timestamp=timestamp,
            sender=sender,
            message=message
        )

        if item is not None:

            if item["type"] == "task":

                task_counter += 1

                item["item_id"] = (
                    f"TASK_{task_counter:03d}"
                )

            else:

                event_counter += 1

                item["item_id"] = (
                    f"EVENT_{event_counter:03d}"
                )

            # -------------------------------------------------------
            # IMPORTANT:
            # If the source message is sensitive, never expose the
            # original message as the task/event description.
            # -------------------------------------------------------

            if sensitive["is_sensitive"]:
                item["description"] = (
                    sensitive["masked_text"]
                )

            task_event_results.append(item)

        # -----------------------------------------------------------
        # Mandatory demonstration result
        # -----------------------------------------------------------

        if message_id in mandatory_ids:

            mandatory_record = {
                "message_id": message_id,
                "category": classification["category"],
                "confidence": classification["confidence"],
                "reason": classification["reason"],
                "sensitive": sensitive["is_sensitive"],
            }

            if sensitive["is_sensitive"]:

                mandatory_record[
                    "sensitivity_type"
                ] = sensitive["sensitivity_type"]

                mandatory_record[
                    "risk"
                ] = sensitive["risk"]

                mandatory_record[
                    "masked_text"
                ] = sensitive["masked_text"]

                mandatory_record[
                    "recommended_action"
                ] = sensitive["recommended_action"]

            else:

                mandatory_record[
                    "sensitivity_type"
                ] = None

                mandatory_record[
                    "risk"
                ] = None

                mandatory_record[
                    "masked_text"
                ] = None

                mandatory_record[
                    "recommended_action"
                ] = None

            mandatory_results.append(
                mandatory_record
            )

    # ---------------------------------------------------------------
    # Save outputs
    # ---------------------------------------------------------------

    save_json(
        classification_results,
        OUTPUT_DIR / "classification_results.json"
    )

    save_json(
        task_event_results,
        OUTPUT_DIR / "task_event_results.json"
    )

    save_json(
        sensitive_results,
        OUTPUT_DIR / "sensitive_results.json"
    )

    save_json(
        mandatory_results,
        OUTPUT_DIR / "mandatory_results.json"
    )

    # ---------------------------------------------------------------
    # Safe console summary
    # ---------------------------------------------------------------

    category_counts = (
        pd.Series(
            [
                item["category"]
                for item in classification_results
            ]
        )
        .value_counts()
        .to_dict()
    )

    print("=" * 60)
    print("MESSAGE INTELLIGENCE PIPELINE")
    print("=" * 60)

    print(f"Messages processed: {len(df)}")

    print(
        f"Tasks extracted: "
        f"{sum(1 for x in task_event_results if x['type'] == 'task')}"
    )

    print(
        f"Meetings/events extracted: "
        f"{sum(1 for x in task_event_results if x['type'] == 'meeting_or_event')}"
    )

    print(
        f"Sensitive messages detected: "
        f"{len(sensitive_results)}"
    )

    print(
        f"Mandatory messages processed: "
        f"{len(mandatory_results)}"
    )

    print("\nCategory distribution:")

    for category, count in sorted(
        category_counts.items()
    ):
        print(f"- {category}: {count}")

    print("\nOutput files created:")

    print(
        "- outputs/classification_results.json"
    )

    print(
        "- outputs/task_event_results.json"
    )

    print(
        "- outputs/sensitive_results.json"
    )

    print(
        "- outputs/mandatory_results.json"
    )

    print("=" * 60)


if __name__ == "__main__":
    process_dataset()