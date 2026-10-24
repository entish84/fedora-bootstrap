"""Subprocess executor with privilege separation (root vs user) and dry-run safety."""

import os
import shlex
import subprocess
import sys
from typing import List, Optional, Union
from core.context import ExecutionContext
from core.logger import logger, ANSIColors


class ExecutionResult:
    """Standardized result of a command execution."""

    def __init__(self, returncode: int, stdout: str = "", stderr: str = ""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    @property
    def success(self) -> bool:
        return self.returncode == 0


def run_root(
    cmd: Union[str, List[str]],
    ctx: ExecutionContext,
    check: bool = True,
    capture: bool = False,
    env: Optional[dict] = None
) -> ExecutionResult:
    """Execute a system-level command with root privileges."""
    cmd_str = cmd if isinstance(cmd, str) else " ".join(shlex.quote(c) for c in cmd)
    cmd_list = shlex.split(cmd) if isinstance(cmd, str) else cmd

    if ctx.dry_run:
        logger.debug(f"[DRY-RUN ROOT] {cmd_str}")
        return ExecutionResult(returncode=0, stdout="[dry-run output]")

    logger.debug(f"[EXEC ROOT] {cmd_str}")

    exec_env = os.environ.copy()
    if env:
        exec_env.update(env)

    try:
        proc = subprocess.run(
            cmd_list,
            check=check,
            capture_output=capture,
            text=True,
            env=exec_env
        )
        return ExecutionResult(
            returncode=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or ""
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Root command failed (code {e.returncode}): {cmd_str}")
        if capture and e.stderr:
            logger.error(f"STDERR: {e.stderr.strip()}")
        if check:
            raise
        return ExecutionResult(
            returncode=e.returncode,
            stdout=e.stdout or "",
            stderr=e.stderr or ""
        )


def run_user(
    cmd: Union[str, List[str]],
    ctx: ExecutionContext,
    check: bool = True,
    capture: bool = False,
    env: Optional[dict] = None
) -> ExecutionResult:
    """Execute a command as the target unprivileged user (preventing root pollution in $HOME)."""
    cmd_str = cmd if isinstance(cmd, str) else " ".join(shlex.quote(c) for c in cmd)

    if ctx.dry_run:
        logger.debug(f"[DRY-RUN USER ({ctx.target_user})] {cmd_str}")
        return ExecutionResult(returncode=0, stdout="[dry-run output]")

    logger.debug(f"[EXEC USER ({ctx.target_user})] {cmd_str}")

    # Build sudo -u user -H wrapper ensuring user paths (~/.local/bin, ~/bin, /usr/local/bin) are on PATH
    wrapped_cmd = f'export PATH="$HOME/.local/bin:$HOME/bin:/usr/local/bin:$PATH"; {cmd_str}'
    user_cmd = ["sudo", "-u", ctx.target_user, "-H", "bash", "-c", wrapped_cmd]

    exec_env = os.environ.copy()
    exec_env["HOME"] = str(ctx.target_home)
    exec_env["USER"] = ctx.target_user
    exec_env["LOGNAME"] = ctx.target_user
    if env:
        exec_env.update(env)

    try:
        proc = subprocess.run(
            user_cmd,
            check=check,
            capture_output=capture,
            text=True,
            env=exec_env
        )
        return ExecutionResult(
            returncode=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or ""
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"User command failed for {ctx.target_user} (code {e.returncode}): {cmd_str}")
        if capture and e.stderr:
            logger.error(f"STDERR: {e.stderr.strip()}")
        if check:
            raise
        return ExecutionResult(
            returncode=e.returncode,
            stdout=e.stdout or "",
            stderr=e.stderr or ""
        )
