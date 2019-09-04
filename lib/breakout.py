"""Analyzes stock data for price breakouts, used as entry and exit signals.
"""
from random import randint
import datetime
import json
from .alphavantage import backward_from
from .maths import exp_moving_average

def detected(numbers, mode):
    """
    Returns a Boolean result indicating whether the last member in a numeric array is the max or
    min, depending on the setting.

    Arguments
      - numbers: an array of numbers
      - mode: 'max' or 'min'
    """
    call_dict = {'min': min, 'max': max}
    if mode not in call_dict.keys():
        print('Must specify either max or min')
        return
    return numbers[-1] == call_dict[mode](numbers)

def entry_by_symbol(symbols,
                    mode,
                    day_to_analyze=datetime.datetime.today(),
                    num_days_entry=55,
                    num_days_exit=20,
                    avg_smoothing_period=2):
    """
    Returns a subset of symbols for which:
      1) a breakout indicator has been detected on the specified day of trading (or most recent
         trading day before that)
      2) the previously detected breakout cycle, if acted upon, would have led to a
         loss (i.e. the last 'max' breakout cycle ended with the price lower than when
         it began and vice-versa for a 'min' breakout cycle)
    Arguments
      - symbols: array of ticker symbols to analyze
      - mode: 'max' or 'min'
      - day_to_analyze: the trading day to analyze (defaults to most recent trading day)
      - num_days_entry: number of days before which a "entry" breakout is considered actionable
      - num_days_exit: number of days before which a "exit" breakout is considered actionable
      - avg_smoothing_period: period used in calculating EMA
    """
    symbols_to_consider = []
    for symbol in symbols:
        print(f"Evaluating {symbol}")
        try:
            data = backward_from(symbol, num_days_entry + avg_smoothing_period, day_to_analyze)
            price_subset_entry = exp_moving_average([float(data[date]['4. close']) for\
                date in data], avg_smoothing_period)\
                [avg_smoothing_period:]
            if detected(price_subset_entry, mode):
                print('detected...')
                historical_data = backward_from(symbol, 365, day_to_analyze)
                if last_breakout_failed(mode, historical_data, num_days_entry, num_days_exit):
                    print(price_subset_entry)
                    print(f"Trend duration: {trend_duration(mode, historical_data, num_days_entry, avg_smoothing_period)}")
                    symbols_to_consider.append(symbol)
                else:
                    print('BUT LAST BREAKOUT DID NOT FAIL')
        except (json.decoder.JSONDecodeError, OverflowError, LookupError) as error:
            print(f"Error evaluating {symbol}: {error}")
    return symbols_to_consider

def exit_mode(mode):
    """
    Returns 'min' if given 'max' and vice-versa.
    Arguments
      - mode: 'max' or 'min'
    """
    return 'min' if mode == 'max' else 'max'

def exit_by_symbol(symbols,
                   mode,
                   day_to_analyze=datetime.datetime.today(),
                   num_days_exit=20,
                   avg_smoothing_period=2):
    """
    Returns a subset of symbols for which an exit signal has been detected on the day specified.
    Arguments
      - symbols: array of ticker symbols to analyze
      - mode: 'max' or 'min'
      - day_to_analyze: the trading day to analyze (defaults to most recent trading day)
      - num_days_entry: number of days before which a "entry" breakout is considered actionable
      - num_days_exit: number of days before which a "exit" breakout is considered actionable
      - avg_smoothing_period: period used in calculating EMA
    """
    symbols_to_consider = []

    for symbol in symbols:
        print(f"Evaluating {symbol}")
        data = backward_from(symbol, num_days_exit + avg_smoothing_period, day_to_analyze)
        price_subset_exit = exp_moving_average([float(data[date]['4. close'])\
            for date in data], avg_smoothing_period)[avg_smoothing_period:]
        print(price_subset_exit)
        if detected(price_subset_exit, exit_mode(mode)):
            symbols_to_consider.append(symbol)
    return symbols_to_consider

