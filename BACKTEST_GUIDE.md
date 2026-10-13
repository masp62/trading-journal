# Backtesting Dokumentations-Guide

## Übersicht
Dieser Guide erklärt, wie Sie Ihre manuellen Backtests dokumentieren, um später automatisierte Analysen durchführen zu können.

## Verfügbare Templates

### 1. Basic Template (`backtest_template_basic.csv`)
**20 essenzielle Spalten** - Empfohlen für den Start

Öffnen Sie mit Excel, Google Sheets oder LibreOffice Calc.

#### Pflichtfelder (müssen ausgefüllt werden):
- **id**: Fortlaufende Nummer (1, 2, 3, ...)
- **backtest_session_id**: Name Ihrer Backtest-Session (z.B. "MACD_Q1_2026")
- **timestamp**: Schlusszeitpunkt des Trades (Format: YYYY-MM-DD HH:MM:SS)
- **symbol**: Handelssymbol (z.B. AAPL, EUR/USD, BTC)
- **direction**: LONG oder SHORT
- **entry_price**: Einstiegspreis
- **exit_price**: Ausstiegspreis
- **quantity**: Anzahl/Positionsgröße
- **net_pnl**: Nettogewinn/-verlust (nach Kosten)

#### Wichtige Felder:
- **pnl_percent**: Gewinn/Verlust in Prozent
- **stop_loss**: Ihr Stop-Loss Niveau
- **take_profit**: Ihr Take-Profit Niveau
- **actual_exit_reason**: Warum wurde ausgestiegen?
  - TAKE_PROFIT
  - STOP_LOSS
  - TIME_EXIT (z.B. Handelsschluss)
  - MANUAL (manuelle Entscheidung)
  - TRAILING_STOP

#### Analyse-Felder:
- **r_multiple**: R-Vielfaches (Gewinn ÷ Risiko)
  - Berechnung: (Exit - Entry) ÷ (Entry - Stop Loss)
  - Beispiel: Entry 100, Exit 103, SL 98 → R = (103-100)/(100-98) = 1.5R
- **entry_setup**: Was war das Signal? (z.B. "MACD Cross über Null + RSI > 50")
- **strategy_name**: Name Ihrer Strategie
- **timeframe**: Zeitrahmen (1min, 5min, 15min, 1h, 4h, Daily, Weekly)
- **trade_quality**: Subjektive Bewertung 1-10 (wie gut war das Setup?)

#### Lern-Felder:
- **mistakes_made**: Welche Fehler wurden gemacht?
- **notes**: Freitext-Notizen

---

### 2. Full Template (`backtest_template_full.csv`)
**Alle 36 Spalten** - Für detaillierte Analysen

Zusätzlich zum Basic Template enthält diese Version:

#### Zeiten:
- **opening_time**: Eröffnungszeitpunkt
- **hold_time_minutes**: Haltedauer in Minuten

#### Kosten & Finanzen:
- **gross_pnl**: Bruttogewinn (vor Kosten)
- **commission**: Kommissionskosten
- **account_balance_before**: Kontostand vor Trade
- **account_balance_after**: Kontostand nach Trade

#### Risk Management:
- **risk_amount**: Risikobetrag in Währung
- **risk_percent**: Risiko in % des Kapitals (z.B. 1%, 2%)
- **position_size_percent**: Positionsgröße in % des Kapitals

#### Markt-Analyse:
- **market_condition**: TRENDING, RANGING, VOLATILE, BREAKOUT
- **trend_alignment**: TRUE/FALSE - Handel mit dem Trend?
- **signal_strength**: Signalstärke 1-10

#### Psychologie & Lernen:
- **psychological_state**: CONFIDENT, FEARFUL, GREEDY, NEUTRAL, UNCERTAIN
- **lessons_learned**: Was haben Sie gelernt?
- **chart_screenshot**: Pfad zu Screenshot (z.B. "screenshots/trade_001.png")
- **tags**: Kategorien (z.B. "momentum,breakout,news_trade")

---

## Workflow-Empfehlung

### Schritt 1: Setup vorbereiten
1. Kopieren Sie eines der Templates
2. Benennen Sie es nach Ihrer Session (z.B. `backtest_macd_strategy_2026.csv`)
3. Löschen Sie die Beispiel-Zeile

