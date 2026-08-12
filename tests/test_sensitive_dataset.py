import pandas as pd
from app.sensitive_detector import detect_sensitive_information


df = pd.read_csv("data/messages.csv")

total = 0
types = {}

for _, row in df.iterrows():
    result = detect_sensitive_information(row["message"])

    if result["is_sensitive"]:
        total += 1

        sensitivity_type = result["sensitivity_type"]
        types[sensitivity_type] = types.get(sensitivity_type, 0) + 1


print("Total messages scanned:", len(df))
print("Sensitive messages detected:", total)

print("\nSensitivity types:")
for sensitivity_type, count in sorted(types.items()):
    print(f"- {sensitivity_type}: {count}")