def get_breakout_price(historical_data,
                       mode,
                       dates,
                       len_dates,
                       offset,
                       num_days_breakout,
                       verbose=True,
                       avg_smoothing_period=2,
                       step_dir='backward'):
    """
    Returns the price at which a breakout signal was detected.
    Arguments
      - historical_data: dict of historical data following format {'date': {'4. close': some_price}}
      - mode: 'max' or 'min'
      - dates: sorted list of the dates in historical_data, precalculated for efficiency
      - len_dates: length of dates list
      - offset: number of days back from which to begin search for breakout
      - num_days_breakout: number of days before which a breakout is considered actionable
      - avg_smoothing_period: period used in calculating EMA
      - step_dir: direction in which to traverse the price data ('forward' or 'backward')
    """
    price = None
    while not price:
        price_subset = [float(historical_data[date]['4. close']) for date in \
            dates[len_dates - num_days_breakout - offset - avg_smoothing_period:len_dates - offset]]
        price_subset_smoothed = exp_moving_average(price_subset, avg_smoothing_period)[avg_smoothing_period:]
        if detected(price_subset_smoothed, mode):
            price = price_subset[-1]
        else:
            offset += 1 if step_dir == 'backward' else -1
    if verbose:
        print(f"{mode} breakout price is {price} on",
              f"{dates[len_dates - num_days_breakout - offset - avg_smoothing_period:len_dates - offset][-1]}")
    return price, offset

def last_breakout_failed(mode,
                         historical_data,
                         num_days_entry=55,
                         num_days_exit=20):
    """
    Returns a Boolean result indicating whether the last breakout cycle before the specified date,
    if acted upon, would have led to a loss.

    Arguments
      - mode: 'max' or 'min'
      - historical_data: dict of historical data following format {'date': {'4. close': some_price}}
      - num_days_entry: number of days before which a "entry" breakout is considered actionable
      - num_days_exit: number of days before which a "exit" breakout is considered actionable
    """
    dates = sorted(list(historical_data.keys()))
    len_dates = len(dates)
    offset = 0
    entry_breakout_price = None
    offset = get_breakout_price(historical_data, exit_mode(mode), dates, len_dates, offset, num_days_exit, False)[1]
    near_offset = get_breakout_price(historical_data, mode, dates, len_dates, offset, num_days_entry, False)[1]
    antefar_offset = get_breakout_price(historical_data, exit_mode(mode), dates, len_dates, near_offset, num_days_exit,
                                        False)[1]
    far_offset = get_breakout_price(historical_data, mode, dates, len_dates, antefar_offset, num_days_entry, False, 2,
                                    'forward')[1]
    print(f"furthest back {mode} is {historical_data[dates[len_dates - far_offset]]['4. close']} on",
          f"{dates[len_dates - far_offset]} and the nearest is",
          f"{historical_data[dates[len_dates - near_offset]]['4. close']} on {dates[len_dates - near_offset]}")
    entry_breakout_index = randint(near_offset, far_offset)
    entry_breakout_price = float(historical_data[dates[len_dates - entry_breakout_index]]['4. close'])
    print(f"selected entry price {entry_breakout_price} on {dates[len_dates - entry_breakout_index]}")
    exit_breakout_price = get_breakout_price(historical_data, exit_mode(mode), dates, len_dates, near_offset,
                                             num_days_exit, True, 2, 'forward')[0]
    return (exit_breakout_price < entry_breakout_price) if mode == 'max' else\
        (exit_breakout_price > entry_breakout_price)

def trend_duration(mode,
                   historical_data,
                   num_days_breakout,
                   avg_smoothing_period=2):
    """
    Returns the number of days that a given breakout has persisted before the inputted date. If, for
    example, the inputted date is the first on which the given trend has been detected, then
    trend_duration returns 0.
    Arguments:
      - mode: 'max' or 'min'
      - historical_data: dict of historical data following format {'date': {'4. close': some_price}}
      - num_days_breakout: number of days before which a breakout is considered actionable
      - avg_smoothing_period: period used in calculating EMA
    """
    dates = sorted(list(historical_data.keys()))
    len_dates = len(dates)
    offset = 0
    streak_ongoing = True
    while streak_ongoing:
        price_subset = [float(historical_data[date]['4. close']) for date in \
            dates[len_dates - num_days_breakout - offset - avg_smoothing_period:len_dates - offset]]
        price_subset_smoothed = exp_moving_average(price_subset, avg_smoothing_period)[avg_smoothing_period:]
        streak_ongoing = detected(price_subset_smoothed, mode)
        if streak_ongoing:
            offset += 1
    return offset
