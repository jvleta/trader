# llm.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pandas as pd
from openai import OpenAI


@dataclass
class LLMConfig:
    """
    Runtime config for LLM calls.
    You can expose these as CLI flags or config.yaml fields later.
    """

    model: str = "gpt-4.1-mini"
    max_output_tokens: int = 800
    temperature: float = 0.3


_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """
    Lazily initialize the OpenAI client.
    Requires OPENAI_API_KEY in the environment.
    """
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _format_candidates_for_prompt(
    candidates: pd.DataFrame,
    max_rows: int = 20,
) -> str:
    """
    Turn the candidate DataFrame into a compact JSON-like text block.
    Only include the most relevant columns.
    """
    if candidates.empty:
        return "[]"

    display_cols = [
        "symbol",
        "underlying_price",
        "strike",
        "dte",
        "premium",
        "premium_yield_pct",
        "moneyness_pct",
        "iv",
        "hv_20",
        "volume",
        "open_interest",
        "earnings_in_days",
    ]

    cols = [c for c in display_cols if c in candidates.columns]
    df = candidates[cols].head(max_rows).copy()

    # Replace NaNs with None to avoid weird prompt artifacts
    df = df.fillna(value=pd.NA)

    records = df.to_dict(orient="records")
    return repr(records)  # simple Python-literal style string


def _build_prompt(
    candidates_block: str,
    risk_profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create the user-facing prompt for the LLM.
    """
    profile_text = ""
    if risk_profile:
        profile_text = (
            "Here is the covered call writer's risk profile as JSON:\n"
            f"{risk_profile}\n\n"
            "Respect this profile when ranking and commenting.\n"
        )

    return f"""
You are an options trading assistant that helps screen covered call candidates.

{profile_text}
Here is a list of candidate covered calls as a JSON-like list of dicts.
Each dict may contain some of these keys:
- symbol: stock ticker
- underlying_price: current stock price
- strike: option strike
- dte: days to expiration
- premium: option premium in dollars
- premium_yield_pct: premium / underlying_price * 100
- moneyness_pct: (strike / underlying_price - 1) * 100
- iv: implied volatility
- hv_20: 20-day historical volatility
- volume, open_interest: option liquidity
- earnings_in_days: days until earnings (None if unknown)

Candidates:
{candidates_block}

Your tasks:
1. Rank the candidates from most attractive to least attractive for a covered call writer.
2. For each candidate, output:
   - symbol
   - a 1–2 sentence explanation that comments on:
     * income vs downside risk
     * volatility / event risk (earnings, very high IV)
     * liquidity concerns if any
   - a label in {{ "Conservative", "Moderate", "Aggressive", "Avoid" }}.
3. If none of the candidates fit a conservative profile, say so explicitly.

Return your answer as **markdown**, with a table of ranked candidates followed
by bullet-point commentary.
    """.strip()


def explain_candidates(
    candidates: pd.DataFrame,
    risk_profile: Optional[Dict[str, Any]] = None,
    cfg: Optional[LLMConfig] = None,
) -> str:
    """
    Main entry point.

    - Takes a DataFrame of covered-call candidates.
    - Returns a markdown-formatted explanation string from the LLM.
    """
    if cfg is None:
        cfg = LLMConfig()

    if candidates.empty:
        return "No candidates were generated today, so there is nothing to analyze."

    candidates_block = _format_candidates_for_prompt(candidates)
    prompt = _build_prompt(candidates_block, risk_profile)

    client = _get_client()
    response = client.responses.create(
        model=cfg.model,
        input=prompt,
        max_output_tokens=cfg.max_output_tokens,
        temperature=cfg.temperature,
    )

    # The Python SDK exposes a convenience property for text output
    # so you don't have to walk the 'output' array manually.
    # See: https://platform.openai.com/docs/overview?lang=python
    return response.output_text  # type: ignore[attr-defined]
