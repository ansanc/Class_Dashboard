# --- Configuration ---
import numpy as np
from pathlib import Path


CONFIG = {
    'paths': {
        'repo_root': Path(__file__).resolve().parent.parent,
        'output_dir': 'data',
        'log_dir': 'logs',
        'db_path': 'data/home_credit.db',
        'output_file': 'processed_application_data.csv',
        'cube_file': 'processed_data_cube.csv',
        'log_file': 'pipeline.log'
    },
    'queries': {
        'application': f"""
        SELECT 
            SK_ID_CURR, TARGET, NAME_CONTRACT_TYPE,CODE_GENDER, FLAG_OWN_CAR,
            FLAG_OWN_REALTY, CNT_CHILDREN, AMT_INCOME_TOTAL, AMT_CREDIT, AMT_ANNUITY,
            AMT_GOODS_PRICE, NAME_INCOME_TYPE, NAME_EDUCATION_TYPE, NAME_FAMILY_STATUS,
            NAME_HOUSING_TYPE, DAYS_BIRTH, DAYS_EMPLOYED, DAYS_REGISTRATION, DAYS_ID_PUBLISH,
            OWN_CAR_AGE, OCCUPATION_TYPE, CNT_FAM_MEMBERS, date_application 
        FROM application
        """,

        'previous_application': f"""
        SELECT
            SK_ID_CURR, SK_ID_PREV, DAYS_DECISION, NAME_CONTRACT_TYPE, NAME_CONTRACT_STATUS,
            CHANNEL_TYPE, AMT_CREDIT, AMT_GOODS_PRICE, CNT_PAYMENT 
        FROM previous_application
        """,

        'bureau': f"""
        SELECT * 
        FROM bureau
        """
    },
    'clean': {
        'income_outlier_max': 10000000,
        'days_employed_anomaly': 365243
    },
    'transform': {
        'education_mapping': {
            'Lower secondary': 'Lower Education',
            'Secondary / secondary special': 'Lower Education',
            'Higher education': 'Higher Education',
            'Academic degree': 'Higher Education'
        },
        'education_default': 'Lower Education',
        'income_bins': [0, 100000, 150000, 200000, np.inf],
        'income_labels': ['Low Income', 'Medium Income', 'High Income', 'Very High Income'],
        'age_bins': [0, 25, 35, 45, 55, np.inf],
        'age_labels': ['0-25', '26-35', '36-45', '46-55', '56+'],
        'ratio_bins': [0, 1, 3, 5, np.inf],
        'ratio_labels': ['<1x', '1x-3x', '3x-5x', '>5x'],
        'emp_bins': [0, 2, 5, 10, np.inf],
        'emp_labels': ['0-2 years', '2-5 years', '5-10 years', '10+ years'],
        'age_gender_conditions_labels': ['Young Male', 'Young Female', 'Middle-aged', 'Senior'],
        'ownership_labels': ['Home and Car Owners', 'Home Owners', 'Car Owners', 'No Home or Car'],
        'debt_ratio_bins': [-np.inf, 0, 1, np.inf],
        'debt_ratio_labels': ['No Debt', 'Low Burden', 'High Burden']
    },
    'agg': {
        'recent_days_threshold': -180,
        'refused_status': 'Refused'
    }
}