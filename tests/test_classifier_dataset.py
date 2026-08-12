import pandas as pd

from app.classifier import classify_message


df = pd.read_csv("data/messages.csv")

category_counts = {}

confidence_values = []

for _, row in df.iterrows():

    result = classify_message(
        message=row["message"],
        sender=row["sender"]
    )

    category = result["category"]
    confidence = result["confidence"]

    category_counts[category] = (
        category_counts.get(category, 0) + 1
    )

    confidence_values.append(confidence)


print("Total messages processed:", len(df))

print("\nCategory distribution:")

for category, count in sorted(category_counts.items()):
    print(f"- {category}: {count}")

print("\nConfidence:")
print("Minimum:", min(confidence_values))
print("Maximum:", max(confidence_values))
print(
    "Average:",
    round(sum(confidence_values) / len(confidence_values), 3)
)