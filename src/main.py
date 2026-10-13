#!/usr/bin/env python3
"""Main entry point for the Trading Logbook and Journal application."""

import click
import csv
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tabulate import tabulate

from database.db_manager import DatabaseManager
from services.trade_service import TradeService
from services.journal_service import JournalService
from services.overnight_service import OvernightService
from utils.analytics import Analytics


@click.group()
def cli():
    """Trading Logbook and Journal - Track your trades and trading journey."""
    pass


@cli.command()
@click.option('--symbol', prompt='Symbol', help='Trading symbol (e.g., AAPL, BTCUSD)')
@click.option('--action', prompt='Action', type=click.Choice(['BUY', 'SELL']), help='Trade action')
@click.option('--quantity', prompt='Quantity', type=float, help='Number of shares/contracts')
@click.option('--price', prompt='Price', type=float, help='Entry/Exit price')
@click.option('--notes', default='', help='Optional notes about the trade')
def add_trade(symbol, action, quantity, price, notes):
    """Add a new trade to the logbook."""
    db = DatabaseManager()
    trade_service = TradeService(db)
    
    trade_id = trade_service.add_trade(
        symbol=symbol.upper(),
        action=action,
        quantity=quantity,
        price=price,
        notes=notes
    )
    
    click.echo(f"✓ Trade added successfully (ID: {trade_id})")


