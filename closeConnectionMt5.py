# closeConnectionMt5.py

import MetaTrader5 as mt5
from datetime import datetime


def closeConnection():
    # Chiudere la connessione
    mt5.shutdown()
    print("Connessione chiusa")
