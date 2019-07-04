"""Detects price signals at which to enter short and long positions.
"""
import datetime
import json
import random
from lib.breakout import entry_by_symbol

with open('./data/static/symbols.json') as f:
    STOCKS = json.load(f)

for timeframe in [{'entry': 20, 'exit': 10}, {'entry': 55, 'exit': 20}]:
    for method in ['min', 'max']:
        candidate = None
        while not candidate:
            random_pick = random.SystemRandom().choice(STOCKS)
            try:
                result = entry_by_symbol([random_pick], method, datetime.datetime.today(), timeframe['entry'],
                                         timeframe['exit'])
            except (TypeError, KeyError) as error:
                print(f"Error evaluating {random_pick}: {error}")
                continue
            candidate = result[0] if result else None

        print(f"Found {timeframe['entry']}-day { {'min': 'short', 'max': 'long'}[method] } candidate: {candidate}")
