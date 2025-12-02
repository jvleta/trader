import sys
import types
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

if "openbb" not in sys.modules:
    stub_module = types.ModuleType("openbb")
    stub_module.obb = types.SimpleNamespace()
    sys.modules["openbb"] = stub_module

import trader


def test_parse_dividend_amounts_supports_multiple_shapes():
    df = pd.DataFrame([{"amount": 1.25}, {"cash_amount": "2.75"}])
    assert trader._parse_dividend_amounts({"data": df}) == [1.25, 2.75]
    mixed = df.to_dict(orient="records") + [None]
    assert trader._parse_dividend_amounts(mixed) == [1.25, 2.75]


def test_parse_dividend_amounts_rejects_non_numeric():
    with pytest.raises(ValueError):
        trader._parse_dividend_amounts([{"amount": "abc"}])


def test_parse_dividend_amounts_handles_plain_dict_and_fallback():
    class BrokenToDict:
        def to_dict(self, orient=None):
            if orient is not None:
                raise ValueError("boom")
            return {"amount": 2}

    assert trader._parse_dividend_amounts({"amount": 3}) == [3.0]
    assert trader._parse_dividend_amounts(BrokenToDict()) == [2.0]


def test_get_spot_price_uses_latest_close(monkeypatch):
    quote_response = types.SimpleNamespace(
        data=[types.SimpleNamespace(close=np.float64(101.5))]
    )
    price = types.SimpleNamespace(quote=lambda symbol: quote_response)
    equity = types.SimpleNamespace(price=price)
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(equity=equity))

    assert trader.get_spot_price("XYZ") == pytest.approx(101.5)


def test_get_dividend_yield_aggregates_amounts(monkeypatch):
    dividends_data = [{"amount": 1.0}, {"dividend": 0.5}]
    fundamental = types.SimpleNamespace(
        dividends=lambda symbol, start_date, end_date: types.SimpleNamespace(
            data=dividends_data
        )
    )
    equity = types.SimpleNamespace(fundamental=fundamental, price=types.SimpleNamespace())
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(equity=equity))
    monkeypatch.setattr(trader, "get_spot_price", lambda symbol: 100.0)

    assert trader.get_dividend_yield("XYZ") == pytest.approx(0.015)


def test_get_dividend_yield_raises_on_missing_data(monkeypatch):
    fundamental = types.SimpleNamespace(
        dividends=lambda symbol, start_date, end_date: types.SimpleNamespace(data=[])
    )
    equity = types.SimpleNamespace(fundamental=fundamental, price=types.SimpleNamespace())
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(equity=equity))
    monkeypatch.setattr(trader, "get_spot_price", lambda symbol: 50.0)

    with pytest.raises(RuntimeError):
        trader.get_dividend_yield("XYZ")


def test_get_risk_free_rate_prefers_recent(monkeypatch):
    rates = [
        {"year_10": None},
        {"year_10": "0.95"},
        {"year_10": 4.5},
    ]
    government = types.SimpleNamespace(
        treasury_rates=lambda start_date, end_date: types.SimpleNamespace(data=rates)
    )
    fixedincome = types.SimpleNamespace(government=government)
    monkeypatch.setattr(
        trader, "obb", types.SimpleNamespace(fixedincome=fixedincome)
    )

    assert trader.get_risk_free_rate() == pytest.approx(0.045)


def test_get_risk_free_rate_skips_none_entries(monkeypatch):
    rates = [None, {"year_10": 0.5}]
    government = types.SimpleNamespace(
        treasury_rates=lambda start_date, end_date: types.SimpleNamespace(data=rates)
    )
    fixedincome = types.SimpleNamespace(government=government)
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(fixedincome=fixedincome))

    assert trader.get_risk_free_rate() == pytest.approx(0.5)


