# Trading Logbook and Journal - Copilot Instructions

## Project Overview
This is a Python application for tracking trades and maintaining a trading journal with performance analytics. It provides both a CLI interface and a REST API.

## Project Structure
- **src/**: Main source code directory
  - **main.py**: CLI entry point with Click commands
  - **app.py**: FastAPI application entry point
  - **api/**: REST API implementation
    - **models.py**: Pydantic models for API
    - **trades.py**: Trade endpoints
    - **journal.py**: Journal endpoints
    - **analytics.py**: Analytics endpoints
  - **database/**: Database management (DuckDB)
  - **models/**: Data models (Trade, JournalEntry)
  - **services/**: Business logic (TradeService, JournalService, OvernightService)
  - **utils/**: Utilities (Analytics, Config)
- **data/**: DuckDB database storage (created at runtime)
- **requirements.txt**: Python dependencies

## Key Technologies
- Python 3.8+
- DuckDB for data storage
- Click for CLI interface
- FastAPI for REST API
- Pydantic for data validation
- Uvicorn as ASGI server
- Pandas/NumPy for analytics
- Tabulate for formatted output

## Available Commands (CLI)
- `python3 src/main.py init` - Initialize database
- `python3 src/main.py add-trade` - Add a new trade
- `python3 src/main.py list-trades` - List recent trades
- `python3 src/main.py add-journal` - Add journal entry
- `python3 src/main.py list-journal` - List journal entries
- `python3 src/main.py analytics` - Display performance analytics

## API Endpoints
- **GET /** - Root endpoint
- **GET /health** - Health check
- **POST /trades/** - Create a new trade
- **GET /trades/** - Get recent trades
- **GET /trades/{trade_id}** - Get specific trade
- **DELETE /trades/{trade_id}** - Delete a trade
- **POST /journal/** - Create journal entry
- **GET /journal/** - Get recent journal entries
- **GET /journal/{entry_id}** - Get specific entry
- **DELETE /journal/{entry_id}** - Delete an entry
- **GET /analytics/** - Get performance analytics

## Starting the API
- **Windows**: `start_api.bat`
- **Unix/Linux/Mac**: `./start_api.sh`
- **Direct**: `uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload`

## API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Development Guidelines
- All database operations go through DatabaseManager
- Services handle business logic
- Models define data structures (both ORM and Pydantic)
- Use Click decorators for CLI commands
- Use FastAPI routers for API endpoints
- Follow Python PEP 8 style guidelines
- API responses use Pydantic models for validation
