"""
Main script for running the evaluation agent.

This script loads configuration from a YAML file and executes
the evaluation agent with the specified parameters.
"""

import json
import os
from pathlib import Path
import yaml

from descidb.query.evaluation_agent import EvaluationAgent
from descidb.utils.logging_utils import get_logger

# Get module logger
logger = get_logger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parents[2]
# Config file path relative to project root
CONFIG_PATH = PROJECT_ROOT / "config" / "evaluation.yml"


def load_config() -> dict:
    """
    Load configuration from YAML file.

    Returns:
        Dictionary containing configuration parameters
    """
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)

    logger.info(f"Loaded configuration from {CONFIG_PATH}")
    return config


def main():
    """Main function to run the evaluation agent."""
    # Load configuration
    config = load_config()

    # Initialize evaluation agent
    agent = EvaluationAgent(model_name=config.get("model_name"))

    # Run query on collections
    results_file = agent.query_collections(
        query=config.get("query"),
        collection_names=config.get("collections"),
        db_path=config.get("db_path")
    )

    # Evaluate results
    evaluation = agent.evaluate_results(results_file)

    # Output results
    output_dir = config.get("output_dir")
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_file = Path(output_dir) / "evaluation_results.json"
        with open(output_file, 'w') as f:
            json.dump(evaluation, f, indent=2)
        logger.info(f"Saved evaluation results to {output_file}")

    # Print results to stdout
    print(json.dumps(evaluation, indent=2))


if __name__ == "__main__":
    main()
