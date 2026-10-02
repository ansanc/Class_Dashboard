import pandas as pd
import sqlite3
from loguru import logger
from pathlib import Path


def to_numeric_if_possible(df):
    """Dynamically coerce numeric-like string columns to proper numeric types."""
    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    return df


def load_data(config):
    """Load application, previous application, and bureau datasets from SQLite database."""
    logger.info("Loading datasets from SQLite database...")
    try:
        db_path = Path(config['paths']['db_path'])

        query_app = config['queries']['application']
        query_prev = config['queries']['previous_application']
        query_bureau = config['queries']['bureau']
        
        with sqlite3.connect(db_path) as conn:
            logger.info("Querying 'application' table...")
            df_app = pd.read_sql_query(query_app, conn)
            
            logger.info("Querying 'previous_application' table...")
            df_prev = pd.read_sql_query(query_prev, conn)
            
            logger.info("Querying 'bureau' table...")
            df_bureau = pd.read_sql_query(query_bureau, conn)

        logger.info("Converting loaded SQLite string columns to appropriate numeric types...")
        df_app = df_app.pipe(to_numeric_if_possible)
        df_prev = df_prev.pipe(to_numeric_if_possible)
        df_bureau = df_bureau.pipe(to_numeric_if_possible)

        if df_app.empty or df_prev.empty or df_bureau.empty:
            logger.warning("One or more loaded datasets are empty!")

        return df_app, df_prev, df_bureau
    except sqlite3.Error as e:
        logger.error(f"SQLite database error: {e}")
        raise
    except FileNotFoundError as e:
        logger.error(f"Failed to find database file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading datasets: {e}")
        raise