"""Scheduled Docker cleanup helper.

This script keeps the host Docker environment tidy by scheduling a daily
`docker system prune -a -f --volumes` run at 03:00. It logs disk space
before and after cleanup so operators can monitor reclaimed capacity.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import time
from pathlib import Path

import schedule

LOG_PATH = Path(__file__).with_suffix(".log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def _format_bytes(num_bytes: int) -> str:
    """Return a human readable representation of bytes."""
    step_unit = 1024
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"]
    size = float(num_bytes)
    for idx, unit in enumerate(units):
        # If we've reached the largest unit, stop scaling.
        if size < step_unit or idx == len(units) - 1:
            return f"{size:0.2f} {unit}"
        size /= step_unit


def log_free_space() -> None:
    """Log the total and free space for the filesystem hosting this repo."""
    repo_path = Path(__file__).resolve().parent
    total, used, free = shutil.disk_usage(repo_path)
    logging.info(
        "Disk usage - total: %s, used: %s, free: %s",
        _format_bytes(total),
        _format_bytes(used),
        _format_bytes(free),
    )


def prune_docker() -> None:
    """Run docker prune and log disk usage before/after the cleanup."""
    logging.info("Starting scheduled Docker cleanup task.")
    log_free_space()
    try:
        result = subprocess.run(
            ["docker", "system", "prune", "-a", "-f", "--volumes"],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            logging.info("Docker prune output:\n%s", result.stdout.strip())
        if result.stderr.strip():
            logging.warning("Docker prune stderr:\n%s", result.stderr.strip())
    except subprocess.CalledProcessError as exc:
        logging.error("Docker prune failed: %s", exc)
        if exc.stdout:
            logging.error("stdout:\n%s", exc.stdout)
        if exc.stderr:
            logging.error("stderr:\n%s", exc.stderr)
    finally:
        log_free_space()
        logging.info("Completed Docker cleanup task.")


schedule.every().day.at("03:00").do(prune_docker)


if __name__ == "__main__":
    logging.info("DevOps agent started. Daily cleanup scheduled for 03:00.")
    while True:
        schedule.run_pending()
        time.sleep(60)
