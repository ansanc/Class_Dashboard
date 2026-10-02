import numpy as np
from loguru import logger
import pandas as pd


def clean_application_data(df, config):
    """Clean anomalies and outliers using method chaining."""
    logger.info("Cleaning data...")
    c_cfg = config['clean']

    return (df
        .assign(
            AMT_INCOME_TOTAL=lambda x: x['AMT_INCOME_TOTAL'].mask(
                x['AMT_INCOME_TOTAL'] > c_cfg['income_outlier_max'], np.nan
            ),
            DAYS_EMPLOYED=lambda x: x['DAYS_EMPLOYED'].replace(
                c_cfg['days_employed_anomaly'], np.nan
            )
        )
    )


def transform_application_data(df, config):
    """Create new derived features and categorizations using method chaining."""
    logger.info("Transforming application data...")
    t_cfg = config['transform']

    return (df
        .assign(
            # 1. Education Level Mapping
            EDUCATION_LEVEL=lambda x: x['NAME_EDUCATION_TYPE']
                .map(t_cfg['education_mapping'])
                .fillna(t_cfg['education_default']),

            # 2. Income Group Categorization
            INCOME_GROUP=lambda x: pd.cut(
                x['AMT_INCOME_TOTAL'], bins=t_cfg['income_bins'], labels=t_cfg['income_labels']
            ),

            # 3. Age Calculation
            AGE=lambda x: (-x['DAYS_BIRTH'] / 365).astype(int),

            # 6. Credit to Income Ratio Calculation
            CREDIT_INCOME_RATIO=lambda x: x['AMT_CREDIT'] / x['AMT_INCOME_TOTAL'],

            # 7. Years Employed Calculation
            YEARS_EMPLOYED=lambda x: -x['DAYS_EMPLOYED'] / 365
        )
        .assign(
            # Age Group depends on AGE
            AGE_GROUP=lambda x: pd.cut(
                x['AGE'], bins=t_cfg['age_bins'], labels=t_cfg['age_labels']
            ),

            # 6b. Credit to Income Ratio Group
            CREDIT_INCOME_RATIO_GROUP=lambda x: pd.cut(
                x['CREDIT_INCOME_RATIO'], bins=t_cfg['ratio_bins'], labels=t_cfg['ratio_labels']
            ),

            # 7b. Employment Stability Group
            YEARS_EMPLOYED_GROUP=lambda x: pd.cut(
                x['YEARS_EMPLOYED'], bins=t_cfg['emp_bins'], labels=t_cfg['emp_labels']
            )
        )
        .assign(
            # 4. Age-Gender Segmentation (depends on AGE_GROUP)
            AGE_GENDER_SEGMENT=lambda x: np.select(
                [
                    ((x['AGE_GROUP'].isin(['0-25', '26-35'])) & (x['CODE_GENDER'] == 'M')),
                    ((x['AGE_GROUP'].isin(['0-25', '26-35'])) & (x['CODE_GENDER'] == 'F')),
                    (x['AGE_GROUP'].isin(['36-45', '46-55'])),
                    (x['AGE_GROUP'].isin(['56+']))
                ],
                t_cfg['age_gender_conditions_labels'],
                default='Unknown'
            ),

            # 5. Home and Car Ownership
            HOME_CAR_OWNERSHIP=lambda x: np.select(
                [
                    ((x['FLAG_OWN_REALTY'] == 'Y') & (x['FLAG_OWN_CAR'] == 'Y')),
                    ((x['FLAG_OWN_REALTY'] == 'Y') & (x['FLAG_OWN_CAR'] == 'N')),
                    ((x['FLAG_OWN_REALTY'] == 'N') & (x['FLAG_OWN_CAR'] == 'Y')),
                    ((x['FLAG_OWN_REALTY'] == 'N') & (x['FLAG_OWN_CAR'] == 'N'))
                ],
                t_cfg['ownership_labels'],
                default='Unknown'
            ),

            # month of application
            MONTH_APPLIED=lambda x: pd.to_datetime(x['date_application']).dt.month,

            # year of application
            YEAR_APPLIED=lambda x: pd.to_datetime(x['date_application']).dt.year
        )
    )


def transform_post_merge(df, config):
    """Apply transformations that depend on merged datasets."""
    logger.info("Transforming post-merge data...")
    t_cfg = config['transform']
    return (df
        .assign(
            DEBT_INCOME_RATIO=lambda x: x["total_bureau_debt"] / x["AMT_INCOME_TOTAL"]
        )
        .assign(
            BURDEN_CAT=lambda x: pd.cut(
                x["DEBT_INCOME_RATIO"],
                bins=t_cfg['debt_ratio_bins'],
                labels=t_cfg['debt_ratio_labels']
            )
        )
    )