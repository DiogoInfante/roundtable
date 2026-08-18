"""LangGraph workflow construction and compiled graph instance."""

from langgraph.graph import END, START, StateGraph

from agents import (
    analyst_risk_node,
    analyst_technical_node,
    bear_node,
    bull_node,
    manager_node,
    route_after_debate,
    trader_node,
)
from schemas import TradingState


def build_graph():
    """Construct and compile the multi-agent trading analysis workflow graph."""
    builder = StateGraph(TradingState)
    builder.add_node("analyst_technical", analyst_technical_node)
    builder.add_node("analyst_risk", analyst_risk_node)
    builder.add_node("bull", bull_node)
    builder.add_node("bear", bear_node)
    builder.add_node("manager", manager_node)
    builder.add_node("trader", trader_node)

    builder.add_edge(START, "analyst_technical")
    builder.add_edge(START, "analyst_risk")
    builder.add_edge("analyst_technical", "bull")
    builder.add_edge("analyst_risk", "bull")
    builder.add_edge("bull", "bear")
    builder.add_conditional_edges("bear", route_after_debate, ["bull", "manager"])
    builder.add_edge("manager", "trader")
    builder.add_edge("trader", END)
    return builder.compile()


# Build once at module import so `graph` serves as the reusable application singleton
graph = build_graph()