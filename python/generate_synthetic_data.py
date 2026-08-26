from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from healthcentre_analytics.data_generation import generate_all, save_generated_data


def main() -> None:
    save_generated_data(generate_all())
    print("Synthetic raw datasets generated in data/raw.")


if __name__ == "__main__":
    main()
