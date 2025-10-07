import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import json
from handlers import handle_leadtime_get

cases = [
    {"model_ids": ["PRIUS"]},
    {"model_ids": ["CROWN", "AQUA"]},
    {"model_ids": ["UNKNOWN"]},
    # MCP-like input where model_ids is passed as a JSON string
    {"model_ids": '["CROWN", "AQUA"]'},
    # MCP-like input where model_ids is passed as a plain string
    {"model_ids": 'CROWN,AQUA'}
]

for c in cases:
    print('INPUT:', c)
    res = handle_leadtime_get(c)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print('---')
