import os
import argparse
import sys
import logging
from src.core.pipeline import DataPipeline
from src.core.generator import generate_messy_dataset

logger = logging.getLogger("CLI")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Antigravity Data Cleaning & Reporting Automation CLI Tool")
    parser.add_argument(
        "--input", 
        type=str, 
        help="Path to the raw input data file (CSV or Excel)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Path where cleaned dataset should be saved"
    )
    parser.add_argument(
        "--report", 
        type=str, 
        help="Path where PDF audit report should be saved"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to the cleaning configuration JSON file"
    )
    parser.add_argument(
        "--generate-sample", 
        action="store_true",
        help="Generates a messy e-commerce sales dataset and config file for demonstration purposes"
    )
    
    args = parser.parse_args()
    
    # Check if user requested sample data generation
    if args.generate_sample:
        raw_path = os.path.abspath("data/raw/sample_sales.csv")
        generate_messy_dataset(raw_path)
        logger.info(f"Sample dataset generated successfully at {raw_path}")
        return 0

    if not args.input:
        parser.print_help()
        sys.exit(1)
        
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        logger.error(f"Input file path does not exist: {input_path}")
        sys.exit(1)
        
    # Default Paths
    output_path = args.output
    if not output_path:
        base, ext = os.path.splitext(os.path.basename(input_path))
        output_path = os.path.abspath(f"data/processed/{base}_cleaned{ext}")
    else:
        output_path = os.path.abspath(output_path)
        
    report_path = args.report
    if not report_path:
        base, _ = os.path.splitext(os.path.basename(input_path))
        report_path = os.path.abspath(f"data/processed/{base}_audit_report.pdf")
    else:
        report_path = os.path.abspath(report_path)
        
    config_path = args.config
    if not config_path:
        config_path = os.path.abspath("config/default_config.json")
        if not os.path.exists(config_path):
            config_path = None
    else:
        config_path = os.path.abspath(config_path)

    logger.info("Initializing Data Cleaning Automation Pipeline...")
    logger.info(f"Input File: {input_path}")
    logger.info(f"Cleaned Output Target: {output_path}")
    logger.info(f"Audit PDF Target: {report_path}")
    logger.info(f"Config Profile: {config_path if config_path else 'AUTO CLEAN strategy'}")
    
    try:
        pipeline = DataPipeline(config_path)
        results = pipeline.run(input_path, output_path, report_path)
        
        logger.info("--------------------------------------------------")
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"Original Records: {results['raw_profile']['total_rows']}")
        logger.info(f"Standardized Records: {results['cleaned_rows']}")
        logger.info(f"Quality Index: {results['raw_profile']['health_score']}% -> {results['clean_profile']['health_score']}%")
        logger.info(f"Cleaned dataset saved: {output_path}")
        logger.info(f"Audit Report generated: {report_path}")
        logger.info("--------------------------------------------------")
        
    except Exception as e:
        logger.error(f"Pipeline failed with unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
