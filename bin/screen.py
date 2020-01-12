"""Detects price signals at which to enter short and long positions.
"""
import datetime
import json
import random
from lib.breakout import entry_by_symbol

with open('./data/static/symbols.json') as f:
    STOCKS = json.load(f)

def reset():
    """
    outputs candidate of "None" and a randomly-chosen timeframe and method.
    """
    timeframe = random.SystemRandom().choice([{'entry': 20, 'exit': 10}, {'entry': 55, 'exit': 20}])
    method = random.SystemRandom().choice(['min', 'max'])
    print(f"Timeframe: {timeframe}\tMethod: {method}")
    return (None, timeframe, method)

def main():
    """
    choose a potential stock candidate based on a randomly selected timeframe and strategy (short or long)
    """
    while True:
        candidate, timeframe, method = reset()
        while not candidate:
            random_pick = random.SystemRandom().choice(STOCKS)
            try:
                result = entry_by_symbol([random_pick], method,
                                         datetime.datetime.today(),
                                         timeframe['entry'],
                                         timeframe['exit'])
            except (TypeError, KeyError) as error:
                print(f"Error evaluating {random_pick}: {error}")
                continue
            if result:
                candidate = result[0]
                print(f"Found {timeframe['entry']}-day { {'min': 'short', 'max': 'long'}[method] } " +\
                    f"candidate: {candidate}")
                candidate, timeframe, method = reset()

main()
