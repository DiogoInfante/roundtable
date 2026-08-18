"""Terminal interface and execution entry point."""

import argparse

from graph import graph


def run_analysis(ticker: str, rounds: int) -> dict:
    """Invoke the trading analysis graph for a ticker and return the final state."""
    # Seed read-before-write state fields so nodes can append to transcript and increment round counter
    return graph.invoke({
        "ticker": ticker,
        "transcript": "",
        "round": 0,
        "max_rounds": rounds,
    })


def main() -> None:
    """Parse command-line arguments and display the analysis output."""
    parser = argparse.ArgumentParser(
        description="Run a multi-agent trading analysis on a stock ticker.",
    )
    parser.add_argument("ticker", help="Ticker to analyze, e.g. AAPL or PETR4.SA")
    parser.add_argument(
        "--rounds",
        type=int,
        default=2,
        help="Number of bull/bear debate rounds (default: 2)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print the full debate transcript",
    )
    args = parser.parse_args()

    print(f"Analyzing {args.ticker} ({args.rounds} rounds)...\n")
    result = run_analysis(args.ticker, args.rounds)

    print("--- technical ---")
    print(result["report_technical"])
    print("\n--- risk ---")
    print(result["report_risk"])

    if args.verbose:
        print("\n--- debate ---")
        print(result["transcript"])

    print(f"\n--- manager: {result['lean']} ---")
    print(result["synthesis"])
    d = result["decision"]
    print(f"\n=== {d.action} ({d.confidence}) ===")
    print(d.rationale)


if __name__ == "__main__":
    main()