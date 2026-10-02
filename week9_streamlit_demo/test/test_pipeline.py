import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def test_output_matches_baseline():
    result = pd.read_csv(DATA_DIR / 'processed_application_data_exercise.csv')

    baseline = pd.read_csv(DATA_DIR / 'reconciliation_baseline.csv')

    # Check same columns
    assert set(result.columns) == set(baseline.columns)

    # Reorder result to match baseline
    result = result[baseline.columns]

    # Check same data
    assert result.equals(baseline)

    

