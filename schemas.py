"""Pydantic output schemas and LangGraph state dictionary."""

from typing import Literal, TypedDict

from pydantic import BaseModel


class ResearchVerdict(BaseModel):
    """Structured verdict emitted by the research manager evaluating the debate."""

    lean: Literal["bullish", "bearish", "neutral"]
    summary: str


class TradeDecision(BaseModel):
    """Structured final decision emitted by the trader node."""

    action: Literal["BUY", "HOLD", "SELL"]
    confidence: Literal["low", "medium", "high"]
    rationale: str


class TradingState(TypedDict):
    """Shared state dictionary passed across all LangGraph nodes in the pipeline."""

    ticker: str
    report_technical: str
    report_risk: str
    round: int
    max_rounds: int
    transcript: str
    lean: str
    synthesis: str
    decision: TradeDecision
