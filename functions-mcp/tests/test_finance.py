import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from handlers import handle_finance_precheck
import json

cases = [
    {"income": 12000000, "requested_amount": 2000000},
    {"customer_profile": {"income":6000000}, "requested_amount":3000000},
    {"income": 0, "requested_amount": 1000000},
    {"income":8000000, "requested_amount":4000000, "existing_debt":5000000, "dependents":2}
]
for c in cases:
    print('INPUT:', c)
    print(json.dumps(handle_finance_precheck(c), ensure_ascii=False, indent=2))
    print('---')
