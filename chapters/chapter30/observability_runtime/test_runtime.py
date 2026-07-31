import json
import unittest

from observability_runtime import TraceRecorder


class TraceRecorderTest(unittest.TestCase):
    def test_nested_spans_share_trace_and_parent(self):
        recorder = TraceRecorder("trace-1")
        with recorder.span("root") as root:
            with recorder.span("child"):
                pass
        child, recorded_root = recorder.spans
        self.assertEqual(root.span_id, child.parent_span_id)
        self.assertEqual("trace-1", recorded_root.trace_id)

    def test_redacts_secret_attributes(self):
        recorder = TraceRecorder()
        with recorder.span("model", {"api_key": "secret", "model": "small"}):
            pass
        data = json.loads(recorder.to_json())
        self.assertEqual("[REDACTED]", data[0]["attributes"]["api_key"])

    def test_error_status_is_recorded(self):
        recorder = TraceRecorder()
        with self.assertRaises(RuntimeError):
            with recorder.span("tool"):
                raise RuntimeError("boom")
        self.assertEqual(1, recorder.metrics()["error_count"])


if __name__ == "__main__":
    unittest.main()
