import pandas as pd

from app.classifier import classify_message
from app.sensitive_detector import detect_sensitive_information


messages = pd.read_csv("data/messages.csv")
mandatory = pd.read_csv("data/mandatory_demo_ids.csv")

# Create lookup by message ID
message_lookup = messages.set_index("message_id")


print("MANDATORY MESSAGE RESULTS")
print("=" * 80)

for message_id in mandatory["message_id"]:

    row = message_lookup.loc[message_id]

    classification = classify_message(
        message=row["message"],
        sender=row["sender"]
    )

    sensitive = detect_sensitive_information(row["message"])

    print(f"\nMessage ID: {message_id}")
    print(f"Category: {classification['category']}")
    print(f"Confidence: {classification['confidence']}")
    print(f"Reason: {classification['reason']}")

    if sensitive["is_sensitive"]:
        print("Sensitive: YES")
        print(f"Type: {sensitive['sensitivity_type']}")
        print(f"Risk: {sensitive['risk']}")
        print(f"Recommended Action: {sensitive['recommended_action']}")
    else:
        print("Sensitive: NO")