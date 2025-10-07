import sys
import os

# ensure project root on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from handlers import handle_quotation_calc


def test_subscription_basic():
    body = {
        "vehicle_price": 3500000,
        "subscription_term_months": 36,
        "maintenance_included": True,
        "discount_percent": 5
    }
    res = handle_quotation_calc(body)
    assert isinstance(res, dict)
    assert res.get("monthly_fee") is not None
    assert res.get("term_months") == 36


if __name__ == '__main__':
    try:
        test_subscription_basic()
        print('TEST_PASS')
    except AssertionError as e:
        print('TEST_FAIL', e)
