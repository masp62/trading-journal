# Trading Logbook and Journal

A Python application for tracking trades and maintaining a trading journal with both CLI and REST API interfaces.

## Features

- **Trade Tracking**: Record and manage all your trades
- **Journal Entries**: Document your trading thoughts, strategies, and lessons learned
- **Performance Analytics**: Analyze your trading performance with key metrics
- **SQLite Database**: Local data storage for all your trading data
- **CLI Interface**: Easy-to-use command-line interface
- **REST API**: FastAPI-based REST API for integration with other applications
- **Interactive API Documentation**: Swagger UI and ReDoc available

## Project Structure

```
trading-journal/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── app.py               # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── models.py        # Pydantic models
│   │   ├── trades.py        # Trade endpoints
│   │   ├── journal.py       # Journal endpoints
│   │   └── analytics.py     # Analytics endpoints
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_manager.py    # Database operations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trade.py         # Trade model
│   │   └── journal.py       # Journal entry model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── trade_service.py # Trade management
│   │   └── journal_service.py # Journal management
│   └── utils/
│       ├── __init__.py
│       ├── analytics.py     # Performance analytics
│       └── config.py        # Configuration management
├── data/                    # Database storage (created at runtime)
├── start_api.bat            # Windows API startup script
├── start_api.sh             # Unix API startup script
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

### Automatische Installation (empfohlen)

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

Das Skript erstellt automatisch eine virtuelle Umgebung und installiert alle Abhängigkeiten.

### Manuelle Installation

1. Erstellen Sie eine virtuelle Umgebung:
```bash
python -m venv venv
```

2. Aktivieren Sie die virtuelle Umgebung:

**Windows:**
```bash
venv\Scripts\activate
# Oder nutzen Sie:
activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
# Oder nutzen Sie:
source activate.sh
```

3. Installieren Sie die Abhängigkeiten:
```bash
pip install -r requirements.txt
```

## Usage

### CLI Usage

Run the CLI application:
```bash
python src/main.py
```

Available commands:
- `python src/main.py add-trade` - Add a new trade
- `python src/main.py list-trades` - List recent trades (with filters)
- `python src/main.py add-journal` - Add a journal entry
- `python src/main.py list-journal` - List journal entries
- `python src/main.py analytics` - Show performance analytics
- `python src/main.py risk-calculator` - Calculate risk amounts for your portfolio

#### List Trades with Filters

Filter your trading history with multiple options:

```bash
# Show last 20 trades
python src/main.py list-trades --limit 20

# Filter by symbol
python src/main.py list-trades --symbol "Tech"

# Filter by action (BUY or SELL)
python src/main.py list-trades --action BUY

# Filter by date range
python src/main.py list-trades --from-date 2026-01-01 --to-date 2026-01-31

# Filter by profit/loss
python src/main.py list-trades --min-profit 10
python src/main.py list-trades --max-profit -5

# Combine multiple filters
python src/main.py list-trades --symbol "Germany40" --action BUY --min-profit 5 --from-date 2026-01-20
```

Available filter options:
- `--limit INTEGER` - Number of trades to show (default: 10)
- `--symbol TEXT` - Filter by symbol/instrument (partial match)
- `--action [BUY|SELL]` - Filter by trade direction
- `--from-date YYYY-MM-DD` - Show trades from this date onwards
- `--to-date YYYY-MM-DD` - Show trades until this date
- `--min-profit FLOAT` - Show only trades with P/L >= value
- `--max-profit FLOAT` - Show only trades with P/L <= value

### REST API Usage

Start the FastAPI server:

**Windows:**
```bash
start_api.bat
```

**Linux/Mac:**
```bash
./start_api.sh
```

**Or directly:**
```bash
python run_api.py
```

Access the API:
- **API Base URL**: http://localhost:8000
- **Swagger UI (Interactive Docs)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### Trades
- `POST /trades/` - Create a new trade
- `GET /trades/` - Get recent trades with filters
  - Query params: `limit`, `include_overnight`, `format` (json/csv)
  - Filter params: `symbol`, `action`, `from_date`, `to_date`, `min_profit`, `max_profit`
- `GET /trades/{trade_id}` - Get a specific trade
- `DELETE /trades/{trade_id}` - Delete a trade

**Example API calls:**
```bash
# Get last 10 trades
curl http://localhost:8000/trades/

