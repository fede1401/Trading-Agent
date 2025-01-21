import yfinance as yf
import os
import fnmatch
import pandas as pd
#import db.insertDataDB as db, db.connectDB as connectDB
import logging
from datetime import datetime, time, timedelta
import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')
from db import insertDataDB as db, connectDB  as connectDB

from symbols import getSymbols as getSymbols
from pathlib import Path



df = yf.download(
    tickers='AAPL',
    start='2022-01-02',
    end='2022-01-10',
    interval='1d',
    auto_adjust=False
)

#print(df[['Open','High','Low','Close']])

print(df)