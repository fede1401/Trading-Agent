
import MetaTrader5 as mt5
from datetime import datetime
import psycopg2 
import numpy as np
import closeConnectionMt5, login, connectDB, downloadData
import logging



# Funzione per convertire numpy types in Python types
def convert_numpy_to_python(value):
    if isinstance(value, np.generic):
        return value.item()  # Usa .item() per ottenere un valore scalare
    return value



def insert_data(symbol, time_frame, rates, cur):
    for rate in rates:
        print(rate)
        try:
            cur.execute(
                "INSERT INTO nasdaq_actions (symbol, time_frame, time_value, open_price, high_price, low_price, close_price, tick_volume, spread, real_volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.fromtimestamp(rate['time']),
                    convert_numpy_to_python(rate['open']),
                    convert_numpy_to_python(rate['high']),
                    convert_numpy_to_python(rate['low']),
                    convert_numpy_to_python(rate['close']),
                    convert_numpy_to_python(rate['tick_volume']),
                    convert_numpy_to_python(rate['spread']),
                    convert_numpy_to_python(rate['real_volume'])
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)



def downloadInsertDB_data(symbol, timeframe, start_date, end_date):
    # Ottenere i dati storici
    logging.info("Entrato nel metodo")
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

    # Controllare se abbiamo ottenuto i dati
    if rates is None:
        print("No data retrieved")
    else:
        # Connettersi al database
        cur, conn = connectDB.connect_nasdaq()
        if cur is not None and conn is not None:
            print("\nConnessione al database nasdaq_actions avvenuta con successo.\n\n\n")
            insert_data(symbol, timeframe, rates, cur)
            conn.commit()
            
            print("Dati salvati nel db.\n\n\n")
            cur.close()
            conn.close()

    return True
