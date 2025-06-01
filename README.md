# Pokémon MCP Server

A Modular Control Platform server that interfaces with the Open Pokémon API, providing structured access to Pokémon data for AI agents.

## Features

- RESTful API built with FastAPI
- Modular components for Pokémon data retrieval, comparison, and strategy
- Team composition generator
- Simple web interface for testing and demonstration
- SQLite database for caching and performance

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

4. Open the frontend:
- Open `frontend/index.html` in your web browser

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # Database models
│   └── modules/             # Modular components
│       ├── info.py          # Information retrieval module
│       ├── comparison.py    # Comparison module
│       ├── strategy.py      # Strategy module
│       └── team.py          # Team composition module
├── frontend/
│   ├── index.html          # Main web interface
│   ├── styles.css          # Styling
│   └── script.js           # Frontend logic
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## API Documentation

Once the server is running, visit:
- http://localhost:8000/docs for Swagger UI documentation
- http://localhost:8000/redoc for ReDoc documentation

## Testing

Run tests with:
```bash
pytest
``` 