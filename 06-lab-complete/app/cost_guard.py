"""Budget protection — track daily spending per instance."""
import time

from fastapi import HTTPException

from app.config import settings

_daily_cost: float = 0.0
_cost_reset_day: str = time.strftime("%Y-%m-%d")


def check_and_record_cost(input_tokens: int, output_tokens: int) -> None:
    """
    Track estimated cost and enforce daily budget.
    Raises 402 Payment Required if daily budget is exceeded.

    Pricing estimate (GPT-4o-mini):
      - Input:  $0.15  / 1M tokens
      - Output: $0.60  / 1M tokens
    """
    global _daily_cost, _cost_reset_day

    today = time.strftime("%Y-%m-%d")
    if today != _cost_reset_day:
        _daily_cost = 0.0
        _cost_reset_day = today

    if _daily_cost >= settings.daily_budget_usd:
        raise HTTPException(
            status_code=402,
            detail="Daily budget exhausted. Try again tomorrow.",
        )

    cost = (input_tokens / 1_000_000) * 0.15 + (output_tokens / 1_000_000) * 0.60
    _daily_cost += cost


def get_daily_cost() -> float:
    """Return current daily accumulated cost."""
    return _daily_cost
