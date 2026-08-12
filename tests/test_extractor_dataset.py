import pandas as pd

from app.extractor import extract_item


df = pd.read_csv("data/messages.csv")

task_count = 0
event_count = 0

priority_counts = {
    "high": 0,
    "medium": 0,
    "low": 0
}

events_with_date = 0
events_with_time = 0
events_without_date = 0
events_without_time = 0

tasks_with_deadline = 0
tasks_without_deadline = 0


for _, row in df.iterrows():

    result = extract_item(
        message_id=row["message_id"],
        timestamp=row["timestamp"],
        sender=row["sender"],
        message=row["message"]
    )

    if result is None:
        continue

    priority = result["priority"]

    if priority in priority_counts:
        priority_counts[priority] += 1

    if result["type"] == "task":

        task_count += 1

        if result["deadline"] is not None:
            tasks_with_deadline += 1
        else:
            tasks_without_deadline += 1

    elif result["type"] == "meeting_or_event":

        event_count += 1

        if result["date"] is not None:
            events_with_date += 1
        else:
            events_without_date += 1

        if result["time"] is not None:
            events_with_time += 1
        else:
            events_without_time += 1


print("Total messages processed:", len(df))

print("\nExtraction results:")
print("Tasks extracted:", task_count)
print("Meetings/events extracted:", event_count)
print("Total extracted:", task_count + event_count)

print("\nTask deadlines:")
print("With deadline:", tasks_with_deadline)
print("Without deadline:", tasks_without_deadline)

print("\nEvent dates:")
print("With date:", events_with_date)
print("Without date:", events_without_date)

print("\nEvent times:")
print("With time:", events_with_time)
print("Without time:", events_without_time)

print("\nPriority distribution:")
for priority, count in priority_counts.items():
    print(f"- {priority}: {count}")