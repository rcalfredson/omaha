"""AlphaVantage API wrapper.
"""
import datetime
from datetime import timedelta
import os
import time
import requests
from .disk_io import glob_delete, json_from_file, write

DATA_PATH = '../data/alphavantage'

def daily(symbol, from_date="", to_date=""):
    """
    Returns dictionary of daily stock data. By default, returns 20-year
    span of results, ending on the most recent trading day.

    Arguments
      - symbol: ticker symbol of the equity (not case-sensitive)
      - from_date (optional): start date of returned results
      - to_date (optional): end date of returned results
    """
    if not "ALPHAVANTAGE_API_KEY" in os.environ:
        print('Error: ALPHAVANTAGE_API_KEY not set.')
        return
    symbol = symbol.upper()
    current_date = datetime.date.today().strftime('%Y-%m-%d')
    latest_file = f'{symbol}_{current_date}.json'
    glob_delete(DATA_PATH, f'{symbol}_*', latest_file)
    if not os.path.isfile(os.path.join(os.path.dirname(__file__), DATA_PATH, latest_file)):
        time.sleep(12)
        request = requests.get((f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}'
                                f"&outputsize=full&apikey={os.environ['ALPHAVANTAGE_API_KEY']}"))
        write(f'../data/alphavantage/{latest_file}', request.json())
    data = json_from_file(f'{DATA_PATH}/{latest_file}')['Time Series (Daily)']
    if from_date:
        data = {k: v for k, v in data.items() if datetime.datetime.strptime(k, '%Y-%m-%d') >= from_date}
    if to_date:
        data = {k: v for k, v in data.items() if datetime.datetime.strptime(k, '%Y-%m-%d') <= to_date}
    return data

def backward_from(symbol, num_days, from_date=datetime.datetime.today()):
    """
    Returns array of daily trading stats for a requested symbol for the requested number of trading
    days, backward from the specified date.
    Arguments
      - symbol: ticker symbol of the equity (not case-sensitive)
      - num_days: number of trading days to include, backward from the most recent day
    """
    start_date = from_date - timedelta(days=num_days)
    data = daily(symbol, start_date, from_date)
    days_diff = num_days - len(data.keys())
    max_attempts = 20
    num_attempts = 0
    len_data_prev = 0
    while days_diff > 0:
        start_date -= timedelta(days=days_diff)
        data = daily(symbol, start_date, from_date)
        len_data = len(data)
        days_diff = num_days - len_data
        num_attempts = num_attempts + 1 if len_data == len_data_prev else 0
        len_data_prev = len_data
        if num_attempts >= max_attempts:
            raise LookupError(f'Requested data range for {symbol} not available.')
    return_object = {}
    for date in sorted(data.keys()):
        return_object[date] = data[date]
    return return_object