### Schritt 2: Trading-Session dokumentieren
Für jeden simulierten Trade:
1. Neue Zeile hinzufügen
2. Pflichtfelder ausfüllen
3. Entry/Exit mit Stop-Loss/Take-Profit festhalten
4. **Sofort dokumentieren** - nicht später versuchen sich zu erinnern!

### Schritt 3: Nach dem Trade
1. Actual Exit Reason eintragen
2. P&L berechnen und eintragen
3. R-Multiple berechnen
4. Trade Quality bewerten (war das Setup gut?)
5. Fehler & Lessons Learned notieren

### Schritt 4: Analyse (später automatisiert)
Die CSV-Datei kann später:
- In Excel analysiert werden (Pivot-Tables)
- In Python eingelesen werden (pandas)
- In Ihre DuckDB importiert werden
- Mit bestehenden Analytics kombiniert werden

---

## Berechnungs-Formeln

### Net P&L
```
net_pnl = (exit_price - entry_price) * quantity - commission
```
Für SHORT Positionen:
```
net_pnl = (entry_price - exit_price) * quantity - commission
```

### P&L Prozent
```
pnl_percent = (net_pnl / (entry_price * quantity)) * 100
```

### R-Multiple
```
risiko = abs(entry_price - stop_loss)
gewinn_verlust = abs(exit_price - entry_price)
r_multiple = gewinn_verlust / risiko
```

### Position Size Percent
```
position_size_percent = (entry_price * quantity / account_balance_before) * 100
```

---

## Tipps für erfolgreiches Backtesting

### ✅ DO's:
- **Konsistent dokumentieren** - jeder Trade, kein Cherry-Picking
- **Sofort eintragen** - nicht aus dem Gedächtnis später
- **Ehrlich sein** bei Fehlern und Trade Quality
- **Screenshots machen** von wichtigen Setups
- **Sessions gruppieren** - eine Strategie pro Session
- **Realistische Kosten** berücksichtigen

### ❌ DON'Ts:
- Nicht nur gewinnende Trades dokumentieren
- Nicht nachträglich "optimieren" (Backtradeing)
- Nicht unrealistische Fills annehmen
- Nicht Kosten vergessen
- Nicht emotional - objektiv bleiben

---

## Integration mit Trading Journal

### Option 1: Manuell importieren
Nach Abschluss der Backtest-Session können Sie die Trades in Ihre Datenbank importieren.

### Option 2: Separate Analyse
Nutzen Sie die CSV für getrennte Backtest-Analysen mit Excel/Python.

### Option 3: Spätere Integration
Erstellen Sie eine `backtest_trades` Tabelle in der Datenbank und importieren Sie alle Sessions.

---

## Beispiel-Eintrag

```csv
1,MACD_2026,2026-03-08 14:30:00,AAPL,LONG,150.25,152.75,100,248.00,1.66,148.50,154.00,TAKE_PROFIT,1.65,MACD Crossover + RSI<30,Mean Reversion,15min,8,,Good setup
```

**Interpretation:**
- Trade #1 in Session "MACD_2026"
- AAPL Long um 150.25, Exit bei 152.75
- 100 Aktien = €248 Gewinn (1.66%)
- Stop Loss bei 148.50, TP bei 154.00
- Exit via Take Profit
- 1.65R Gewinn (Risiko war €175, Gewinn €288)
- Setup: MACD Crossover + RSI<30
- Trade Quality: 8/10

---

## Nächste Schritte

1. **Wählen Sie ein Template** (Basic für den Start)
2. **Kopieren & umbenennen** Sie es
3. **Erste Trades dokumentieren**
4. **Nach 20-30 Trades**: Erste Analyse durchführen
5. **Nach 100+ Trades**: Automatisierte Auswertung erwägen

---

## Fragen?

Bei Fragen zur Dokumentation oder wenn Sie die Analysen automatisieren möchten:
- Nutzen Sie die bestehenden Analytics-Features
- Erstellen Sie Python-Scripts für CSV-Analyse
- Integrieren Sie in die DuckDB-Datenbank

Viel Erfolg beim Backtesting! 📊📈
