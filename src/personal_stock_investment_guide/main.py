#!/usr/bin/env python
import warnings
from datetime import datetime

from personal_stock_investment_guide.crew import MoroccoInvestmentGuideCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the Morocco long-term investing guide crew (no user input).
    """
    inputs = {
        "country": "Morocco",
        "horizon_years": "10-15",
        "constraints": "Sharia-aware (exclude banking, insurance, and other haram sectors by business activity)",
        "current_date": str(datetime.now()),
    }

    result = MoroccoInvestmentGuideCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== MOROCCO LONG-TERM INVESTING GUIDE (FINAL) ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()
