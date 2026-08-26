from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from healthcentre_analytics.reporting import generate_monthly_report


def main() -> None:
    path = generate_monthly_report()
    print(f"Monthly management report generated: {path}")


if __name__ == "__main__":
    main()
