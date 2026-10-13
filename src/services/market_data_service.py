"""Service for fetching and normalizing external market index data."""

from datetime import datetime, UTC
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

from utils.config import Config


logger = logging.getLogger(__name__)


class MarketDataService:
    """Fetches quote snapshots for configured market indices."""

    CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
    BROWSER_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/",
        "Origin": "https://finance.yahoo.com",
    }
    SUPPORTED_RANGES: Dict[str, Dict[str, Any]] = {
        "1d": {"label": "1 Day", "chart_interval": "5m", "use_batch_quote": True},
        "5d": {"label": "5 Days", "chart_interval": "1h", "use_batch_quote": False},
        "1wk": {"label": "1 Week", "chart_interval": "1d", "use_batch_quote": False},
        "1mo": {"label": "1 Month", "chart_interval": "1d", "use_batch_quote": False},
        "3mo": {"label": "3 Months", "chart_interval": "1d", "use_batch_quote": False},
        "6mo": {"label": "6 Months", "chart_interval": "1d", "use_batch_quote": False},
    }
    _cache_until_by_range: Dict[str, float] = {}
    _cache_indices_by_range: Dict[str, List[Dict[str, Any]]] = {}
    _cache_errors_by_range: Dict[str, List[Dict[str, str]]] = {}

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.timeout = self.config.get("market.timeout_seconds", 8)
        self.request_delay_seconds = self.config.get("market.request_delay_seconds", 1.2)
        self.max_retries = self.config.get("market.max_retries", 2)
        self.retry_backoff_seconds = self.config.get("market.retry_backoff_seconds", 2.0)
        self.cache_ttl_seconds = self.config.get("market.cache_ttl_seconds", 30)
        self.source_name = self.config.get("market.source", "Yahoo Finance")
        self.session = requests.Session()
        self.session.headers.update(self.BROWSER_HEADERS)
        self.index_mappings = self.config.get(
            "market.indices",
            [
                {"name": "US100", "provider_symbol": "^NDX"},
                {"name": "US30", "provider_symbol": "^DJI"},
            ],
        )

    def get_us_indices_snapshot(self, requested_range: str = "1d") -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """Return normalized quotes for configured index mappings for a selected range."""
        selected_range = self._normalize_range(requested_range)

        if self._is_cache_valid(selected_range):
            return (
                list(self.__class__._cache_indices_by_range.get(selected_range, [])),
                list(self.__class__._cache_errors_by_range.get(selected_range, [])),
            )

        indices: List[Dict[str, Any]] = []
        errors: List[Dict[str, str]] = []
        use_batch_quote = self.SUPPORTED_RANGES[selected_range]["use_batch_quote"]

        if use_batch_quote:
            try:
                quote_rows_by_symbol = self._fetch_indices_batch()
            except Exception:
                # Some environments reject this endpoint with 401. Fall back to per-symbol chart calls.
                quote_rows_by_symbol = {}
        else:
            quote_rows_by_symbol = {}

        for idx, mapping in enumerate(self.index_mappings):
            provider_symbol = mapping.get("provider_symbol", "")
            quote_row = quote_rows_by_symbol.get(provider_symbol)

            try:
                if quote_row:
                    indices.append(self._normalize_quote_row(mapping, quote_row))
                    continue

                if idx > 0 and self.request_delay_seconds > 0:
                    time.sleep(self.request_delay_seconds)

                indices.append(self._fetch_index(mapping, selected_range))
            except Exception as exc:
                failed_row = self._build_failed_row(mapping, str(exc))
                indices.append(failed_row)
                errors.append(
                    {
                        "symbol": provider_symbol,
                        "name": mapping.get("name", ""),
                        "message": str(exc),
                    }
                )

        self.__class__._cache_indices_by_range[selected_range] = list(indices)
        self.__class__._cache_errors_by_range[selected_range] = list(errors)
        self.__class__._cache_until_by_range[selected_range] = time.time() + max(0, self.cache_ttl_seconds)

        return indices, errors

    def get_single_index_snapshot(
        self,
        provider_symbol: str,
        name: Optional[str] = None,
        requested_range: str = "1d",
    ) -> Dict[str, Any]:
        """Fetch one configured index snapshot, returning an error row on failure."""
        selected_range = self._normalize_range(requested_range)
        mapping = self._find_mapping(provider_symbol, name)
        try:
            row = self._fetch_index(mapping, selected_range)
            self._update_cached_row(row, selected_range)
            return row
        except Exception as exc:
            failed_row = self._build_failed_row(mapping, str(exc))
            self._update_cached_row(failed_row, selected_range)
            return failed_row

    def _fetch_index(self, mapping: Dict[str, str], selected_range: str = "1d") -> Dict[str, Any]:
        provider_symbol = mapping["provider_symbol"]
        display_name = mapping["name"]

        payload = self._request_chart_payload(provider_symbol, selected_range)
        result = payload.get("chart", {}).get("result")
        if not result:
            error = payload.get("chart", {}).get("error")
            raise ValueError(error.get("description") if isinstance(error, dict) else "Missing chart data")

        chart_result = result[0]
        meta = chart_result.get("meta", {})
        fifty_two_week_high = self._to_float(meta.get("fiftyTwoWeekHigh"))
        fifty_two_week_low = self._to_float(meta.get("fiftyTwoWeekLow"))
        interval_start_time, interval_end_time = self._extract_interval_bounds(chart_result)

        if selected_range == "1d":
            last = self._to_float(meta.get("regularMarketPrice"))
            prev = self._to_float(meta.get("chartPreviousClose") or meta.get("previousClose"))
            high = self._to_float(meta.get("regularMarketDayHigh"))
            low = self._to_float(meta.get("regularMarketDayLow"))
            change = self._to_float(meta.get("regularMarketChange"))
            change_percent = self._to_float(meta.get("regularMarketChangePercent"))

            if change is None and last is not None and prev is not None:
                change = last - prev

            if change_percent is None and prev not in (None, 0) and last is not None:
                change_percent = ((last - prev) / prev) * 100

            market_time = self._format_timestamp(meta.get("regularMarketTime"))
            if not interval_end_time:
                interval_end_time = market_time
            if not interval_start_time:
                interval_start_time = interval_end_time
        else:
            metrics = self._build_interval_metrics(chart_result)
            last = metrics["last"]
            prev = metrics["prev"]
            high = metrics["high"]
            low = metrics["low"]
            change = metrics["change"]
            change_percent = metrics["change_percent"]
            market_time = metrics["time"]
            interval_start_time = metrics["interval_start_time"]
            interval_end_time = metrics["interval_end_time"]

        return {
            "symbol": provider_symbol,
            "name": display_name,
            "time": market_time,
            "interval_start_time": interval_start_time,
            "interval_end_time": interval_end_time,
            "last": last,
            "prev": prev,
            "high": high,
            "low": low,
            "fifty_two_week_high": fifty_two_week_high,
            "fifty_two_week_low": fifty_two_week_low,
            "change": change,
            "change_percent": change_percent,
            "error": None,
        }

    def _fetch_indices_batch(self) -> Dict[str, Dict[str, Any]]:
        """Fetch all configured symbols in one request to reduce rate-limit pressure."""
        symbols = [m.get("provider_symbol") for m in self.index_mappings if m.get("provider_symbol")]
        if not symbols:
            return {}

        payload = self._request_with_retry(self.QUOTE_URL, {"symbols": ",".join(symbols)})
        rows = payload.get("quoteResponse", {}).get("result", [])
        return {row.get("symbol", ""): row for row in rows if row.get("symbol")}

    def _normalize_quote_row(self, mapping: Dict[str, str], row: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize /quote response row into API schema."""
        last = self._to_float(row.get("regularMarketPrice"))
        prev = self._to_float(row.get("regularMarketPreviousClose"))
        high = self._to_float(row.get("regularMarketDayHigh"))
        low = self._to_float(row.get("regularMarketDayLow"))
        fifty_two_week_high = self._to_float(row.get("fiftyTwoWeekHigh"))
        fifty_two_week_low = self._to_float(row.get("fiftyTwoWeekLow"))
        change = self._to_float(row.get("regularMarketChange"))
        change_percent = self._to_float(row.get("regularMarketChangePercent"))

        if change is None and last is not None and prev is not None:
            change = last - prev

        if change_percent is None and prev not in (None, 0) and last is not None:
            change_percent = ((last - prev) / prev) * 100

        return {
            "symbol": mapping["provider_symbol"],
            "name": mapping["name"],
            "time": self._format_timestamp(row.get("regularMarketTime")),
            "interval_start_time": self._format_timestamp(row.get("regularMarketTime")),
            "interval_end_time": self._format_timestamp(row.get("regularMarketTime")),
            "last": last,
            "prev": prev,
            "high": high,
            "low": low,
            "fifty_two_week_high": fifty_two_week_high,
            "fifty_two_week_low": fifty_two_week_low,
            "change": change,
            "change_percent": change_percent,
            "error": None,
        }

    def _request_chart_payload(self, provider_symbol: str, selected_range: str = "1d") -> Dict[str, Any]:
        """Fetch chart payload with basic retry/backoff for rate limits."""
        chart_interval = self.SUPPORTED_RANGES[selected_range]["chart_interval"]
        return self._request_with_retry(
            self.CHART_URL.format(symbol=provider_symbol),
            {"interval": chart_interval, "range": selected_range},
            context=provider_symbol,
        )

    def _build_interval_metrics(self, chart_result: Dict[str, Any]) -> Dict[str, Any]:
        """Build range-based metrics from chart time series for multi-day/week/month views."""
        timestamps = chart_result.get("timestamp", []) or []
        quote_rows = chart_result.get("indicators", {}).get("quote", [])
        quote = quote_rows[0] if quote_rows else {}

        closes_raw = quote.get("close", []) or []
        highs_raw = quote.get("high", []) or []
        lows_raw = quote.get("low", []) or []

        close_points: List[Tuple[Optional[int], float]] = []
        for idx, close_raw in enumerate(closes_raw):
            close_value = self._to_float(close_raw)
            if close_value is None:
                continue
            timestamp = timestamps[idx] if idx < len(timestamps) else None
            close_points.append((timestamp, close_value))

        if close_points:
            prev = close_points[0][1]
            last = close_points[-1][1]
            first_timestamp = close_points[0][0]
            latest_timestamp = close_points[-1][0]
        else:
            prev = None
            last = None
            first_timestamp = None
            latest_timestamp = None

        high_values = [self._to_float(value) for value in highs_raw]
        high_values = [value for value in high_values if value is not None]
        low_values = [self._to_float(value) for value in lows_raw]
        low_values = [value for value in low_values if value is not None]

        high = max(high_values) if high_values else (max([p[1] for p in close_points]) if close_points else None)
        low = min(low_values) if low_values else (min([p[1] for p in close_points]) if close_points else None)

        change = None
        if last is not None and prev is not None:
            change = last - prev

        change_percent = None
        if change is not None and prev not in (None, 0):
            change_percent = (change / prev) * 100

        return {
            "time": self._format_timestamp(latest_timestamp),
            "interval_start_time": self._format_timestamp(first_timestamp),
            "interval_end_time": self._format_timestamp(latest_timestamp),
            "last": last,
            "prev": prev,
            "high": high,
            "low": low,
            "change": change,
            "change_percent": change_percent,
        }

    def _request_with_retry(
        self, url: str, params: Dict[str, Any], context: str = "batch"
    ) -> Dict[str, Any]:
        """HTTP GET with retry/backoff tuned for occasional 429 responses."""
        last_error: Optional[str] = None
        request_url = self._build_request_url(url, params)

        for attempt in range(self.max_retries + 1):
            logger.warning(
                "Yahoo API request context=%s attempt=%s/%s query=%s",
                context,
                attempt + 1,
                self.max_retries + 1,
                request_url,
            )
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 429:
                retry_after_header = response.headers.get("Retry-After")
                wait_seconds = self.retry_backoff_seconds * (attempt + 1)
                if retry_after_header:
                    try:
                        wait_seconds = max(wait_seconds, float(retry_after_header))
                    except ValueError:
                        pass

                last_error = f"Rate limit (429) for {context}"
                if attempt >= self.max_retries:
                    break

                # Prime Yahoo cookies the same way a browser would before retry.
                try:
                    self.session.get("https://finance.yahoo.com", timeout=self.timeout)
                except requests.RequestException:
                    pass

                time.sleep(wait_seconds)
                continue

            try:
                response.raise_for_status()
            except requests.RequestException as exc:
                last_error = str(exc)
                if attempt >= self.max_retries:
                    break
                time.sleep(self.retry_backoff_seconds * (attempt + 1))
                continue

            return response.json()

        raise ValueError(last_error or f"Failed to fetch market data for {context}")

    def _find_mapping(self, provider_symbol: str, name: Optional[str] = None) -> Dict[str, str]:
        """Find configured mapping by provider symbol, optionally matching name."""
        for mapping in self.index_mappings:
            if mapping.get("provider_symbol") == provider_symbol:
                if not name or mapping.get("name") == name:
                    return mapping

        # Allow ad-hoc retry even if symbol is not found in configuration.
        return {
            "provider_symbol": provider_symbol,
            "name": name or provider_symbol,
        }

    def _build_failed_row(self, mapping: Dict[str, str], message: str) -> Dict[str, Any]:
        """Create a normalized failed row so UI can still render and retry it."""
        return {
            "symbol": mapping.get("provider_symbol", ""),
            "name": mapping.get("name", mapping.get("provider_symbol", "")),
            "time": datetime.now(UTC).isoformat(),
            "interval_start_time": None,
            "interval_end_time": None,
            "last": None,
            "prev": None,
            "high": None,
            "low": None,
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "change": None,
            "change_percent": None,
            "error": message,
        }

    def _update_cached_row(self, row: Dict[str, Any], selected_range: str) -> None:
        """Update in-memory cache row if cache is populated."""
        range_cache = self.__class__._cache_indices_by_range.get(selected_range, [])
        if not range_cache:
            return

        for idx, existing in enumerate(range_cache):
            if existing.get("symbol") == row.get("symbol") and existing.get("name") == row.get("name"):
                range_cache[idx] = row
                break

        self.__class__._cache_indices_by_range[selected_range] = range_cache
        # Keep cache alive after row-level retries.
        self.__class__._cache_until_by_range[selected_range] = time.time() + max(0, self.cache_ttl_seconds)

    def _normalize_range(self, requested_range: Optional[str]) -> str:
        """Validate and normalize requested Yahoo chart range."""
        normalized = (requested_range or "1d").strip().lower()
        if normalized not in self.SUPPORTED_RANGES:
            raise ValueError(
                f"Unsupported range '{requested_range}'. Supported ranges: {', '.join(self.get_supported_ranges())}"
            )
        return normalized

    def _is_cache_valid(self, selected_range: str) -> bool:
        """Check whether cached rows for a range are still valid."""
        cache_until = self.__class__._cache_until_by_range.get(selected_range, 0.0)
        return time.time() < cache_until

    @classmethod
    def get_supported_ranges(cls) -> List[str]:
        """Return supported range keys for Yahoo chart snapshots."""
        return list(cls.SUPPORTED_RANGES.keys())

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _format_timestamp(timestamp: Any) -> str:
        try:
            return datetime.fromtimestamp(int(timestamp), UTC).isoformat()
        except (TypeError, ValueError, OSError):
            return datetime.now(UTC).isoformat()

    @staticmethod
    def _build_request_url(url: str, params: Dict[str, Any]) -> str:
        """Build a fully rendered request URL for debug logging."""
        prepared = requests.Request("GET", url, params=params).prepare()
        return prepared.url or url

    def _extract_interval_bounds(self, chart_result: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Derive interval start/end timestamps from chart payload."""
        timestamps = chart_result.get("timestamp", []) or []
        if not timestamps:
            return None, None

        first = timestamps[0]
        last = timestamps[-1]
        return self._format_timestamp(first), self._format_timestamp(last)
