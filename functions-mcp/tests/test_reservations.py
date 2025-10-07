import sys
import os
import json

# Ensure project root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from handlers import handle_reservations_create


def test_missing_customer_id():
    body = {
        # intentionally omit customer_id
        "vehicle_id": "PRIUS",
        "grade_id": "PRIUS-G",
        "engine_id": "PRIUS-G-1.8L",
        "preferred_times": ["2025-10-11T10:00"]
    }
    res = handle_reservations_create(body)
    assert isinstance(res, dict)
    assert res.get("error") == "missing_required_parameters"
    assert "customer_id" in res.get("message", "")


if __name__ == '__main__':
    # quick local run
    try:
        test_missing_customer_id()
        print('TEST_PASS')
    except AssertionError as e:
        print('TEST_FAIL', e)
