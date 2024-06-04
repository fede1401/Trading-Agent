# Raccolta dei dati e inserimento nel database postgreSQL.

import MetaTrader5 as mt5
from datetime import datetime
import login_mt5, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send
import psycopg2
import time
import numpy as np


# Specificare il simbolo dell'azione (ad esempio, 'AAPL' per Apple, 'NFLX' per Netflix)
symbols = ['MSFT', 'AAPL', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX', 'AMD', 'AZN', 'PEP', 
           'QCOM', 'TMUS', 'PDD', 'ADBE', 'CSCO', 'AMAT', 'AMGN', 'CMCSA', 'ISRG', 'MU',
           'INTC', 'BKNG', 'LRCX', 'VRTX']


# Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri)
timeframe = mt5.TIMEFRAME_M1


def main():
    login_mt5.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

    # Specificare l'intervallo di tempo di cui prendere i dati
    start_date = datetime(2024, 5, 28)
    end_date = datetime.now()

    while (True):
    
        for symbol in symbols:
            print(symbol)
            # verifico se il simbolo è esistente ed è presente nel MarketWatch, se non lo è lo aggiungo
            info_order_send.checkSymbol(symbol)

            # scarico i dati tramite la funzione copy_rates_range e li inserisco nel database
            downloadAndInsertDataDB.downloadInsertDB_data(symbol, timeframe, start_date, end_date)


        print("\nsleep!\n")
        print(datetime.now())
        
        # sleep di 1 minuto
        time.sleep(60)

        start_date = end_date
        end_date = datetime.now()
        print(f"\nStart date: {start_date}\n")
        print(f"End date: {end_date}\n")


    closeConnectionMt5.closeConnection()
    return 



if __name__ == '__main__':
    
    main()
