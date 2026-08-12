Yes. Below is the **complete README in one single copy-paste block**.

Open:

```text
messageintelligence\README.md
```

Press **Ctrl+A**, delete everything, then copy-paste the entire block below and press **Ctrl+S**.

````markdown
# Message Intelligence

A local message-processing application that converts unstructured messages into structured, reviewable information.

The system performs:

- Message classification
- Confidence scoring
- Task and event extraction
- Sensitive-information detection
- Sensitive-value masking
- Priority detection
- Mandatory-message processing
- Structured JSON output generation
- Web-based result visualization

The application was developed for the Message Intelligence assignment using the supplied fictional message dataset.

---

## 1. Assignment Objective

The objective is to process a chronological collection of messages and identify:

1. The category of each message.
2. Tasks, meetings, and events contained in messages.
3. Sensitive information that must be detected and masked.
4. Important decisions with reasons and confidence scores.
5. The required mandatory demonstration messages.

The supplied candidate dataset is processed locally.

The original candidate dataset is **not included in the public GitHub repository**.

---

## 2. System Overview

The application follows this processing flow:

```text
                    Candidate Messages
                           |
                           v
                  Chronological Ordering
                           |
                           v
             Sensitive Information Detection
                           |
                           v
                  Message Classification
                           |
                           v
               Task / Event Extraction
                           |
                           v
                  Structured JSON Output
                           |
                           v
                     Web Dashboard
````

Each message is processed independently while preserving the chronological order of the input dataset.

---

## 3. Message Classification

Every message is classified into one of six categories:

* `action_required`
* `meeting_or_event`
* `personal_information`
* `general_information`
* `promotional`
* `sensitive_information`

For every message, the system stores:

* Message ID
* Predicted category
* Confidence score
* Short classification reason

Example:

```json
{
  "message_id": "MSG_001",
  "category": "action_required",
  "confidence": 0.91,
  "reason": "The message contains an explicit request for an action."
}
```

### Classification Approach

The current classifier uses deterministic rule-based pattern matching.

It checks message content for category-specific language patterns.

Examples include:

* Action/request phrases
* Meeting and event terminology
* Personal-information language
* Promotional language
* General informational language
* Sensitive-information patterns

Sensitive information is checked before the final classification so that messages containing detected sensitive information can be classified as:

```text
sensitive_information
```

The classifier also produces a confidence score based on the strength of the detected patterns.

---

## 4. Task and Event Extraction

Messages that contain an actionable task, meeting, or event are passed to the extraction component.

The extractor attempts to identify:

* Item ID
* Type
* Title
* Description
* Date
* Deadline
* Time
* Person
* Priority
* Source message ID

### Task Example

```json
{
  "item_id": "TASK_014",
  "type": "task",
  "title": "Submit internship report",
  "description": "Submit the internship report.",
  "date": null,
  "deadline": "2026-08-15",
  "time": null,
  "person": null,
  "priority": "high",
  "source_message_id": "MSG_118"
}
```

### Event Example

```json
{
  "item_id": "EVENT_003",
  "type": "meeting_or_event",
  "title": "Project Review",
  "description": "The project review is scheduled.",
  "date": "2026-09-12",
  "deadline": null,
  "time": "15:00",
  "person": null,
  "priority": "medium",
  "source_message_id": "MSG_120"
}
```

---

## 5. Handling Missing Information

The system does not invent missing information.

If the message does not explicitly contain a date, time, person, or deadline, the corresponding field is stored as:

```text
null
```

For example:

```json
{
  "item_id": "EVENT_005",
  "type": "meeting_or_event",
  "title": "Meeting",
  "description": "Let us meet sometime next week.",
  "date": null,
  "deadline": null,
  "time": null,
  "person": null,
  "priority": "medium",
  "source_message_id": "MSG_125"
}
```

This allows ambiguous messages to remain unresolved instead of introducing fabricated information.

---

## 6. Priority Detection

The extractor determines priority using explicit language.

High-priority signals include terms such as:

```text
urgent
immediately
as soon as possible
critical
important
deadline
due
```

An explicit deadline such as:

```text
by 2026-09-10
```

is also treated as a high-priority signal.

Low-priority signals include phrases such as:

```text
optional
if possible
whenever
when you are free
```

If no clear priority signal is present, the system uses:

```text
medium
```

---

## 7. Sensitive Information Detection

The system detects sensitive-looking information before displaying or storing results.

The detector currently handles categories including:

* One-time passwords
* Passwords
* Phone numbers
* Bank account numbers
* Card numbers
* Identification numbers
* Home addresses
* Account recovery codes
* Access tokens

Sensitive values are replaced with masking characters.

Example:

```text
Original:
Your OTP is 123456

