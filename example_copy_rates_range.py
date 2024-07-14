
import MetaTrader5 as mt5
from datetime import datetime
import login, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send, symbolsAcceptedByTickmill
import psycopg2
import time
import numpy as np
import logging



if __name__ == '__main__':

    # Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri, mt5.TIMEFRAME_M15 ogni 15 minuti)
    timeframe = mt5.TIMEFRAME_M1

    login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)
    symbol = 'AAPL'

    start_date = datetime(2024, 7, 8)
    end_date = datetime(2024, 7, 9)


    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date) 
    print()

    for rate in rates:
        print(rate)
        print(datetime.fromtimestamp(rate['time']))
    
    
    
