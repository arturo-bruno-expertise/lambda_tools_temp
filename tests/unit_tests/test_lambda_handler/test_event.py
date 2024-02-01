import json
from pathlib import Path

from call_conversions.app import parse_event


class TestEvent:
    def test_event_parser(self):
        test_data_file = Path(
            Path(__file__).parent.parent.parent, "test_data", "lambda_event.json"
        )
        test_data = json.loads(test_data_file.read_text())

        assert parse_event(test_data) == test_data
