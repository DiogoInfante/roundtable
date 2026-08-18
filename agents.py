"""Pure agent logic and LangGraph node adapters."""

from typing import Literal

from data import get_price_data, get_volatility_data
from llm import call_llm, call_llm_structured
from schemas import ResearchVerdict, TradeDecision, TradingState

TECH_SYSTEM = (
    "You are a TECHNICAL analyst. From the price/trend data only, give 3-4 concise "
    "signals about trend and momentum, each tied to a number. No buy/sell call."
)
RISK_SYSTEM = (
    "You are a RISK analyst. From the volatility data only, assess how risky/volatile "
    "this stock is right now in 3-4 concise points, each tied to a number. No buy/sell call."
)


def briefing(state: TradingState) -> str:
    """Format technical and risk analyst reports into a single briefing."""
    return (
        f"[Technical analyst]\n{state['report_technical']}\n\n"
        f"[Risk analyst]\n{state['report_risk']}"
    )


def analyst_technical_node(state: TradingState) -> dict:
    """Technical analyst node: fetch price data and generate trend signals."""
    data = get_price_data(state["ticker"])
    return {"report_technical": call_llm(TECH_SYSTEM, f"Price/trend data:\n\n{data}")}


def analyst_risk_node(state: TradingState) -> dict:
    """Risk analyst node: fetch volatility metrics and generate risk points."""
    data = get_volatility_data(state["ticker"])
    return {"report_risk": call_llm(RISK_SYSTEM, f"Volatility data:\n\n{data}")}


def bull_node(state: TradingState) -> dict:
    """Bull researcher node: append a bullish argument to the debate transcript."""
    r = state["round"] + 1
    arg = researcher("bull", briefing(state), state["transcript"])
    return {"transcript": state["transcript"] + f"\n[R{r}] BULL: {arg}"}


def bear_node(state: TradingState) -> dict:
    """Bear researcher node: append a bearish argument and update the round count."""
    r = state["round"] + 1
    arg = researcher("bear", briefing(state), state["transcript"])
    return {
        "transcript": state["transcript"] + f"\n[R{r}] BEAR: {arg}",
        # Increment round counter after bear's turn so a full round includes paired bull and bear turns
        "round": r,
    }


def route_after_debate(state: TradingState) -> Literal["bull", "manager"]:
    """Determine whether to continue the debate loop or route to the research manager."""
    if state["round"] < state["max_rounds"]:
        return "bull"
    return "manager"


def manager_node(state: TradingState) -> dict:
    """Research manager node: evaluate debate and set winning stance and synthesis."""
    verdict = research_manager(briefing(state), state["transcript"])
    return {"lean": verdict.lean, "synthesis": verdict.summary}


def trader_node(state: TradingState) -> dict:
    """Trader node: produce final structured trade decision based on manager synthesis."""
    brief = f"Research lean: {state['lean']}\nSynthesis: {state['synthesis']}"
    return {"decision": trader_decision(brief)}


def researcher(
    stance: Literal["bull", "bear"], analyst_report: str, transcript: str
) -> str:
    """Generate a concise rebuttal for the bull or bear researcher stance."""
    roles = {
        "bull": "You are a BULLISH researcher. Argue the strongest case to BUY.",
        "bear": "You are a BEARISH researcher. Argue the strongest case to SELL or avoid.",
    }

    system = (
        roles[stance]
        + " Use ONLY the analyst report and the debate so far. Rebut the other "
        "side's most recent point SPECIFICALLY. Be concise: 2-4 sentences."
    )

    user = (
        f"Analyst report:\n{analyst_report}\n\n"
        f"Debate so far:\n{transcript or '(nothing yet — you open)'}"
    )

    return call_llm(system, user)


def research_manager(analyst_report: str, transcript: str) -> ResearchVerdict:
    """Evaluate analyst report and debate transcript to output a structured verdict."""
    return call_llm_structured(
        system=(
            "You are the research manager. Read the analyst report and the bull/bear "
            "debate. Weigh the arguments — do NOT just split the difference. Judge which "
            "side made the stronger case. If the debate was inconclusive or data was thin, "
            "lean neutral."
        ),
        user=f"Analyst report:\n{analyst_report}\n\nDebate:\n{transcript}",
        schema=ResearchVerdict,
    )


def trader_decision(report: str) -> TradeDecision:
    """Generate structured BUY/HOLD/SELL trade decision from the research manager brief."""
    return call_llm_structured(
        system=(
            "You are a trading decision-maker. Based ONLY on the analyst report, "
            "decide BUY, HOLD, or SELL. If the report says data was insufficient, choose HOLD."
        ),
        user=f"Analyst report:\n\n{report}",
        schema=TradeDecision,
    )
