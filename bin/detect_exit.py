"""Detects price signals at which to exit a position.
"""
import datetime
from lib.breakout import exit_by_symbol

POSITIONS = {'10': {'min': [], 'max': ['TSCO', 'TLT']},
             '20': {'min': ['DEST'], 'max': ['APPF', 'VCSH']}}

for position_timeframe in POSITIONS:
    for position_mode in POSITIONS[position_timeframe].keys():
        symbols_to_consider = exit_by_symbol(POSITIONS[position_timeframe][position_mode], position_mode,
                                             datetime.datetime.today(), int(position_timeframe))
        print(f"{position_timeframe}-day { {'min': 'short', 'max': 'long'}[position_mode] }"\
               " positions to consider exiting:", symbols_to_consider)