def test_get_risk_free_rate_wraps_provider_errors(monkeypatch):
    def broken_rates(start_date, end_date):
        raise RuntimeError("network failure")

    government = types.SimpleNamespace(treasury_rates=broken_rates)
    fixedincome = types.SimpleNamespace(government=government)
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(fixedincome=fixedincome))

    with pytest.raises(RuntimeError):
        trader.get_risk_free_rate()


def test_fetch_underlying_data_combines_fields(monkeypatch):
    monkeypatch.setattr(trader, "get_spot_price", lambda symbol: 10.0)
    monkeypatch.setattr(trader, "get_dividend_yield", lambda symbol: 0.02)
    monkeypatch.setattr(trader, "get_risk_free_rate", lambda: 0.03)

    assert trader.fetch_underlying_data("XYZ") == {
        "symbol": "XYZ",
        "spot_price": 10.0,
        "dividend_yield": 0.02,
        "risk_free_rate": 0.03,
    }


def test_fetch_option_chain_filters_and_normalizes(monkeypatch):
    chain_df = pd.DataFrame(
        [
            {
                "option_type": "call",
                "expiration": date(2024, 12, 20),
                "strike": 100.0,
                "dte": 30,
                "last_trade_price": 5.5,
                "bid": 5.0,
                "ask": 6.0,
                "volume": 10,
                "open_interest": 5,
                "implied_volatility": 0.25,
            },
            {
                "option_type": "put",
                "expiration": date(2024, 11, 15),
                "strike": 90.0,
                "dte": 10,
                "close": 2.0,
                "bid": 1.9,
                "ask": 2.1,
                "volume": 20,
                "open_interest": 15,
                "implied_volatility": 0.2,
            },
        ]
    )

    class ChainResponse:
        def to_dataframe(self, index=None):
            return chain_df

    options = types.SimpleNamespace(chains=lambda symbol: ChainResponse())
    derivatives = types.SimpleNamespace(options=options)
    monkeypatch.setattr(
        trader, "obb", types.SimpleNamespace(derivatives=derivatives)
    )

    df = trader.fetch_option_chain("XYZ", filter_expiries=[date(2024, 12, 20)])

    assert len(df) == 1
    row = df.iloc[0]
    assert row["symbol"] == "XYZ"
    assert row["expiration"] == date(2024, 12, 20)
    assert row["market_price"] == pytest.approx(5.5)
    assert row["implied_vol"] == pytest.approx(0.25)
    assert row["T_years"] == pytest.approx(30 / 365.0)


def test_fetch_option_chain_returns_empty_after_filter(monkeypatch):
    chain_df = pd.DataFrame(
        [
            {"option_type": "call", "expiration": date(2024, 12, 20), "strike": 100.0, "bid": 1, "ask": 1.2},
        ]
    )

    class ChainResponse:
        def to_dataframe(self, index=None):
            return chain_df

    options = types.SimpleNamespace(chains=lambda symbol: ChainResponse())
    derivatives = types.SimpleNamespace(options=options)
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(derivatives=derivatives))

    df = trader.fetch_option_chain("XYZ", filter_expiries=[date(2024, 11, 1)])
    assert df.empty


def test_fetch_option_chain_sets_nan_market_price_when_missing(monkeypatch):
    future_date = date.today() + pd.Timedelta(days=30)
    chain_df = pd.DataFrame(
        [
            {
                "option_type": "call",
                "expiration": future_date,
                "strike": 100.0,
                "bid": 1.0,
                "ask": 1.4,
                "volume": 0,
                "open_interest": 0,
                "implied_volatility": 0.3,
            },
        ]
    )

    class ChainResponse:
        def to_dataframe(self, index=None):
            return chain_df

    options = types.SimpleNamespace(chains=lambda symbol: ChainResponse())
    derivatives = types.SimpleNamespace(options=options)
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(derivatives=derivatives))

    df = trader.fetch_option_chain("XYZ")
    assert pd.isna(df.loc[0, "market_price"])
    t_years_value = df.loc[0, "T_years"]
    assert isinstance(t_years_value, (int, float, np.number))
    assert float(t_years_value) > 0


