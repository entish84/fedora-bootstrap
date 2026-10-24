"""Dual logger supporting terminal ANSI output and persistent file logging."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional


class ANSIColors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class BootstrapLogger:
    """Central logging controller for bootstrap progress and debug journals."""

    def __init__(self, log_file: Optional[Path] = None, dry_run: bool = False):
        self.dry_run = dry_run
        self.log_file = log_file

        self._logger = logging.getLogger("fedora_bootstrap")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        # Clear existing handlers
        self._logger.handlers.clear()

        # File Handler (if log_file directory is writable or mock)
        if self.log_file:
            try:
                self.log_file.parent.mkdir(parents=True, exist_ok=True)
                fh = logging.FileHandler(str(self.log_file), encoding="utf-8")
                fh.setLevel(logging.DEBUG)
                fh_formatter = logging.Formatter(
                    "[%(asctime)s] [%(levelname)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                fh.setFormatter(fh_formatter)
                self._logger.addHandler(fh)
            except (PermissionError, OSError):
                # Ignore file write failures in unprivileged tests
                pass

    def info(self, msg: str) -> None:
        self._logger.info(msg)
        print(f"{ANSIColors.CYAN}ℹ{ANSIColors.RESET} {msg}")

    def success(self, msg: str) -> None:
        self._logger.info(f"SUCCESS: {msg}")
        print(f"{ANSIColors.GREEN}✔{ANSIColors.RESET} {msg}")

    def warning(self, msg: str) -> None:
        self._logger.warning(msg)
        print(f"{ANSIColors.YELLOW}⚠{ANSIColors.RESET} {msg}")

    def error(self, msg: str) -> None:
        self._logger.error(msg)
        print(f"{ANSIColors.RED}✖ {msg}{ANSIColors.RESET}", file=sys.stderr)

    def step(self, name: str, status: str = "RUNNING") -> None:
        badge = f"{ANSIColors.BOLD}[ {status} ]{ANSIColors.RESET}"
        if status == "OK":
            badge = f"{ANSIColors.GREEN}{ANSIColors.BOLD}[  OK  ]{ANSIColors.RESET}"
        elif status == "CHANGED":
            badge = f"{ANSIColors.CYAN}{ANSIColors.BOLD}[ DONE ]{ANSIColors.RESET}"
        elif status == "SKIPPED":
            badge = f"{ANSIColors.YELLOW}{ANSIColors.BOLD}[ SKIP ]{ANSIColors.RESET}"
        elif status == "DRY-RUN":
            badge = f"{ANSIColors.MAGENTA}{ANSIColors.BOLD}[ DRY  ]{ANSIColors.RESET}"
        elif status == "FAILED":
            badge = f"{ANSIColors.RED}{ANSIColors.BOLD}[ FAIL ]{ANSIColors.RESET}"

        print(f"{badge} {name}")
        self._logger.info(f"[{status}] {name}")

    def debug(self, msg: str) -> None:
        self._logger.debug(msg)


# Global singleton instance
logger = BootstrapLogger()
