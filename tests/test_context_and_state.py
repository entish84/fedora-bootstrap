"""Test execution context detection and state journal persistence."""

from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.context import ExecutionContext
from core.state import StateTracker


class TestContextAndState(unittest.TestCase):
    def test_context_detect(self):
        ctx = ExecutionContext.detect(dry_run=True)
        self.assertIsNotNone(ctx.target_user)
        self.assertIsInstance(ctx.target_uid, int)
        self.assertIsInstance(ctx.target_gid, int)
        self.assertTrue(ctx.target_home.exists() or ctx.dry_run)
        self.assertTrue(ctx.dry_run)

    def test_state_tracker_in_sandbox(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "state.json"
            ctx = ExecutionContext.detect(dry_run=False)
            ctx.state_file = state_file

            tracker = StateTracker(ctx)
            self.assertFalse(tracker.is_task_completed("test_task"))

            tracker.mark_task_completed("test_task", {"status": "ok"})
            self.assertTrue(tracker.is_task_completed("test_task"))
            self.assertTrue(state_file.exists())

            # Reload tracker from file
            tracker2 = StateTracker(ctx)
            self.assertTrue(tracker2.is_task_completed("test_task"))
            self.assertFalse(tracker2.is_new_state)

            # Test removing state.json resets state to new
            state_file.unlink()
            tracker3 = StateTracker(ctx)
            self.assertFalse(tracker3.is_task_completed("test_task"))
            self.assertTrue(tracker3.is_new_state)


if __name__ == "__main__":
    unittest.main()
