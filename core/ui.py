"""Interactive terminal UI with standard library ANSI styling and optional Rich enhancement."""

import sys
from typing import List, Optional, Tuple
from core.logger import ANSIColors


def print_banner() -> None:
    banner = f"""
{ANSIColors.CYAN}{ANSIColors.BOLD}================================================================================
          FEDORA LINUX 44 BOOTSTRAP WIZARD (Python Edition)
================================================================================{ANSIColors.RESET}
    """
    print(banner)


def prompt_choice(question: str, options: List[Tuple[str, str]], default_idx: int = 0) -> str:
    """Prompt user to choose one item from a list of options (value, label)."""
    print(f"\n{ANSIColors.BOLD}{ANSIColors.YELLOW}[?]{ANSIColors.RESET} {ANSIColors.BOLD}{question}{ANSIColors.RESET}")
    for idx, (val, label) in enumerate(options, start=1):
        def_mark = " (Default)" if idx - 1 == default_idx else ""
        print(f"  {ANSIColors.CYAN}{idx}.{ANSIColors.RESET} {label}{def_mark}")

    while True:
        try:
            choice = input(f"\nEnter choice [1-{len(options)}] (default: {default_idx + 1}): ").strip()
            if not choice:
                return options[default_idx][0]
            num = int(choice)
            if 1 <= num <= len(options):
                return options[num - 1][0]
        except (ValueError, KeyboardInterrupt, EOFError):
            pass
        print(f"{ANSIColors.RED}Invalid selection. Please enter a number between 1 and {len(options)}.{ANSIColors.RESET}")


def prompt_yes_no(question: str, default: bool = True) -> bool:
    """Prompt user with a yes/no question."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        try:
            ans = input(f"\n{ANSIColors.BOLD}{ANSIColors.YELLOW}[?]{ANSIColors.RESET} {ANSIColors.BOLD}{question}{ANSIColors.RESET}{suffix}").strip().lower()
            if not ans:
                return default
            if ans in ("y", "yes"):
                return True
            if ans in ("n", "no"):
                return False
        except (KeyboardInterrupt, EOFError):
            print()
            return default
        print(f"{ANSIColors.RED}Please answer 'y' or 'n'.{ANSIColors.RESET}")


def prompt_text(question: str, default: Optional[str] = None) -> str:
    """Prompt user for a free text string."""
    def_str = f" (default: {default})" if default else ""
    try:
        val = input(f"\n{ANSIColors.BOLD}{ANSIColors.YELLOW}[?]{ANSIColors.RESET} {ANSIColors.BOLD}{question}{ANSIColors.RESET}{def_str}: ").strip()
        if not val and default is not None:
            return default
        return val
    except (KeyboardInterrupt, EOFError):
        print()
        return default or ""


def prompt_checkboxes(
    question: str,
    options: List[Tuple[str, str, bool]]  # (key, label, default_checked)
) -> List[str]:
    """Simple command-line multi-select list."""
    print(f"\n{ANSIColors.BOLD}{ANSIColors.YELLOW}[?]{ANSIColors.RESET} {ANSIColors.BOLD}{question}{ANSIColors.RESET}")
    print(f"{ANSIColors.DIM}Enter comma-separated numbers to toggle, or press Enter to accept current selection:{ANSIColors.RESET}")

    selected = {key: checked for key, _, checked in options}

    while True:
        for idx, (key, label, _) in enumerate(options, start=1):
            mark = f"{ANSIColors.GREEN}[X]{ANSIColors.RESET}" if selected[key] else "[ ]"
            print(f"  {idx}. {mark} {label}")

        try:
            inp = input("\nToggle numbers (or Enter to confirm): ").strip()
            if not inp:
                break

            parts = [p.strip() for p in inp.split(",") if p.strip()]
            for p in parts:
                if p.isdigit():
                    idx = int(p)
                    if 1 <= idx <= len(options):
                        key = options[idx - 1][0]
                        selected[key] = not selected[key]
        except (KeyboardInterrupt, EOFError):
            print()
            break

    return [k for k, v in selected.items() if v]


def print_plan_summary(summary_items: List[Tuple[str, str]]) -> None:
    print(f"\n{ANSIColors.CYAN}{ANSIColors.BOLD}--------------------------------------------------------------------------------")
    print(f"                         SUMMARY OF PLANNED OPERATIONS")
    print(f"--------------------------------------------------------------------------------{ANSIColors.RESET}")
    for label, val in summary_items:
        print(f"  {ANSIColors.BOLD}{label:<22}:{ANSIColors.RESET} {val}")
    print(f"{ANSIColors.CYAN}--------------------------------------------------------------------------------{ANSIColors.RESET}\n")
