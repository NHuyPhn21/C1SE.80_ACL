"""SSE queue stream: emits on change only and closes at a terminal status."""

import json
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend import api
from fastapi_app import app


def snap(status, progress, logs=0):
    return {
        "project_id": 1,
        "task": {"id": 1, "status": status, "progress_percent": progress} if status else None,
        "logs": [{"level": "INFO", "message": f"m{i}", "timestamp": "t"} for i in range(logs)],
    }


class QueueStreamTests(unittest.TestCase):
    def run_stream(self, snapshots):
        feed = iter(snapshots)
        with patch.object(api, "_serialize_queue", side_effect=lambda *a, **k: next(feed)), \
             patch.object(api.time, "sleep"):
            return list(api._queue_event_stream(1, None))

    def test_emits_only_on_change_and_finishes_on_terminal(self) -> None:
        frames = self.run_stream([
            snap("RUNNING", 10),
            snap("RUNNING", 10),            # unchanged -> no frame
            snap("RUNNING", 50, logs=1),
            snap("COMPLETED", 100, logs=2),
        ])
        data = [f for f in frames if f.startswith("data: {\"")]
        self.assertEqual(len(data), 3)
        self.assertEqual(json.loads(data[-1][6:])["task"]["status"], "COMPLETED")
        self.assertEqual(frames[-1], "event: done\ndata: {}\n\n")

    def test_stays_open_while_no_task_exists(self) -> None:
        frames = self.run_stream([snap(None, 0), snap(None, 0), snap("QUEUED", 0), snap("FAILED", 0)])
        self.assertEqual(frames[-1], "event: done\ndata: {}\n\n")
        self.assertEqual(sum(f.startswith("data: ") for f in frames), 3)

    def test_awaiting_review_is_terminal(self) -> None:
        frames = self.run_stream([snap("AWAITING_REVIEW", 100)])
        self.assertEqual(frames[-1], "event: done\ndata: {}\n\n")

    def test_endpoint_unknown_project_is_404(self) -> None:
        response = TestClient(app).get("/api/projects/999999/queue/stream")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
