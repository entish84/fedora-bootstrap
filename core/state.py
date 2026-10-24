"""State persistence engine for idempotency and resumability."""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional
from core.context import ExecutionContext
from core.logger import logger


class StateTracker:
    """Tracks applied tasks and configurations to ensure idempotent executions."""

    def __init__(self, ctx: ExecutionContext):
        self.ctx = ctx
        self.state_file = ctx.state_file
        self.data: Dict[str, Any] = {
            "version": 1,
            "created_at": time.time(),
            "updated_at": time.time(),
            "profile": ctx.profile,
            "completed_tasks": {},
            "metadata": {}
        }
        self._load()

    def _load(self) -> None:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.data.update(loaded)
            except Exception as e:
                logger.warning(f"Could not load state file {self.state_file}: {e}")

    def save(self) -> None:
        if self.ctx.dry_run:
            return

        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            self.data["updated_at"] = time.time()
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist state file {self.state_file}: {e}")

    def is_task_completed(self, task_name: str) -> bool:
        return task_name in self.data.get("completed_tasks", {})

    def mark_task_completed(self, task_name: str, details: Optional[Dict[str, Any]] = None) -> None:
        if "completed_tasks" not in self.data:
            self.data["completed_tasks"] = {}
        self.data["completed_tasks"][task_name] = {
            "timestamp": time.time(),
            "details": details or {}
        }
        self.save()

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.data.get("metadata", {}).get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        self.data["metadata"][key] = value
        self.save()
