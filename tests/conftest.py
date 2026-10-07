from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def docs_dir() -> Path:
    return ROOT / "data" / "docs"


@pytest.fixture(scope="session")
def intents_df() -> pd.DataFrame:
    return pd.read_csv(ROOT / "data" / "intents.csv")
