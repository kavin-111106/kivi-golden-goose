# Kivi Golden Goose

A FastAPI backend that provides personal word-memory functionality for Kivi.

The system learns corrections from observed words and intended words, stores them as memories, and uses confirmed memories to transform future text.

## Features

- Store word observations and intended corrections
- Detect repeated observations
- Track evidence count and confidence
- Automatically confirm memories after repeated evidence
- Transform text using confirmed memories
- Preserve punctuation during transformation
- View stored memories
- Update memories
- Delete individual memories
- Reset all memories
- Input validation using Pydantic
- SQLite database using SQLAlchemy
- Automated API tests using pytest

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- RapidFuzz
- Pytest

## Project Structure

```text
kivi-golden-goose/
│
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
│
├── tests/
│   └── test_api.py
│
├── data/
│
├── .gitignore
├── requirements.txt
└── README.md
