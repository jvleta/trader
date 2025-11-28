import sys
import types
from datetime import date

import numpy as np
import pandas as pd
import pytest

if "openbb" not in sys.modules:
    stub_module = types.ModuleType("openbb")
    stub_module.obb = types.SimpleNamespace()
    sys.modules["openbb"] = stub_module

import openbb_wrapper


def test_parse_dividend_amounts_supports_multiple_shapes():
    df = pd.DataFrame([{"amount": 1.25}, {"cash_amount": "2.75"}])
    assert openbb_wrapper._parse_dividend_amounts({"data": df}) == [1.25, 2.75]
    mixed = df.to_dict(orient="records") + [None]
    assert openbb_wrapper._parse_dividend_amounts(mixed) == [1.25, 2.75]


def test_parse_dividend_amounts_rejects_non_numeric():
    with pytest.raises(ValueError):
        openbb_wrapper._parse_dividend_amounts([{"amount": "abc"}])


def test_get_spot_price_uses_latest_close(monkeypatch):
    quote_response = types.SimpleNamespace(
        data=[types.SimpleNamespace(close=np.float64(101.5))]
    )
    price = types.SimpleNamespace(quote=lambda symbol: quote_response)
    equity = types.SimpleNamespace(price=price)
    monkeypatch.setattr(openbb_wrapper, "obb", types.SimpleNamespace(equity=equity))

    assert openbb_wrapper.get_spot_price("XYZ") == pytest.approx(101.5)


def test_get_dividend_yield_aggregates_amounts(monkeypatch):
    dividends_data = [{"amount": 1.0}, {"dividend": 0.5}]
    fundamental = types.SimpleNamespace(
        dividends=lambda symbol, start_date, end_date: types.SimpleNamespace(
            data=dividends_data
        )
    )
    equity = types.SimpleNamespace(fundamental=fundamental, price=types.SimpleNamespace())
    monkeypatch.setattr(openbb_wrapper, "obb", types.SimpleNamespace(equity=equity))
    monkeypatch.setattr(openbb_wrapper, "get_spot_price", lambda symbol: 100.0)

    assert openbb_wrapper.get_dividend_yield("XYZ") == pytest.approx(0.015)


def test_get_dividend_yield_raises_on_missing_data(monkeypatch):
    fundamental = types.SimpleNamespace(
        dividends=lambda symbol, start_date, end_date: types.SimpleNamespace(data=[])
    )
    equity = types.SimpleNamespace(fundamental=fundamental, price=types.SimpleNamespace())
    monkeypatch.setattr(openbb_wrapper, "obb", types.SimpleNamespace(equity=equity))
    monkeypatch.setattr(openbb_wrapper, "get_spot_price", lambda symbol: 50.0)

    with pytest.raises(RuntimeError):
        openbb_wrapper.get_dividend_yield("XYZ")


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
        openbb_wrapper, "obb", types.SimpleNamespace(fixedincome=fixedincome)
    )

    assert openbb_wrapper.get_risk_free_rate() == pytest.approx(0.045)


def test_fetch_underlying_data_combines_fields(monkeypatch):
    monkeypatch.setattr(openbb_wrapper, "get_spot_price", lambda symbol: 10.0)
    monkeypatch.setattr(openbb_wrapper, "get_dividend_yield", lambda symbol: 0.02)
    monkeypatch.setattr(openbb_wrapper, "get_risk_free_rate", lambda: 0.03)

    assert openbb_wrapper.fetch_underlying_data("XYZ") == {
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
        openbb_wrapper, "obb", types.SimpleNamespace(derivatives=derivatives)
    )

    df = openbb_wrapper.fetch_option_chain("XYZ", filter_expiries=[date(2024, 12, 20)])

    assert len(df) == 1
    row = df.iloc[0]
    assert row["symbol"] == "XYZ"
    assert row["expiration"] == date(2024, 12, 20)
    assert row["market_price"] == pytest.approx(5.5)
    assert row["implied_vol"] == pytest.approx(0.25)
    assert row["T_years"] == pytest.approx(30 / 365.0)
