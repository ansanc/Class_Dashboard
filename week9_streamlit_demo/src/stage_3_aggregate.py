from loguru import logger


def aggregate_previous_applications(df_prev, config):
    """Aggregate features from previous applications using method chaining."""
    logger.info("Aggregating previous applications data...")
    a_cfg = config['agg']

    recent_apps = (df_prev
        .query(f"DAYS_DECISION >= {a_cfg['recent_days_threshold']}")
        .groupby('SK_ID_CURR')
        .size()
        .reset_index(name='recent_prev_app_count')
    )

    refused_apps = (df_prev
        .query(f"NAME_CONTRACT_STATUS == '{a_cfg['refused_status']}'")
        .groupby('SK_ID_CURR')
        .size()
        .reset_index(name='refused_count')
    )

    return (recent_apps
        .merge(refused_apps, on='SK_ID_CURR', how='outer')
        .fillna(0)
    )


def aggregate_bureau(df_bureau, config):
    """Aggregate external debt features from the bureau dataset."""
    logger.info("Aggregating bureau data...")
    return (df_bureau
        .groupby("SK_ID_CURR")
        .agg(
            bureau_loan_count=("SK_ID_BUREAU", "size"),
            total_bureau_debt=("AMT_CREDIT_SUM_DEBT", "sum")
        )
        .reset_index()
    )

def create_cubes(df_final):
    """Aggregate the final dataset into data cubes for analysis."""
    logger.info("Creating data cubes from the final dataset...")
    return (df_final
            .groupby(['MONTH_APPLIED', 'YEAR_APPLIED', 'NAME_CONTRACT_TYPE', 'AGE_GROUP', 'CREDIT_INCOME_RATIO_GROUP', 'YEARS_EMPLOYED_GROUP',
                       'AGE_GENDER_SEGMENT', 'HOME_CAR_OWNERSHIP', 'BURDEN_CAT']) 
            .agg(
                total_applications=('SK_ID_CURR', 'count'),
                total_defaults=('TARGET', 'sum'),
                total_credit=('AMT_CREDIT', 'sum'),
                total_recent_prev_apps=('recent_prev_app_count', 'sum'),
                total_refused_prev_apps=('refused_count', 'sum'),
                total_bureau_loans=('bureau_loan_count', 'sum'),
                total_bureau_debt=('total_bureau_debt', 'sum')
            )
            .reset_index()
    )
    