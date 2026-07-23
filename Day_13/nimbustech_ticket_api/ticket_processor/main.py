"""Command-line entry point for NimbusTech ticket processing."""

import argparse
import json
import logging
import sys
from pathlib import Path

from .config import DEFAULT_OUTPUT_PATH, INVALID_ROW_ABORT_RATIO
from .processor import build_report, process_csv


def configure_logging():
    """Configure application logging.

    Returns:
        logging.Logger: Logger for the ticket processor.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    return logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line options for the processing script.

    Returns:
        argparse.Namespace: Input and output file paths.
    """
    parser = argparse.ArgumentParser(description="Process NimbusTech ticket exports.")
    parser.add_argument("--input", required=True, type=Path, help="Raw CSV input path.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="JSON report output path.",
    )
    return parser.parse_args()


def write_report(report, output_path):
    """Write a ticket report as formatted JSON.

    Args:
        report: JSON-serializable report data.
        output_path: Destination report path.

    Returns:
        None
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(report, output_file, indent=2)


def main():
    """Run the ticket-processing command-line workflow.

    Returns:
        int: Zero on success, otherwise a non-zero error code.
    """
    logger = configure_logging()
    arguments = parse_arguments()
    logger.info("Starting ticket processing for %s", arguments.input)

    try:
        valid_tickets, invalid_rows = process_csv(arguments.input, logger)
    except (FileNotFoundError, OSError, ValueError) as error:
        logger.error("Unable to process input: %s", error)
        return 1

    total_rows = len(valid_tickets) + len(invalid_rows)
    invalid_ratio = len(invalid_rows) / total_rows if total_rows else 0
    if total_rows == 0:
        logger.error("Input CSV contains no ticket rows; report was not written.")
        return 1
    if invalid_ratio > INVALID_ROW_ABORT_RATIO:
        logger.error(
            "Abort triggered: %.1f%% invalid rows exceeds the %.1f%% limit.",
            invalid_ratio * 100,
            INVALID_ROW_ABORT_RATIO * 100,
        )
        return 1

    report = build_report(valid_tickets, invalid_rows)
    try:
        write_report(report, arguments.output)
    except OSError as error:
        logger.error("Unable to write report: %s", error)
        return 1

    logger.info("Report written to %s", arguments.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