@cli.command()
@click.option('--limit', default=10, help='Number of recent trades to show')
@click.option('--symbol', default=None, help='Filter by symbol/instrument (e.g., AAPL, BTC)')
@click.option('--action', default=None, type=click.Choice(['BUY', 'SELL'], case_sensitive=False), help='Filter by action')
@click.option('--from-date', default=None, help='Filter trades from date (YYYY-MM-DD)')
@click.option('--to-date', default=None, help='Filter trades until date (YYYY-MM-DD)')
@click.option('--min-profit', default=None, type=float, help='Filter trades with minimum P/L')
@click.option('--max-profit', default=None, type=float, help='Filter trades with maximum P/L')
def list_trades(limit, symbol, action, from_date, to_date, min_profit, max_profit):
    """List recent trades with optional filters."""
    db = DatabaseManager()
    trade_service = TradeService(db)
    
    trades = trade_service.get_recent_trades(
        limit=limit, 
        include_overnight=True,
        symbol=symbol,
        action=action.upper() if action else None,
        from_date=from_date,
        to_date=to_date,
        min_profit=min_profit,
        max_profit=max_profit
    )
    
    if not trades:
        click.echo("No trades found.")
        return
    
    # Show active filters
    filters = []
    if symbol:
        filters.append(f"Symbol: {symbol}")
    if action:
        filters.append(f"Action: {action.upper()}")
    if from_date:
        filters.append(f"Von: {from_date}")
    if to_date:
        filters.append(f"Bis: {to_date}")
    if min_profit is not None:
        filters.append(f"Min P/L: {min_profit:.2f} €")
    if max_profit is not None:
        filters.append(f"Max P/L: {max_profit:.2f} €")
    
    if filters:
        click.echo("\n" + "="*80)
        click.echo("AKTIVE FILTER: " + " | ".join(filters))
        click.echo("="*80)
    
    headers = ['ID', 'Date', 'Open', 'Symbol', 'Action', 'Qty', 'Duration (min)', 'Open Price (€)', 'Close Price (€)', 
               'Gross (€)', 'Net (€)', 'FX Fee (€)', 'P/L (€)', 'Overnight (€)', 'Currency', 'Order#']
    table_data = []
    
    for trade in trades:
        order_num = trade.get('order_number_name', '-')
        order_num = order_num[:10] + '...' if order_num and len(order_num) > 10 else (order_num or '-')
        
        # Calculate trade duration in minutes
        duration_minutes = '-'
        if trade.get('timestamp') and trade.get('opening_time'):
            try:
                # Parse timestamps
                close_time = datetime.fromisoformat(trade['timestamp'].replace('+02:00', '').replace('+03:00', ''))
                open_time = datetime.fromisoformat(trade['opening_time'].replace('+02:00', '').replace('+03:00', ''))
                duration = close_time - open_time
                duration_minutes = f"{int(duration.total_seconds() / 60)}"
            except Exception:
                duration_minutes = '-'
        
        overnight_total = trade.get('overnight_fees_total', 0.0)
        
        table_data.append([
            trade['id'],
            trade['timestamp'][:10] if trade.get('timestamp') else '-',
            trade['opening_time'][:10] if trade.get('opening_time') else '-',
            trade['symbol'],
            trade['action'],
            f"{trade.get('quantity', 0):.2f}",
            duration_minutes,
            f"{trade.get('price', 0):.2f}",
            f"{trade.get('close_price', 0):.2f}",
            f"{trade.get('result_gross', 0):.2f}",
            f"{trade.get('result_net', 0):.2f}",
            f"{trade.get('fx_fee', 0):.2f}",
            f"{trade.get('result_after_fx_fee', 0):.2f}",
            f"{overnight_total:.2f}" if overnight_total != 0 else '-',
            trade.get('instrument_currency', '-'),
            order_num
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Show summary statistics for filtered trades
    total_pnl = sum(trade.get('result_after_fx_fee', 0) or 0 for trade in trades)
    total_overnight = sum(trade.get('overnight_fees_total', 0) or 0 for trade in trades)
    winning_trades = sum(1 for trade in trades if (trade.get('result_after_fx_fee', 0) or 0) > 0)
    losing_trades = sum(1 for trade in trades if (trade.get('result_after_fx_fee', 0) or 0) < 0)
    
    click.echo("\n" + "="*100)
    click.echo(f"ZUSAMMENFASSUNG: {len(trades)} Trades | Gewinne: {winning_trades} | Verluste: {losing_trades}")
    click.echo(f"Gesamt P/L: {total_pnl:.2f} € | Overnight Fees: {total_overnight:.2f} € | Total: {(total_pnl + total_overnight):.2f} €")
    click.echo("="*100 + "\n")


@cli.command()
@click.option('--limit', default=20, help='Number of recent overnight fees to show')
def list_overnight(limit):
    """List recent overnight fees."""
    db = DatabaseManager()
    overnight_service = OvernightService(db)
    
    fees = overnight_service.get_recent_fees(limit)
    
    if not fees:
        click.echo("No overnight fees found.")
        return
    
    headers = ['ID', 'Date', 'Symbol', 'Direction', 'Quantity', 'Interest', 'Currency', 'Order Number']
    table_data = []
    
    for fee in fees:
        order_num = fee.get('order_number_name', '')
        # Truncate order number for display
        order_num = order_num[:12] + '...' if order_num and len(order_num) > 12 else (order_num or '-')
        currency = fee.get('instrument_currency', '-')
        table_data.append([
            fee['id'],
            fee['timestamp'][:10],
            fee['symbol'],
            fee['direction'],
            f"{fee['quantity']:.2f}",
            f"€{fee['interest']:.2f}",
            currency,
            order_num
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Show total interest
    total_interest = overnight_service.get_total_interest()
    click.echo(f"\nTotal overnight interest: €{total_interest:.2f}")


@cli.command()
@click.option('--output', default='trades_export.csv', help='Output CSV filename')
@click.option('--limit', default=None, type=int, help='Limit number of trades to export (all if not specified)')
def export_trades(output, limit):
    """Export trades to a CSV file."""
    db = DatabaseManager()
    trade_service = TradeService(db)
    
    # Get trades
    if limit:
        trades = trade_service.get_recent_trades(limit)
    else:
        # Get all trades
        all_trades = db.execute_query('SELECT * FROM trades ORDER BY timestamp DESC')
        trades = [dict(row) for row in all_trades]
    
    if not trades:
        click.echo("No trades to export.")
        return
    
    # Write to CSV
    output_path = Path(output)
    
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'symbol', 'action', 'quantity', 'price', 'total', 'notes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';', quoting=csv.QUOTE_ALL)
            
            writer.writeheader()
            
            for trade in trades:
                total = trade['quantity'] * trade['price']
                writer.writerow({
                    'timestamp': trade['timestamp'],
                    'symbol': trade['symbol'],
                    'action': trade['action'],
                    'quantity': trade['quantity'],
                    'price': trade['price'],
                    'total': total,
                    'notes': trade.get('notes', '')
                })
        
        click.echo(f"✓ Exported {len(trades)} trades to {output_path}")
        
    except Exception as e:
        click.echo(f"✗ Error exporting trades: {e}")


@cli.command()
@click.option('--title', prompt='Title', help='Journal entry title')
@click.option('--content', prompt='Content', help='Journal entry content')
@click.option('--tags', default='', help='Comma-separated tags')
def add_journal(title, content, tags):
    """Add a new journal entry."""
    db = DatabaseManager()
    journal_service = JournalService(db)
    
    entry_id = journal_service.add_entry(title, content, tags)
    
    click.echo(f"✓ Journal entry added successfully (ID: {entry_id})")


@cli.command()
@click.option('--limit', default=5, help='Number of recent entries to show')
def list_journal(limit):
    """List recent journal entries."""
    db = DatabaseManager()
    journal_service = JournalService(db)
    
    entries = journal_service.get_recent_entries(limit)
    
    if not entries:
        click.echo("No journal entries found.")
        return
    
    headers = ['ID', 'Date', 'Title', 'Tags', 'Content']
    table_data = []
    
    for entry in entries:
        # Truncate content for table display
        content_preview = entry['content'][:50] + '...' if len(entry['content']) > 50 else entry['content']
        table_data.append([
            entry['id'],
            entry['timestamp'][:10],
            entry['title'],
            entry['tags'] or 'None',
            content_preview
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@cli.command()
@click.option('--period', default='day', type=click.Choice(['day', 'week', 'month', 'year']), help='Time period for grouping trades')
@click.option('--limit', default=10, type=int, help='Limit number of periods to show (default: 10)')
def analytics(period, limit):
    """Display trading performance analytics grouped by time period."""
    db = DatabaseManager()
    analytics_service = Analytics(db)
    
    # Get trades per period
    trades_per_period = analytics_service.get_trades_per_period(period, limit)
    
    if not trades_per_period:
        click.echo("No trades available for analysis.")
        return
    
    period_name = {'day': 'Tag', 'week': 'Woche', 'month': 'Monat', 'year': 'Jahr'}
    _display_period_analytics(trades_per_period, period_name[period], period)


@cli.command()
@click.option('--limit', default=None, type=int, 
              help='Limit number of instruments to show (default: all)')
def instrument_stats(limit):
    """Display trading statistics grouped by instrument/symbol."""
    db = DatabaseManager()
    analytics_service = Analytics(db)
    
    # Get instrument statistics
    stats = analytics_service.get_all_instrument_stats(limit=limit)
    
    if not stats:
        click.echo("No instrument statistics available.")
        return
    
    _display_instrument_stats(stats)


def _display_period_analytics(trades_per_period, period_name, period_key):
    """Helper function to display analytics for a specific period."""
    # Get target for this period (same for all rows)
    period_target = trades_per_period[0].get('target_profit', 0.0) if trades_per_period else 0.0
    
    # Display header
    click.echo("\n" + "="*120)
    click.echo(f"TRADES PRO {period_name.upper()}")
    click.echo(f"Ziel pro {period_name}: {period_target:.2f} €")
    click.echo("="*120)
    
    # Create table
    headers = ['Zeitraum', 'Anzahl Trades', 'Gewinn/Verlust', 'Durchschn. P/L', 'Overnight Fees', 'Total', 'Abweichung']
    table_data = []
    
    total_trades = 0
    total_pnl = 0.0
    total_overnight = 0.0
    total_combined = 0.0
    total_target = 0.0
    total_deviation = 0.0
    
    for row in trades_per_period:
        count = row['trade_count']
        pnl = row['total_pnl'] or 0.0
        avg_pnl = row['avg_pnl'] or 0.0
        overnight_fees = row.get('overnight_fees', 0.0)
        combined_total = pnl + overnight_fees
        target = row.get('target_profit', 0.0)
        deviation = row.get('deviation_from_target', 0.0)
        
        total_trades += count
        total_pnl += pnl
        total_overnight += overnight_fees
        total_combined += combined_total
        total_target += target
        total_deviation += deviation
        
        table_data.append([
            row['period'],
            count,
            f"{pnl:.2f} €",
            f"{avg_pnl:.2f} €",
            f"{overnight_fees:.2f} €" if overnight_fees != 0 else '-',
            f"{combined_total:.2f} €",
            f"{deviation:.2f} €"
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Summary
    click.echo("\n" + "="*120)
    click.echo(f"Gesamt: {total_trades} Trades | P/L: {total_pnl:.2f} € | Overnight Fees: {total_overnight:.2f} € | Total: {total_combined:.2f} €")
    click.echo(f"Ziel Gesamt: {total_target:.2f} € | Abweichung: {total_deviation:.2f} €")
    click.echo("="*120 + "\n")


def _display_instrument_stats(stats):
    """Helper function to display instrument statistics."""
    # Display header
    click.echo("\n" + "="*120)
    click.echo("INSTRUMENT STATISTIKEN")
    click.echo("="*120)
    
    # Create table
    headers = ['Symbol', 'Trades', 'Wins', 'Losses', 'Win%', 'Total P/L (€)', 
               'Avg P/L (€)', 'Best (€)', 'Worst (€)', 'Overnight (€)', 'Net Total (€)']
    table_data = []
    
    # Totals
    total_trades = 0
    total_wins = 0
    total_losses = 0
    total_pnl = 0.0
    total_overnight = 0.0
    
    for row in stats:
        # Build row data
        trades = row['total_trades']
        wins = row.get('winning_trades', 0)
        losses = row.get('losing_trades', 0)
        win_rate = row.get('win_rate', 0.0) * 100
        pnl = row.get('total_pnl', 0.0)
        avg_pnl = row.get('avg_pnl', 0.0)
        best = row.get('largest_win', 0.0)
        worst = row.get('largest_loss', 0.0)
        overnight = row.get('overnight_fees', 0.0)
        net_total = row.get('net_total', 0.0)
        
        # Accumulate totals
        total_trades += trades
        total_wins += wins
        total_losses += losses
        total_pnl += pnl
        total_overnight += overnight
        
        table_data.append([
            row['symbol'],
            trades,
            wins,
            losses,
            f"{win_rate:.1f}%",
            f"{pnl:.2f}",
            f"{avg_pnl:.2f}",
            f"{best:.2f}",
            f"{worst:.2f}",
            f"{overnight:.2f}" if overnight != 0 else '-',
            f"{net_total:.2f}"
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    # Summary
    total_net = total_pnl + total_overnight
    total_closed = total_wins + total_losses
    overall_win_rate = (total_wins / total_closed * 100) if total_closed > 0 else 0.0
    
    click.echo("\n" + "="*120)
    click.echo(f"Gesamt: {total_trades} Trades | Wins: {total_wins} | Losses: {total_losses} | Win Rate: {overall_win_rate:.1f}%")
    click.echo(f"P/L: €{total_pnl:.2f} | Overnight: €{total_overnight:.2f} | Net: €{total_net:.2f}")
    click.echo("="*120 + "\n")


@cli.command()
def init():
    """Initialize the database."""
    db = DatabaseManager()
    click.echo("✓ Database initialized successfully.")


@cli.command()
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def rebuild_database(confirm):
    """Rebuild database from archive files (trades and overnight fees)."""
    
    if not confirm:
        click.echo("\n⚠ WARNUNG: Diese Funktion wird die Datenbank komplett neu aufbauen!")
        click.echo("  - Alle Trades werden gelöscht und neu importiert")
        click.echo("  - Alle Overnight-Fees werden gelöscht und neu importiert")
        click.echo("  - Journal-Einträge bleiben erhalten")
        click.echo("  - Archiv-Dateien werden NICHT verändert\n")
        
        if not click.confirm("Möchten Sie fortfahren?"):
            click.echo("✗ Abgebrochen")
            return
    
    db = DatabaseManager()
    
    # Step 1: Clear trades and overnight fees tables
    click.echo("\n" + "="*60)
    click.echo("Schritt 1: Leere Datenbank-Tabellen")
    click.echo("="*60)
    
    try:
        db.execute_query('DELETE FROM trades')
        db.execute_query('DELETE FROM overnight_fees')
        db.execute_query('ALTER SEQUENCE trades_id_seq RESTART WITH 1')
        db.execute_query('ALTER SEQUENCE overnight_fees_id_seq RESTART WITH 1')
        click.echo("✓ Tabellen geleert")
    except Exception as e:
        click.echo(f"✗ Fehler beim Leeren der Tabellen: {e}")
        return
    
    # Step 2: Re-import trades from archive
    click.echo("\n" + "="*60)
    click.echo("Schritt 2: Importiere Trades aus Archiv")
    click.echo("="*60)
    
    archive_trades_dir = Path(__file__).parent.parent / "archive" / "trades"
    
    if not archive_trades_dir.exists():
        click.echo(f"✗ Archiv-Verzeichnis nicht gefunden: {archive_trades_dir}")
    else:
        json_files = list(archive_trades_dir.rglob('*.json'))
        click.echo(f"Gefunden: {len(json_files)} Trade-Dateien im Archiv")
        
        trade_service = TradeService(db)
        imported_count = 0
        skipped_count = 0
        
        # Instrument code mapping
        instrument_code_mapping = {
            '#NQ': 'USA Tech 100',
            '#AX': 'Germany40'
        }
        
        for filepath in json_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    trade = json.load(file)
                
                # Extract external ID from orderNumber
                order_number_id = None
                order_number = trade.get('orderNumber', {})
                if isinstance(order_number, dict):
                    order_number_id = order_number.get('id')
                
                # Extract and map code
                code = trade.get('code', '')
                if code[:3] in instrument_code_mapping:
                    code = instrument_code_mapping.get(code[:3])
                
                # Map direction
                direction = trade.get('direction', '')
                if direction == 'buy':
                    action = 'BUY'
                elif direction == 'sell':
                    action = 'SELL'
                else:
                    action = direction.upper()
                
                # Extract all fields
                quantity = float(trade.get('quantity', 0))
                price = float(trade.get('price', 0))
                close_price = float(trade.get('closePrice', 0))
                result_gross = float(trade.get('resultGross', 0))
                result_net = float(trade.get('resultNet', 0))
                fx_fee = float(trade.get('fxFee', 0))
                result_after_fx_fee = float(trade.get('resultAfterFxFeeAccountCurrency', 0))
                realised_profit_loss_account_currency = float(trade.get('realisedProfitLossAccountCurrency', 0))
                realised_profit_loss_instrument_currency = float(trade.get('realisedProfitLossInstrumentCurrency', 0))
                net_result_account_currency = float(trade.get('netResultAccountCurrency', 0))
                
                instrument_currency = trade.get('instrumentCurrency', '')
                event_type = trade.get('eventType', '')
                
                event_number_obj = trade.get('eventNumber', {})
                event_number = event_number_obj.get('name', '') if isinstance(event_number_obj, dict) else ''
                
                order_name = order_number.get('name', '') if isinstance(order_number, dict) else ''
                
                timestamp = trade.get('time', '')
                opening_time = trade.get('openingTime', '')
                
                notes = f"P/L: {result_after_fx_fee:.2f} | Opened: {opening_time[:19]} | Closed: {timestamp[:19]}"
                
                # Add trade to database
                trade_service.add_trade(
                    symbol=code,
                    action=action,
                    quantity=quantity,
                    price=price,
                    close_price=close_price,
                    timestamp=timestamp,
                    opening_time=opening_time,
                    result_gross=result_gross,
                    result_net=result_net,
                    fx_fee=fx_fee,
                    result_after_fx_fee=result_after_fx_fee,
                    realised_profit_loss_account_currency=realised_profit_loss_account_currency,
                    realised_profit_loss_instrument_currency=realised_profit_loss_instrument_currency,
                    net_result_account_currency=net_result_account_currency,
                    instrument_currency=instrument_currency,
                    event_type=event_type,
                    event_number=event_number,
                    order_number_name=order_name,
                    order_number_id=order_number_id,
                    notes=notes
                )
                imported_count += 1
                
            except Exception as e:
                click.echo(f"⚠ Fehler beim Importieren von {filepath.name}: {e}")
                skipped_count += 1
        
        click.echo(f"✓ Trades importiert: {imported_count}")
        if skipped_count > 0:
            click.echo(f"  Übersprungen: {skipped_count}")
    
    # Step 3: Re-import overnight fees from archive
    click.echo("\n" + "="*60)
    click.echo("Schritt 3: Importiere Overnight-Fees aus Archiv")
    click.echo("="*60)
    
    archive_overnight_dir = Path(__file__).parent.parent / "archive" / "overnight"
    
    if not archive_overnight_dir.exists():
        click.echo(f"✗ Archiv-Verzeichnis nicht gefunden: {archive_overnight_dir}")
    else:
        json_files = list(archive_overnight_dir.rglob('*.json'))
        click.echo(f"Gefunden: {len(json_files)} Overnight-Dateien im Archiv")
        
        overnight_service = OvernightService(db)
        imported_count = 0
        skipped_count = 0
        
        # Instrument code mapping
        instrument_code_mapping = {
            '#NQ': 'USA Tech 100',
            '#AX': 'Germany40'
        }
        
        for filepath in json_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    record = json.load(file)
                
                # Extract external ID
                order_number_id = record.get('id')
                
                # Extract and map code
                code = record.get('code', '')
                if code[:3] in instrument_code_mapping:
                    code = instrument_code_mapping.get(code[:3])
                
                # Map direction
                direction = record.get('direction', '').upper()
                
                quantity = float(record.get('quantity', 0))
                interest = float(record.get('interest', 0))
                timestamp = record.get('time', '')
                instrument_currency = record.get('instrumentCurrency', '')
                
                # Extract order number
                order_number_name = None
                order_num_obj = record.get('orderNumber', {})
                if isinstance(order_num_obj, dict):
                    order_number_name = order_num_obj.get('name')
                
                # Add overnight fee to database
                overnight_service.add_overnight_fee(
                    timestamp=timestamp,
                    symbol=code,
                    direction=direction,
                    quantity=quantity,
                    interest=interest,
                    instrument_currency=instrument_currency,
                    order_number_id=order_number_id,
                    order_number_name=order_number_name
                )
                imported_count += 1
                
            except Exception as e:
                click.echo(f"⚠ Fehler beim Importieren von {filepath.name}: {e}")
                skipped_count += 1
        
        click.echo(f"✓ Overnight-Fees importiert: {imported_count}")
        if skipped_count > 0:
            click.echo(f"  Übersprungen: {skipped_count}")
    
    # Summary
    click.echo("\n" + "="*60)
    click.echo("ZUSAMMENFASSUNG")
    click.echo("="*60)
    click.echo("✓ Datenbank erfolgreich neu aufgebaut!")
    click.echo(f"  Archiv-Verzeichnisse wurden NICHT verändert")
    click.echo(f"  Sie können diese Funktion jederzeit wiederholen")
    click.echo("="*60 + "\n")


@cli.command()
def manual():
    """Display comprehensive help and usage information."""
    help_text = """
╔════════════════════════════════════════════════════════════════════════════╗
║                   TRADING LOGBOOK AND JOURNAL - HELP                       ║
╚════════════════════════════════════════════════════════════════════════════╝

DESCRIPTION:
    A comprehensive tool for tracking trades and maintaining a trading journal
    with performance analytics. Stores data in a local DuckDB database.

USAGE:
    python3 src/main.py [COMMAND] [OPTIONS]

AVAILABLE COMMANDS:

  init
      Initialize the database (run this first time)
      Example: python3 src/main.py init

  add-trade
      Add a new trade to your logbook
      Options:
        --symbol TEXT      Trading symbol (e.g., AAPL, TSLA, BTCUSD)
        --action [BUY|SELL]  Trade action
        --quantity FLOAT   Number of shares/contracts
        --price FLOAT      Entry/Exit price per unit
        --notes TEXT       Optional notes about the trade
      
      Interactive mode (prompts for each field):
        python3 src/main.py add-trade
      
      Non-interactive mode (provide all options):
        python3 src/main.py add-trade --symbol AAPL --action BUY --quantity 100 --price 150.50 --notes "Strong bullish signal"

  list-trades
      Display recent trades in a formatted table
      Options:
        --limit INTEGER    Number of recent trades to show (default: 10)
      
      Example:
        python3 src/main.py list-trades --limit 20

  list-overnight
      Display recent overnight fees in a formatted table
      Options:
        --limit INTEGER    Number of recent overnight fees to show (default: 20)
      
      Example:
        python3 src/main.py list-overnight --limit 50

  export-trades
      Export trades to a CSV file
      Options:
        --output TEXT      Output CSV filename (default: trades_export.csv)
        --limit INTEGER    Limit number of trades to export (all if not specified)
      
      Examples:
        python3 src/main.py export-trades
        python3 src/main.py export-trades --output my_trades.csv
        python3 src/main.py export-trades --limit 50

  add-journal
      Add a new journal entry to document your trading thoughts
      Options:
        --title TEXT       Entry title
        --content TEXT     Entry content/body
        --tags TEXT        Comma-separated tags (e.g., "strategy,reflection")
      
      Interactive mode:
        python3 src/main.py add-journal
      
      Non-interactive mode:
        python3 src/main.py add-journal --title "Market Analysis" --content "Noticed strong support at 150" --tags "analysis,support"

  list-journal
      Display recent journal entries
      Options:
        --limit INTEGER    Number of recent entries to show (default: 5)
      
      Example:
        python3 src/main.py list-journal --limit 10

  analytics
      Display trading performance analytics grouped by time period
      Options:
        --period [day|week|month|year]  Time period for grouping (default: day)
        --limit INTEGER                 Limit number of periods to show (default: 10)
      
      Examples:
        python3 src/main.py analytics
        python3 src/main.py analytics --period month --limit 12
        python3 src/main.py analytics --period year

  risk-calculator
      Calculate risk amounts for different percentages of your portfolio
      Options:
        --portfolio FLOAT  Portfolio value in Euro (auto-calculated from DB if not specified)
      
      Examples:
        python3 src/main.py risk-calculator
        python3 src/main.py risk-calculator --portfolio 10000

  position-size
      Calculate optimal position size for CFD trading with leverage
      Options:
        --portfolio FLOAT      Portfolio value in Euro (auto-calculated from DB)
        --risk-percent FLOAT   Risk percentage (e.g., 2 for 2%)
        --entry-price FLOAT    Planned entry price
        --stop-loss FLOAT      Stop-loss price
        --leverage FLOAT       Leverage multiplier (default: 20)
      
      Examples:
        python3 src/main.py position-size
        python3 src/main.py position-size --portfolio 10000 --risk-percent 2 --entry-price 18500 --stop-loss 18300 --leverage 20

  rebuild-database
      Rebuild database from archive files (complete re-import)
      WARNING: Deletes all trades and overnight fees, then re-imports from archive
      Options:
        --confirm  Skip confirmation prompt
      
      Examples:
        python3 src/main.py rebuild-database
        python3 src/main.py rebuild-database --confirm

  manual
      Display this help information
      
      Example:
        python3 src/main.py manual

GETTING STARTED:

  1. Initialize the database:
     python3 src/main.py init

  2. Add your first trade:
     python3 src/main.py add-trade

  3. View your trades:
     python3 src/main.py list-trades

  4. Add a journal entry:
     python3 src/main.py add-journal

  5. Check your performance:
     python3 src/main.py analytics

TIPS:

  • Use --help with any command for detailed options: 
      python3 src/main.py add-trade --help
  
  • Commands can be run in interactive mode (with prompts) or 
    non-interactive mode (with all options provided)
  
  • Database file is stored in: data/trading_journal.db
  
  • All timestamps are automatically recorded
  
  • Use tags in journal entries to organize your thoughts and 
    make them easier to search later

For more information, visit the README.md file.
════════════════════════════════════════════════════════════════════════════
"""
    click.echo(help_text)


@cli.command()
@click.option('--portfolio', default=None, type=float, help='Portfolio-Wert in Euro (wird aus Datenbank berechnet, wenn nicht angegeben)')
def risk_calculator(portfolio):
    """Berechne Risiko-Beträge für verschiedene Prozentsätze des Portfolios."""
    
    db = DatabaseManager()
    
    # Wenn kein Portfolio-Wert angegeben, berechne aus Datenbank
    if portfolio is None:
        # Summe aller realisierten Trades
        trade_result = db.execute_query(
            'SELECT SUM(result_after_fx_fee) as total FROM trades WHERE result_after_fx_fee IS NOT NULL'
        )
        total_trades = trade_result[0]['total'] if trade_result and trade_result[0]['total'] else 0.0
        
        # Summe aller Overnight-Zinsen (sind negativ)
        overnight_service = OvernightService(db)
        total_overnight = overnight_service.get_total_interest()
        
        # Berechne Portfolio-Wert
        portfolio = total_trades + total_overnight  # overnight ist negativ, daher addition
        
        click.echo(f"\nPortfolio-Wert aus Datenbank berechnet:")
        click.echo(f"  Realisierte Trades: €{total_trades:,.2f}")
        click.echo(f"  Overnight-Zinsen:   €{total_overnight:,.2f}")
        click.echo(f"  Portfolio-Wert:     €{portfolio:,.2f}")
    
    if portfolio <= 0:
        click.echo("\n✗ Portfolio-Wert muss größer als 0 sein.")
        click.echo("  Tipp: Fügen Sie Trades zur Datenbank hinzu oder geben Sie einen Wert manuell an.")
        return
    
    click.echo("\n" + "="*60)
    click.echo(f"RISIKO-RECHNER - Portfolio: €{portfolio:,.2f}")
    click.echo("="*60)
    
    risk_percentages = [1, 2, 3, 4, 5, 10]
    
    headers = ['Risiko %', 'Betrag (€)', 'Verbleibendes Kapital (€)']
    table_data = []
    
    for percentage in risk_percentages:
        risk_amount = portfolio * (percentage / 100)
        remaining = portfolio - risk_amount
        
        table_data.append([
            f"{percentage}%",
            f"€{risk_amount:,.2f}",
            f"€{remaining:,.2f}"
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    click.echo("\n" + "="*60)
    click.echo("EMPFEHLUNG:")
    click.echo("  • Anfänger: 1-2% Risiko pro Trade")
    click.echo("  • Fortgeschritten: 2-3% Risiko pro Trade")
    click.echo("  • Erfahren: 3-5% Risiko pro Trade")
    click.echo("  • Warnung: >5% Risiko kann zu schnellem Kapitalverlust führen")
    click.echo("="*60 + "\n")


@cli.command()
@click.option('--portfolio', default=None, type=float, help='Portfolio-Wert in Euro (wird aus Datenbank berechnet, wenn nicht angegeben)')
@click.option('--risk-percent', prompt='Risiko in %', type=float, help='Risiko-Prozentsatz (z.B. 2 für 2%)')
@click.option('--entry-price', prompt='Einstiegspreis', type=float, help='Geplanter Einstiegspreis')
@click.option('--stop-loss', prompt='Stop-Loss', type=float, help='Stop-Loss-Preis')
@click.option('--leverage', default=20, type=float, help='Hebel (default: 20)')
def position_size(portfolio, risk_percent, entry_price, stop_loss, leverage):
    """Berechne optimale Positionsgröße für CFD-Trading mit Hebel."""
    
    db = DatabaseManager()
    
    # Wenn kein Portfolio-Wert angegeben, berechne aus Datenbank
    if portfolio is None:
        trade_result = db.execute_query(
            'SELECT SUM(result_after_fx_fee) as total FROM trades WHERE result_after_fx_fee IS NOT NULL'
        )
        total_trades = trade_result[0]['total'] if trade_result and trade_result[0]['total'] else 0.0
        
        overnight_service = OvernightService(db)
        total_overnight = overnight_service.get_total_interest()
        
        portfolio = total_trades + total_overnight
        
        if portfolio <= 0:
            click.echo("\n✗ Kein Portfolio-Wert in der Datenbank gefunden.")
            click.echo("  Bitte geben Sie einen Wert mit --portfolio an.")
            return
        
        click.echo(f"\nPortfolio-Wert aus Datenbank: €{portfolio:,.2f}")
    
    # Validierung
    if entry_price <= 0 or stop_loss <= 0:
        click.echo("\n✗ Einstiegspreis und Stop-Loss müssen größer als 0 sein.")
        return
    
    if risk_percent <= 0 or risk_percent > 100:
        click.echo("\n✗ Risiko-Prozentsatz muss zwischen 0 und 100 liegen.")
        return
    
    # Berechnung
    risk_amount = portfolio * (risk_percent / 100)
    stop_loss_distance = abs(entry_price - stop_loss)
    stop_loss_percent = (stop_loss_distance / entry_price) * 100
    
    # Positionsgröße berechnen
    # Risikobetrag / Stop-Loss-Distanz = Anzahl Kontrakte/Einheiten
    position_size = risk_amount / stop_loss_distance
    position_value = position_size * entry_price
    
    # Margin-Anforderung (mit Hebel)
    margin_required = position_value / leverage
    
    # Verfügbare Margin nach Trade
    remaining_margin = portfolio - margin_required
    margin_usage_percent = (margin_required / portfolio) * 100
    
    # Möglicher Verlust/Gewinn bei verschiedenen Szenarien
    loss_at_sl = position_size * stop_loss_distance
    
    # Display
    click.echo("\n" + "="*70)
    click.echo("POSITIONSGRÖSSENRECHNER (CFD mit Hebel)")
    click.echo("="*70)
    
    click.echo(f"\n📊 EINGABEPARAMETER:")
    click.echo(f"  Portfolio-Wert:     €{portfolio:,.2f}")
    click.echo(f"  Risiko:             {risk_percent}% (€{risk_amount:,.2f})")
    click.echo(f"  Einstiegspreis:     €{entry_price:,.2f}")
    click.echo(f"  Stop-Loss:          €{stop_loss:,.2f}")
    click.echo(f"  Stop-Loss-Distanz:  €{stop_loss_distance:,.2f} ({stop_loss_percent:.2f}%)")
    click.echo(f"  Hebel:              {leverage:.0f}x")
    
    click.echo(f"\n🎯 BERECHNETE POSITION:")
    click.echo(f"  Positionsgröße:     {position_size:,.2f} Kontrakte/Einheiten")
    click.echo(f"  Positionswert:      €{position_value:,.2f}")
    click.echo(f"  Benötigte Margin:   €{margin_required:,.2f} ({margin_usage_percent:.1f}% des Portfolios)")
    click.echo(f"  Verbleibende Margin: €{remaining_margin:,.2f}")
    
    click.echo(f"\n📉 RISIKO-SZENARIEN:")
    click.echo(f"  Verlust bei Stop-Loss: €{loss_at_sl:,.2f} ({risk_percent}% des Portfolios)")
    
    # Verschiedene Kursszenarien
    scenarios = [
        (-2, "2% Kursverlust"),
        (-1, "1% Kursverlust"),
        (-0.5, "0.5% Kursverlust"),
        (-0.25, "0.25% Kursverlust"),
        (0, "Breakeven (0%)"),
        (0.25, "0.25% Kursgewinn"),
        (0.5, "0.5% Kursgewinn"),
        (1, "1% Kursgewinn"),
        (2, "2% Kursgewinn")
    ]
    
    click.echo(f"\n📈 GEWINN/VERLUST-SZENARIEN:")
    headers = ['Szenario', 'Kursänderung (€)', 'Neuer Kurs', 'G/V (€)', 'G/V (% Portfolio)']
    table_data = []
    
    for percent_change, label in scenarios:
        new_price = entry_price * (1 + percent_change/100)
        price_change = new_price - entry_price
        pnl = position_size * price_change
        pnl_percent = (pnl / portfolio) * 100
        
        table_data.append([
            label,
            f"{price_change:+.2f}",
            f"€{new_price:,.2f}",
            f"€{pnl:,.2f}",
            f"{pnl_percent:+.2f}%"
        ])
    
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
    
    click.echo("\n" + "="*70)
    click.echo("⚠ WICHTIGE HINWEISE:")
    click.echo("  • Stellen Sie sicher, dass genug freie Margin vorhanden ist")
    click.echo("  • Berücksichtigen Sie Spreads und Gebühren")
    click.echo("  • Hebel vergrößert sowohl Gewinne als auch Verluste")
    click.echo("  • Stop-Loss diszipliniert einhalten!")
    
    if margin_usage_percent > 50:
        click.echo("\n⚠ WARNUNG: Margin-Nutzung über 50%! Hohes Risiko eines Margin Calls!")
    elif margin_usage_percent > 30:
        click.echo("\n⚠ Achtung: Margin-Nutzung über 30%. Vorsicht bei volatilen Märkten!")
    
    click.echo("="*70 + "\n")


if __name__ == '__main__':
    cli()