# Filter trades by symbol
curl "http://localhost:8000/trades/?symbol=Tech&limit=20"

# Filter by date range and action
curl "http://localhost:8000/trades/?from_date=2026-01-01&to_date=2026-01-31&action=BUY"

# Get only winning trades
curl "http://localhost:8000/trades/?min_profit=0"

# Export to CSV
curl "http://localhost:8000/trades/?format=csv&limit=100" > trades.csv
```

#### Journal
- `POST /journal/` - Create a journal entry
- `GET /journal/` - Get recent journal entries (query param: limit)
- `GET /journal/{entry_id}` - Get a specific entry
- `DELETE /journal/{entry_id}` - Delete an entry

#### Analytics
- `GET /analytics/` - Get trading performance analytics

#### Examples

**Get Analytics:**
```bash
curl http://localhost:8000/analytics/
```

Example response:
```json
{
  "total_trades": 150,
  "winning_trades": 85,
  "losing_trades": 65,
  "win_rate": 0.567,
  "total_profit": 4250.500,
  "total_loss": -2890.750,
  "net_profit": 1359.750,
  "average_win": 50.006,
  "average_loss": -44.473,
  "profit_factor": 1.471,
  "largest_win": 285.300,
  "largest_loss": -198.450,
  "total_overnight_fees": -156.230
}
```

**Get Trades (CSV format):**
```bash
curl "http://localhost:8000/trades/?format=csv&limit=100" -o trades.csv
```

**Create a Trade:**
```bash
curl -X POST "http://localhost:8000/trades/" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "USA Tech 100",
    "action": "BUY",
    "quantity": 1.5,
    "price": 16250.50,
    "close_price": 16380.25,
    "timestamp": "2026-01-25T14:30:00",
    "result_after_fx_fee": 194.62
  }'
```

### Risk Calculator

The risk calculator helps you determine appropriate position sizes based on your portfolio value and risk tolerance.

**Basic Usage:**
```bash
python src/main.py risk-calculator
```

This calculates risk amounts using your current portfolio value from the database.

**Custom Portfolio Value:**
```bash
python src/main.py risk-calculator --portfolio 10000
```

**Example Output:**
```
Portfolio-Wert aus Datenbank berechnet:
  Realisierte Trades: €8,450.75
  Overnight-Zinsen:   €-156.23
  Portfolio-Wert:     €8,294.52

============================================================
RISIKO-RECHNER - Portfolio: €8,294.52
============================================================
+----------+---------------+----------------------------+
| Risiko % | Betrag (€)    | Verbleibendes Kapital (€)  |
+==========+===============+============================+
| 1%       | €82.95        | €8,211.57                  |
+----------+---------------+----------------------------+
| 2%       | €165.89       | €8,128.63                  |
+----------+---------------+----------------------------+
| 3%       | €248.84       | €8,045.68                  |
+----------+---------------+----------------------------+
| 4%       | €331.78       | €7,962.74                  |
+----------+---------------+----------------------------+
| 5%       | €414.73       | €7,879.79                  |
+----------+---------------+----------------------------+
| 10%      | €829.45       | €7,465.07                  |
+----------+---------------+----------------------------+

============================================================
EMPFEHLUNG:
  • Anfänger: 1-2% Risiko pro Trade
  • Fortgeschritten: 2-3% Risiko pro Trade
  • Erfahren: 3-5% Risiko pro Trade
  • Warnung: >5% Risiko kann zu schnellem Kapitalverlust führen