def test_get_spot_price_errors_on_missing_price(monkeypatch):
    quote_response = types.SimpleNamespace(data=[types.SimpleNamespace(open=100.0)])
    equity = types.SimpleNamespace(price=types.SimpleNamespace(quote=lambda symbol: quote_response))
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(equity=equity))

    with pytest.raises(RuntimeError):
        trader.get_spot_price("MISSING")


def test_get_spot_price_wraps_provider_errors(monkeypatch):
    def bad_quote(symbol):
        raise RuntimeError("provider down")

    equity = types.SimpleNamespace(price=types.SimpleNamespace(quote=bad_quote))
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(equity=equity))

    with pytest.raises(RuntimeError):
        trader.get_spot_price("XYZ")


def test_get_risk_free_rate_raises_on_invalid(monkeypatch):
    rates = [
        {"year_10": None},
        {"year10": "not-a-number"},
        {"ten_year": None},
    ]
    government = types.SimpleNamespace(
        treasury_rates=lambda start_date, end_date: types.SimpleNamespace(data=rates)
    )
    fixedincome = types.SimpleNamespace(government=government)
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(fixedincome=fixedincome))

    with pytest.raises(RuntimeError):
        trader.get_risk_free_rate()


def test_fetch_option_chain_returns_empty_when_no_data(monkeypatch):
    class EmptyChainResponse:
        def to_dataframe(self, index=None):
            return pd.DataFrame()

    options = types.SimpleNamespace(chains=lambda symbol: EmptyChainResponse())
    derivatives = types.SimpleNamespace(options=options)
    monkeypatch.setattr(trader, "obb", types.SimpleNamespace(derivatives=derivatives))

    df = trader.fetch_option_chain("XYZ")
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_compute_metrics_filters_and_computes(monkeypatch):
    future_date = pd.Timestamp.today() + pd.Timedelta(days=30)
    df = pd.DataFrame(
        [
            {
                "option_type": "call",
                "expiration": future_date,
                "strike": 105.0,
                "bid": 2.0,
                "ask": 2.4,
            },
            {
                "option_type": "call",
                "expiration": future_date,
                "strike": 95.0,
                "bid": -1.0,
                "ask": 0.0,
            },
            {
                "option_type": "put",
                "expiration": future_date,
                "strike": 110.0,
                "bid": 3.0,
                "ask": 3.5,
            },
        ]
    )

    metrics = trader.compute_metrics(df, S=100.0)

    assert len(metrics) == 1  # removes puts, non-positive premiums, strikes below S
    row = metrics.iloc[0]
    assert row["premium"] == pytest.approx(2.2)
    assert row["pct_otm"] == pytest.approx(5.0)
    assert row["breakeven"] == pytest.approx(97.8)
    assert row["annualized_yield"] > 0


def test_screen_prints_summary(monkeypatch, capsys):
    monkeypatch.setattr(
        trader,
        "fetch_underlying_data",
        lambda symbol: {"symbol": symbol, "spot_price": 100.0, "dividend_yield": 0.01, "risk_free_rate": 0.02},
    )
    monkeypatch.setattr(trader, "fetch_option_chain", lambda symbol: pd.DataFrame())

    screen_df = pd.DataFrame(
        [
            {
                "expiration": date.today() + pd.Timedelta(days=14),
                "strike": 105.0,
                "premium": 2.0,
                "dte": 14,
                "pct_otm": 5.0,
                "breakeven": 98.0,
                "annualized_yield": 0.52,
            }
        ]
    )
    monkeypatch.setattr(trader, "compute_metrics", lambda df, S: screen_df)

    trader.screen("AAA")
    output = capsys.readouterr().out
    assert "COVERED CALL SCREEN FOR AAA" in output
    assert "Done." in output