Displayed:
Your OTP is ******
```

The raw sensitive value is not displayed by the dashboard.

---

## 8. Sensitive Information Risk Handling

Detected sensitive information receives a risk level and recommended action.

Possible recommended actions include:

```text
safe_to_process_locally
ask_for_confirmation
do_not_store
do_not_send_to_external_service
```

Example:

```json
{
  "message_id": "MSG_204",
  "sensitivity_type": "one_time_password",
  "risk": "high",
  "masked_text": "Your OTP is ******",
  "recommended_action": "do_not_store"
}
```

The application does not send raw candidate messages to an external AI service.

---

## 9. Mandatory Demonstration Messages

The assignment provides 15 mandatory message IDs.

The system processes these IDs separately and produces a structured result for each one.

The dashboard displays:

* Message ID
* Category
* Confidence
* Classification reason
* Sensitive status
* Risk level when applicable
* Recommended action when applicable

Sensitive values remain masked.

---

## 10. Current Candidate Dataset Results

The supplied dataset contains:

```text
900 messages
```

The current processing run produced:

```text
Messages processed:              900
Tasks extracted:                 150
Meetings/events extracted:       190
Sensitive messages detected:     90
Mandatory messages processed:     15
```

### Classification Distribution

```text
action_required:         200
general_information:     240
meeting_or_event:        170
personal_information:     90
promotional:             110
sensitive_information:    90
```

The six category counts sum to the complete dataset:

```text
200 + 240 + 170 + 90 + 110 + 90 = 900
```

---

## 11. Output Files

The processing pipeline generates four structured JSON files:

```text
outputs/
├── classification_results.json
├── task_event_results.json
├── sensitive_results.json
└── mandatory_results.json
```

These files are generated locally from the supplied candidate dataset.

They are intentionally excluded from the public repository.

---

## 12. Project Structure

```text
messageintelligence/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── classifier.py
│   ├── extractor.py
│   ├── sensitive_detector.py
│   ├── utils.py
│   └── web_app.py
│
├── data/
│   ├── messages.csv
│   └── mandatory_demo_ids.csv
│
├── outputs/
│   ├── classification_results.json
│   ├── task_event_results.json
│   ├── sensitive_results.json
│   └── mandatory_results.json
│
├── static/
│   └── style.css
│
├── templates/
│   └── index.html
│
├── tests/
│   ├── test_classifier_dataset.py
│   ├── test_extractor_dataset.py
│   ├── test_mandatory_ids.py
│   ├── test_pipeline.py
│   └── test_sensitive_dataset.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

> The `data/` and `outputs/` directories shown above are used locally and are not published to the public GitHub repository.

---

## 13. Technology Stack

The application uses:

* Python
* Pandas
* FastAPI
* Uvicorn
* Jinja2
* Regular Expressions
* Pytest
* HTML
* CSS

No external generative-AI API is required for the core processing pipeline.

---

## 14. Installation

Clone the repository:

```bash
git clone https://github.com/Somanadhasai/message-intelligence.git
cd message-intelligence
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```cmd
venv\Scripts\activate
```

Install dependencies:

```cmd
pip install -r requirements.txt
```

---

## 15. Local Dataset Setup

The candidate dataset is intentionally not included in the GitHub repository.

For local assignment execution, place the supplied files in:

```text
data/
├── messages.csv
└── mandatory_demo_ids.csv
```

The application expects `messages.csv` with the following columns:

```text
message_id
timestamp
sender
message
```

The mandatory ID file contains the message IDs required for the demonstration.

---

## 16. Run the Processing Pipeline

Run:

```cmd
python -m app.main
```

The application processes the messages chronologically and generates the structured JSON output files.

Example summary:

```text
MESSAGE INTELLIGENCE PIPELINE