============================================================
```

The risk calculator shows:
- **Risiko %**: The percentage of your portfolio you're willing to risk
- **Betrag (€)**: The actual amount in euros you can risk on a single trade
- **Verbleibendes Kapital**: Your remaining capital after the potential loss

Use these values to calculate position sizes based on your stop-loss distance.

### Position Size Calculator

The position size calculator determines the optimal position size for CFD trading with leverage, taking into account your risk parameters.

**Basic Usage (Interactive):**
```bash
python src/main.py position-size
```

You'll be prompted to enter:
- Risk percentage (e.g., 2 for 2%)
- Entry price
- Stop-loss price

**Non-Interactive Usage:**
```bash
python src/main.py position-size --portfolio 8000 --risk-percent 2 --entry-price 18500 --stop-loss 18300 --leverage 20
```

**Example Output:**
```
Portfolio-Wert aus Datenbank: €8,294.52

======================================================================
POSITIONSGRÖSSENRECHNER (CFD mit Hebel)
======================================================================

📊 EINGABEPARAMETER:
  Portfolio-Wert:     €8,294.52
  Risiko:             2% (€165.89)
  Einstiegspreis:     €18,500.00
  Stop-Loss:          €18,300.00
  Stop-Loss-Distanz:  €200.00 (1.08%)
  Hebel:              20x

🎯 BERECHNETE POSITION:
  Positionsgröße:     0.83 Kontrakte/Einheiten
  Positionswert:      €15,355.00
  Benötigte Margin:   €767.75 (9.3% des Portfolios)
  Verbleibende Margin: €7,526.77

📉 RISIKO-SZENARIEN:
  Verlust bei Stop-Loss: €165.89 (2% des Portfolios)

📈 GEWINN/VERLUST-SZENARIEN:
+---------------------+--------------------+--------------+-----------+------------------+
| Szenario            | Kursänderung (€)   | Neuer Kurs   | G/V (€)   | G/V (% Portfolio)|
+=====================+====================+==============+===========+==================+
| 2% Kursverlust      | -370.00            | €18,130.00   | €-306.89  | -3.70%          |
+---------------------+--------------------+--------------+-----------+------------------+
| 1% Kursverlust      | -185.00            | €18,315.00   | €-153.45  | -1.85%          |
+---------------------+--------------------+--------------+-----------+------------------+
| 0.5% Kursverlust    | -92.50             | €18,407.50   | €-76.72   | -0.92%          |
+---------------------+--------------------+--------------+-----------+------------------+
| 0.25% Kursverlust   | -46.25             | €18,453.75   | €-38.36   | -0.46%          |
+---------------------+--------------------+--------------+-----------+------------------+
| Breakeven (0%)      | +0.00              | €18,500.00   | €0.00     | +0.00%          |
+---------------------+--------------------+--------------+-----------+------------------+
| 0.25% Kursgewinn    | +46.25             | €18,546.25   | €38.36    | +0.46%          |
+---------------------+--------------------+--------------+-----------+------------------+
| 0.5% Kursgewinn     | +92.50             | €18,592.50   | €76.72    | +0.92%          |
+---------------------+--------------------+--------------+-----------+------------------+
| 1% Kursgewinn       | +185.00            | €18,685.00   | €153.45   | +1.85%          |
+---------------------+--------------------+--------------+-----------+------------------+
| 2% Kursgewinn       | +370.00            | €18,870.00   | €306.89   | +3.70%          |
+---------------------+--------------------+--------------+-----------+------------------+

======================================================================
⚠ WICHTIGE HINWEISE:
  • Stellen Sie sicher, dass genug freie Margin vorhanden ist
  • Berücksichtigen Sie Spreads und Gebühren
  • Hebel vergrößert sowohl Gewinne als auch Verluste
  • Stop-Loss diszipliniert einhalten!
======================================================================
```

The position size calculator shows:
- **Positionsgröße**: How many contracts/units to trade
- **Positionswert**: Total value of the position (before leverage)
- **Benötigte Margin**: Amount of capital required to open the position
- **Gewinn/Verlust-Szenarien**: Potential profits/losses at different price levels

This tool helps you maintain proper risk management by ensuring your position size matches your risk tolerance.

### Database UI

View the DuckDB database using the UI:
```bash
duckdb -ui data/trading_journal.db
```

## Requirements

- Python 3.8 or higher
- SQLite3 (included with Python)

## License

MIT License
