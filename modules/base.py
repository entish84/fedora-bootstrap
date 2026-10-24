"""Base definitions and task runner execution harness."""

from abc import ABC, abstractmethod
from typing import List, Optional
from core.context import ExecutionContext
from core.logger import logger
from core.state import StateTracker


class BaseTask(ABC):
    """Abstract contract for an idempotent provisioning task."""

    name: str = "base_task"
    description: str = "Base task description"

    @abstractmethod
    def is_applicable(self, ctx: ExecutionContext) -> bool:
        """Return True if this task applies to the selected configuration."""
        pass

    @abstractmethod
    def check(self, ctx: ExecutionContext) -> bool:
        """Return True if the task's desired state is already satisfied (idempotent skip)."""
        pass

    @abstractmethod
    def apply(self, ctx: ExecutionContext) -> bool:
        """Execute the task actions. Return True on success."""
        pass

    def rollback(self, ctx: ExecutionContext) -> None:
        """Optional rollback logic on catastrophic failure."""
        pass


class TaskRunner:
    """Orchestrates sequential execution of BaseTask modules with idempotency checks."""

    def __init__(self, ctx: ExecutionContext, state: StateTracker):
        self.ctx = ctx
        self.state = state
        self.tasks: List[BaseTask] = []

    def register(self, task: BaseTask) -> None:
        self.tasks.append(task)

    def run_all(self) -> bool:
        """Execute all applicable tasks in sequential order."""
        total = len(self.tasks)
        logger.info(f"Starting execution of {total} registered tasks...")

        for idx, task in enumerate(self.tasks, start=1):
            if not task.is_applicable(self.ctx):
                logger.step(f"[{idx}/{total}] {task.description}", status="SKIPPED")
                continue

            # Check if task was completed in state journal or checks pass
            is_already_done = False
            try:
                if self.state.is_task_completed(task.name) or task.check(self.ctx):
                    is_already_done = True
            except Exception as e:
                logger.debug(f"Check failed for {task.name}: {e}")

            if is_already_done:
                logger.step(f"[{idx}/{total}] {task.description} (Already satisfied)", status="OK")
                continue

            # Run in dry-run mode
            if self.ctx.dry_run:
                logger.step(f"[{idx}/{total}] {task.description}", status="DRY-RUN")
                try:
                    task.apply(self.ctx)
                except Exception as e:
                    logger.debug(f"Dry-run simulation for {task.name}: {e}")
                continue

            # Execute live task
            logger.step(f"[{idx}/{total}] {task.description}...", status="RUNNING")
            try:
                success = task.apply(self.ctx)
                if success:
                    self.state.mark_task_completed(task.name)
                    logger.step(f"[{idx}/{total}] {task.description}", status="CHANGED")
                else:
                    logger.step(f"[{idx}/{total}] {task.description}", status="FAILED")
                    return False
            except Exception as e:
                logger.error(f"Task '{task.name}' failed with error: {e}")
                logger.step(f"[{idx}/{total}] {task.description}", status="FAILED")
                try:
                    task.rollback(self.ctx)
                except Exception as rb_err:
                    logger.warning(f"Rollback failed for {task.name}: {rb_err}")
                return False

        logger.success("All pipeline tasks completed successfully.")
        return True
