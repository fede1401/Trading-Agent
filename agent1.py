# Raccolta dei dati e inserimento nel database postgreSQL.

import MetaTrader5 as mt5
from datetime import datetime
import login, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send, symbolsAcceptedByTickmill
import psycopg2
import time
import numpy as np
import logging


"""
Ecco alcune possibili cause per cui non vengono selezionati tutti i dati se l'intervallo di tempo è superiore a 2 anni:

- Limitazioni del Server del Broker: Il server del broker potrebbe non essere in grado di restituire 
    tutti i dati richiesti in un'unica chiamata se l'intervallo di tempo è troppo lungo.
- Limitazioni dell'API di MT5: L'API di MT5 potrebbe avere limiti sulla quantità di dati che 
    può restituire in una singola chiamata.
- Problemi di Prestazioni: Richiedere troppi dati in una sola volta può causare problemi di prestazioni, 
    sia sul lato del client che del server.

"""


def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Inizio del trading agent 1.")
    
    try:
        login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

        # ottenimento delle azioni del Nasdaq accettate dal broker TickMill.
        symbols = symbolsAcceptedByTickmill.getSymbolsAcceptedByTickmill()
        
        # Specificare l'intervallo di tempo di cui prendere i dati:
            # da un'analisi ho notato che dall'inizio della nascita dell'indice NASDAQ Composite fino al 2017/09/18 i dati ci sono ogni giorno, 
            # dopo di che è necessario specificare un intervallo ogni 2 anni altrimenti non vengono trovati i dati
        #start_date = datetime(1971, 2, 8) # nascita indice NASDAQ composite
        #end_date = datetime(2017, 9, 18)

        for symbol in symbols:
            logging.info(f"Processing symbol: {symbol}")

            info_order_send.checkSymbol(symbol)
                
            logging.info("Scaricamento dati 1 !\n")

            # Scarico i dati tramite la funzione copy_rates_range e li inserisco nel database
            downloadAndInsertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_D1, datetime(1971, 2, 8), datetime(2017, 9, 18))
            downloadAndInsertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, datetime(2017, 9, 18), datetime(2020, 1, 1))
            downloadAndInsertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, datetime(2020, 1, 1), datetime(2022, 1, 1))


        while True:
            start_date = datetime(2022, 1, 1)
            end_date = datetime.now()
            
            for symbol in symbols:
                logging.info(f"Processing symbol: {symbol}")

                info_order_send.checkSymbol(symbol)
                
                logging.info("Scaricamento dati !\n")
                # Scarico i dati tramite la funzione copy_rates_range e li inserisco nel database
                downloadAndInsertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, start_date, end_date)

                
            logging.info("Dormi per un giorno.")
            logging.info(f"Start date: {start_date}")
            logging.info(f"End date: {end_date}")
            
            # sleep di 1 giornoATA
            time.sleep(86400)

            start_date = end_date
            end_date = datetime.now()
            
    except Exception as e:
        logging.critical(f"Uncaught exception: {e}")
    finally:
        closeConnectionMt5.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")



if __name__ == '__main__':

    # Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri, mt5.TIMEFRAME_M15 ogni 15 minuti)
    #timeframe = mt5.TIMEFRAME_M15

    #login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

    #downloadAndInsertDataDB.downloadInsertDB_data("AAPL", mt5.TIMEFRAME_D1, datetime(1971, 2, 8), datetime(2017, 9, 18))
    #downloadAndInsertDataDB.downloadInsertDB_data("AAPL", mt5.TIMEFRAME_M15, datetime(2017, 9, 18), datetime(2020, 1, 1))
    #downloadAndInsertDataDB.downloadInsertDB_data("AAPL", mt5.TIMEFRAME_M15, datetime(2020, 1, 1), datetime(2022, 1, 1))
    #downloadAndInsertDataDB.downloadInsertDB_data("AAPL", mt5.TIMEFRAME_M15, datetime(2022, 1, 1), datetime.now())

    #rates = mt5.copy_rates_range("AAPL", mt5.TIMEFRAME_M15, datetime(2018, 10, 1), datetime(2018, 10, 30))
    #print(rates)
    
    main()