Messages processed: 900
Tasks extracted: 150
Meetings/events extracted: 190
Sensitive messages detected: 90
Mandatory messages processed: 15
```

---

## 17. Run Automated Tests

Run:

```cmd
python -m pytest -q
```

The current automated test suite contains seven tests.

Current result:

```text
7 passed
```

The tests cover:

* Sensitive-information detection
* Sensitive-value masking
* Message classification
* Sensitive classification
* Task extraction
* Event extraction
* Output-file generation
* Output counts

---

## 18. Run the Web Dashboard

Start the FastAPI application:

```cmd
uvicorn app.web_app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The dashboard provides a visual summary of:

* Message counts
* Six classification categories
* Task extraction
* Meeting/event extraction
* Sensitive-information detection
* Mandatory demonstration results
* Low-confidence classifications
* Processing pipeline

The health endpoint is available at:

```text
http://127.0.0.1:8000/health
```

---

## 19. Privacy and Security

The supplied candidate dataset contains fictional messages, but sensitive-looking values must still be handled according to the assignment requirements.

Therefore:

* The supplied CSV files are kept local.
* The supplied dataset is not committed to GitHub.
* Generated candidate outputs are not committed to GitHub.
* Sensitive values are masked before display.
* Raw candidate messages are not sent to external AI services.
* Sensitive-looking values are not intentionally included in screenshots or recordings.
* The public repository contains source code and documentation rather than the candidate dataset.

---

## 20. Assumptions

The following assumptions are used by the current implementation:

1. Classification is based on explicit textual patterns.
2. Dates are extracted when they appear in `YYYY-MM-DD` format.
3. Times are extracted when they appear in `HH:MM` format.
4. Person names are extracted only when they appear in recognizable contextual patterns.
5. Missing information is represented using `null`.
6. Explicit deadline language is treated as a high-priority signal.
7. Low-priority language such as "optional" or "if possible" is treated as a low-priority signal.
8. If no clear priority signal is present, priority defaults to medium.
9. Sensitive-information detection uses local pattern-based rules.
10. The system processes messages in chronological order.
11. The system does not claim perfect semantic understanding of every message.

---

## 21. Limitations

The current implementation is intentionally lightweight and local.

Limitations include:

* Rule-based classification may miss unusual wording.
* Pattern matching may occasionally produce false positives.
* Person extraction is limited to recognizable name patterns.
* Date extraction currently focuses on explicit date formats.
* Natural-language dates such as "next Friday" are not automatically converted into a calendar date.
* Ambiguous tasks or events may be missed.
* Confidence scores are heuristic rather than statistically calibrated probabilities.
* Sensitive-information detection depends on predefined patterns.
* The system does not use a large language model for semantic reasoning.

---

## 22. Possible Improvements

Future improvements could include:

* Local embedding-based semantic classification
* A lightweight locally hosted machine-learning classifier
* Better natural-language date parsing
* Improved named-entity recognition
* More advanced sensitive-information detection
* Confidence calibration using a labeled validation dataset
* Human review workflows for uncertain messages
* Search and filtering across extracted tasks and events
* More detailed dashboard analytics
* Role-based access control for production deployments

---

## 23. AI Tool Usage Declaration

AI development tools were used during development to assist with:

* Project structure planning
* Debugging
* Code suggestions
* Documentation drafting
* Test-case design
* Error diagnosis

The implementation was reviewed and tested locally by the developer.

The core message-processing pipeline does not rely on sending the supplied candidate dataset to ChatGPT, OpenAI, or another external AI service.

The candidate dataset remains local.

---

## 24. Development Verification

The final local implementation was verified with:

```text
Messages processed: 900
Tasks extracted: 150
Meetings/events extracted: 190
Sensitive messages detected: 90
Mandatory messages processed: 15
```

Automated tests:

```text
7 passed
```

---

## 25. Repository

GitHub repository:

[https://github.com/Somanadhasai/message-intelligence](https://github.com/Somanadhasai/message-intelligence)

The public repository intentionally excludes the supplied candidate dataset.

---



