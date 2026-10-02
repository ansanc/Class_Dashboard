import pandas as pd
from loguru import logger

EXPECTED_COLS = [
    'SK_ID_CURR', 'AMT_INCOME_TOTAL', 'DAYS_EMPLOYED',
    'EDUCATION_LEVEL', 'INCOME_GROUP', 'AGE', 'AGE_GROUP', 'AGE_GENDER_SEGMENT',
    'HOME_CAR_OWNERSHIP', 'CREDIT_INCOME_RATIO', 'CREDIT_INCOME_RATIO_GROUP',
    'YEARS_EMPLOYED', 'YEARS_EMPLOYED_GROUP', 'recent_prev_app_count',
    'refused_count', 'bureau_loan_count', 'total_bureau_debt',
    'DEBT_INCOME_RATIO', 'BURDEN_CAT',
]
FILLED_COLS = ['recent_prev_app_count', 'refused_count',
               'bureau_loan_count', 'total_bureau_debt']


class DataValidationError(Exception):
    pass


def validate_final_table(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Validate the final table; raise if any check fails. Returns df for .pipe()."""
    logger.info("Validating final table...")
    errors = []

    # 1. Not empty
    if df.empty:
        raise DataValidationError("Final dataset is empty")

    # 2. Required columns present (stop here if not; later checks depend on them)
    missing = [c for c in EXPECTED_COLS if c not in df.columns]
    if missing:
        raise DataValidationError(f"Missing expected columns: {missing}")

    # 3. One row per applicant (catches join fan-out)
    n_dupes = df['SK_ID_CURR'].duplicated().sum()
    if n_dupes:
        errors.append(f"{n_dupes} duplicate SK_ID_CURR rows after merge")

    # 4. Cleaning worked
    income_max = config['clean']['income_outlier_max']
    if df['AMT_INCOME_TOTAL'].gt(income_max).any():
        errors.append(f"AMT_INCOME_TOTAL has values above {income_max}")

    anomaly = config['clean']['days_employed_anomaly']
    if df['DAYS_EMPLOYED'].eq(anomaly).any():
        errors.append(f"DAYS_EMPLOYED still contains anomaly value {anomaly}")

    # 5. Post-merge fills worked
    for col in FILLED_COLS:
        n_null = df[col].isna().sum()
        if n_null:
            errors.append(f"{col} has {n_null} NaN values after fill")

    if errors:
        for e in errors:
            logger.error(f"Validation failed: {e}")
        raise DataValidationError(f"{len(errors)} validation check(s) failed")

    logger.info(f"Validation passed ({len(df):,} rows)")
    return df