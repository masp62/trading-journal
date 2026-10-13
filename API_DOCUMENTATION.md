# Trading Journal API Documentation

## Übersicht

Die Trading Journal API bietet eine REST-Schnittstelle zum Verwalten von Trades, Journal-Einträgen und zum Abrufen von Performance-Analytics.

**Base URL**: `http://localhost:8000`

## Authentifizierung

Derzeit ist keine Authentifizierung erforderlich. In Produktionsumgebungen sollte eine Authentifizierung implementiert werden.

## Endpoints

### Root & Health

#### GET /
Root-Endpoint mit API-Informationen.

**Response:**
```json
{
  "message": "Trading Journal API",
  "version": "1.0.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

#### GET /health
Health-Check Endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Trades

#### POST /trades/
Erstellt einen neuen Trade.

**Request Body:**
```json
{
  "symbol": "AAPL",
  "action": "BUY",
  "quantity": 10.0,
  "price": 150.50,
  "notes": "Optional notes",
  "close_price": 155.00,
  "timestamp": "2026-01-20T10:30:00",
  "opening_time": "2026-01-20T09:00:00",
  "result_gross": 45.00,
  "result_net": 42.50,
  "fx_fee": 0.50,
  "result_after_fx_fee": 42.00,
  "instrument_currency": "USD",
  "order_number_name": "ORD123456",
  "order_number_id": "ext_123456"
}
```

**Minimale Request:**
```json
{
  "symbol": "AAPL",
  "action": "BUY",
  "quantity": 10.0,
  "price": 150.50
}
```

**Response:**
```json
{
  "message": "Trade created successfully",
  "id": 42
}
```

#### GET /trades/
Holt die neuesten Trades.

**Query Parameters:**
- `limit` (optional): Anzahl der Trades (1-100, default: 10)
- `include_overnight` (optional): Overnight-Gebühren einbeziehen (default: true)

**Example:** `GET /trades/?limit=20&include_overnight=true`

**Response:**
```json
[
  {
    "id": 1,
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 10.0,
    "price": 150.50,
    "notes": "Test trade",
    "timestamp": "2026-01-20T10:30:00",
    "opening_time": "2026-01-20T09:00:00",
    "close_price": 155.00,
    "result_gross": 45.00,
    "result_net": 42.50,
    "fx_fee": 0.50,
    "result_after_fx_fee": 42.00,
    "overnight_fees_total": -1.25,
    "instrument_currency": "USD",
    "order_number_name": "ORD123456"
  }
]
```

#### GET /trades/{trade_id}
Holt einen spezifischen Trade.

**Path Parameters:**
- `trade_id`: Trade ID

**Response:**
```json
{
  "id": 1,
  "symbol": "AAPL",
  "action": "BUY",
  "quantity": 10.0,
  "price": 150.50,
  "notes": "Test trade",
  "timestamp": "2026-01-20T10:30:00",
  "close_price": 155.00,
  "result_after_fx_fee": 42.00,
  "overnight_fees_total": -1.25
}
```

**Error Response (404):**
```json
{
  "detail": "Trade not found"
}
```

#### DELETE /trades/{trade_id}
Löscht einen Trade.

**Path Parameters:**
- `trade_id`: Trade ID

**Response:**
```json
{
  "message": "Trade deleted successfully",
  "id": 1
}
```

---

### Journal

#### POST /journal/
Erstellt einen Journal-Eintrag.

**Request Body:**
```json
{
  "title": "Reflections on Today's Trading",
  "content": "Today I learned that patience is key...",
  "tags": "lessons,patience,discipline"
}
```

**Response:**
```json
{
  "message": "Journal entry created successfully",
  "id": 10
}
```

#### GET /journal/
Holt die neuesten Journal-Einträge.

**Query Parameters:**
- `limit` (optional): Anzahl der Einträge (1-100, default: 10)

**Example:** `GET /journal/?limit=5`

**Response:**
```json
[
  {
    "id": 1,
    "timestamp": "2026-01-20T15:30:00",
    "title": "Reflections on Today's Trading",
    "content": "Today I learned that patience is key...",
    "tags": "lessons,patience,discipline"
  }
]
```

#### GET /journal/{entry_id}
Holt einen spezifischen Journal-Eintrag.

**Path Parameters:**
- `entry_id`: Entry ID

**Response:**
```json
{
  "id": 1,
  "timestamp": "2026-01-20T15:30:00",
  "title": "Reflections on Today's Trading",
  "content": "Today I learned that patience is key...",
  "tags": "lessons,patience,discipline"
}
```

#### DELETE /journal/{entry_id}
Löscht einen Journal-Eintrag.

**Path Parameters:**
- `entry_id`: Entry ID

**Response:**
```json
{
  "message": "Journal entry deleted successfully",
  "id": 1
}
```

---

### Analytics

#### GET /analytics/
Holt Trading Performance Analytics.

**Response:**
```json
{
  "total_trades": 150,
  "winning_trades": 90,
  "losing_trades": 60,
  "win_rate": 0.6,
  "total_profit": 12500.50,
  "total_loss": -7800.25,
  "net_profit": 4700.25,
  "average_win": 138.89,
  "average_loss": -130.00,
  "profit_factor": 1.60,
  "largest_win": 850.00,
  "largest_loss": -520.00
}
```

---

## Fehlerbehandlung

Alle Endpoints können folgende Fehler zurückgeben:

### 400 Bad Request
Ungültige Request-Daten.

```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ]
}
```

### 404 Not Found
Ressource nicht gefunden.

```json
{
  "detail": "Trade not found"
}
```

### 500 Internal Server Error
Server-Fehler.

```json
{
  "detail": "Database connection error"
}
```

---

## Verwendungsbeispiele

### Python mit requests

```python
import requests

# Trade erstellen
trade_data = {
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 10,
    "price": 150.50,
    "notes": "Entry at support level"
}
response = requests.post("http://localhost:8000/trades/", json=trade_data)
print(response.json())

# Trades abrufen
response = requests.get("http://localhost:8000/trades/?limit=10")
trades = response.json()
print(f"Found {len(trades)} trades")

# Analytics abrufen
response = requests.get("http://localhost:8000/analytics/")
analytics = response.json()
print(f"Win Rate: {analytics['win_rate']*100}%")
```

### cURL

```bash
# Trade erstellen
curl -X POST "http://localhost:8000/trades/" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "action": "BUY",
    "quantity": 10,
    "price": 150.50,
    "notes": "Test trade"
  }'

# Trades abrufen
curl "http://localhost:8000/trades/?limit=5"

# Analytics abrufen
curl "http://localhost:8000/analytics/"

# Trade löschen
curl -X DELETE "http://localhost:8000/trades/1"
```

---

## Interaktive Dokumentation

Die API bietet zwei interaktive Dokumentations-Interfaces:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Diese ermöglichen das Testen aller Endpoints direkt im Browser.

---

## Entwicklung & Testing

### Server starten
```bash
# Windows
start_api.bat

# Linux/Mac
./start_api.sh

# Oder direkt
python run_api.py
```

### API Tests ausführen
```bash
python test_api.py
```

---

## CORS

Die API ist aktuell mit `allow_origins=["*"]` konfiguriert. In Produktionsumgebungen sollten nur spezifische Origins erlaubt werden.
