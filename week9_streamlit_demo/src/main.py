"""
Data Pipeline Module

This script modularizes the data cleaning and transformation steps
from Week 5, Week 6, and python_quiz into a single, readable pipeline.
It outputs one central table with the cleaned, merged, and transformed data.

Refactored to use a single configuration dictionary and Pandas method chaining.
"""

from pathlib import Path
from loguru import logger
from config import CONFIG
from stage_1_load_data import load_data
from stage_2_clean_transform import clean_application_data, transform_application_data, transform_post_merge
from stage_3_aggregate import aggregate_bureau, aggregate_previous_applications, create_cubes
from stage_4_validate import validate_final_table

repo_root = Path(CONFIG['paths']['repo_root'])     
logger.add(Path(repo_root) / CONFIG['paths']['log_dir'] / CONFIG['paths']['log_file'], rotation="10 MB", retention="10 days")
    
def run_pipeline():
    """Run the entire data pipeline to produce the final data cube using chaining."""
    try:

        logger.info(f"Repository root resolved to: {repo_root}")

        df_app, df_prev, df_bureau = load_data(CONFIG)
        
        df_prev_agg = aggregate_previous_applications(df_prev, CONFIG)
        df_bureau_agg = aggregate_bureau(df_bureau, CONFIG)
        
        logger.info("Executing main pipeline and merging datasets...")
  
        final_df = (df_app
            .pipe(clean_application_data, config=CONFIG)
            .pipe(transform_application_data, config=CONFIG)
            .merge(df_prev_agg, on='SK_ID_CURR', how='left')
            .merge(df_bureau_agg, on='SK_ID_CURR', how='left')
            .assign(
                recent_prev_app_count=lambda x: x['recent_prev_app_count'].fillna(0),
                refused_count=lambda x: x['refused_count'].fillna(0),
                total_bureau_debt=lambda x: x['total_bureau_debt'].fillna(0),
                bureau_loan_count=lambda x: x['bureau_loan_count'].fillna(0)
            )
            .pipe(transform_post_merge, config=CONFIG)
        )
        
        # Run data quality validation
        validate_final_table(final_df, CONFIG)
        
        # Save the final table
        output_dir = Path(repo_root) / CONFIG['paths']['output_dir']
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            
        output_path = output_dir / CONFIG['paths']['output_file']
        logger.info(f"Saving final table to {output_path}...")
        final_df.to_csv(output_path, index=False)
        
        logger.info("Pipeline completed successfully!")
        logger.info(f"Final dataset shape: {final_df.shape}")

        # Aggregate cubes from the final dataset
        final_cube = create_cubes(final_df)

        # Save the final cube                  
        cube_path = Path(repo_root) / CONFIG['paths']['output_dir'] / CONFIG['paths']['cube_file']
        logger.info(f"Saving final cube to {cube_path}...")
        final_cube.to_csv(cube_path, index=False)
                 
        logger.info("Cube aggregation completed successfully!")
        logger.info(f"Final cube shape: {final_cube.shape}")        
              
        return final_cube   
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise


if __name__ == "__main__":
    run_pipeline()
