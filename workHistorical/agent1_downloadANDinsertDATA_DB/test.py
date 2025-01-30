import yfinance as yf
import os
import fnmatch
import pandas as pd
#import db.insertDataDB as db, db.connectDB as connectDB
import logging
from datetime import datetime, time, timedelta

import sys

from pathlib import Path

# Trova dinamicamente la cartella Trading-Agent e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'Trading-Agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

# Ora possiamo importare `config`
from config import project_root, db_path as db, symbols_path as symbols, market_data_path

print(f"Project Root: {project_root}")  # Debugging
from db import insertDataDB as db, connectDB  as connectDB
from symbols import getSymbols as getSymbols



df = yf.download(
    tickers='AAPL',
    start='2022-01-02',
    end='2022-01-10',
    interval='1d',
    auto_adjust=False
)

#print(df[['Open','High','Low','Close']])

print(df)