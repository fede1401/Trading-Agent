# Raccolta dei dati e inserimento nel database postgreSQL.

import MetaTrader5 as mt5
from datetime import datetime
import login, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send, symbolsAcceptedByTickmill
import psycopg2
import time
import numpy as np
import logging


# Specificare il simbolo dell'azione (ad esempio, 'AAPL' per Apple, 'NFLX' per Netflix)
symbols = symbolsAcceptedByTickmill.getSymbolsAcceptedByTickmill()


# Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri, mt5.TIMEFRAME_M15 ogni 15 minuti)
timeframe = mt5.TIMEFRAME_M15


# def main():
#     login_mt5.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

#     # Specificare l'intervallo di tempo di cui prendere i dati
#     start_date = datetime(1971, 2, 8) # nascita indice nasdaq composite contenente tutte le azioni di tutte le società quotate in borsa nasdaq.
#     end_date = datetime.now()

#     while (True):
    
#         for symbol in symbols:
#             print(symbol)
#             # verifico se il simbolo è esistente ed è presente nel MarketWatch, se non lo è lo aggiungo
#             info_order_send.checkSymbol(symbol)

#             # scarico i dati tramite la funzione copy_rates_range e li inserisco nel database
#             downloadAndInsertDataDB.downloadInsertDB_data(symbol, timeframe, start_date, end_date)


#         print("\nsleep!\n")
#         print(datetime.now())
        
#         # sleep di 1 giorno
#         time.sleep(86400)

#         start_date = end_date
#         end_date = datetime.now()
#         print(f"\nStart date: {start_date}\n")
#         print(f"End date: {end_date}\n")


#     closeConnectionMt5.closeConnection()
#     return 

def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Inizio del trading agent 1.")
    
    try:
        login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

        # Specificare l'intervallo di tempo di cui prendere i dati
        start_date = datetime(1971, 2, 8) # nascita indice NASDAQ composite
        end_date = datetime.now()

        while True:
            for symbol in symbols:
                logging.info(f"Processing symbol: {symbol}")
                
                # Verifico se il simbolo è esistente ed è presente nel MarketWatch, se non lo è lo aggiungo
                if not info_order_send.checkSymbol(symbol):
                    logging.warning(f"Symbol {symbol} not found, skipping.")
                    continue

                try:
                    # Scarico i dati tramite la funzione copy_rates_range e li inserisco nel database
                    downloadAndInsertDataDB.downloadInsertDB_data(symbol, timeframe, start_date, end_date)
                except Exception as e:
                    logging.error(f"Error downloading data for symbol {symbol}: {e}")
                
            logging.info("Dormi per un giorno.")
            logging.info(f"Start date: {start_date}")
            logging.info(f"End date: {end_date}")
            
            # sleep di 1 giorno
            time.sleep(86400)

            start_date = end_date
            end_date = datetime.now()
            
    except Exception as e:
        logging.critical(f"Uncaught exception: {e}")
    finally:
        closeConnectionMt5.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")



if __name__ == '__main__':
    
    main()
