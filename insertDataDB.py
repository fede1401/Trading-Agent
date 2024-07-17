import MetaTrader5 as mt5
from datetime import datetime, timedelta
import psycopg2 
import numpy as np
import closeConnectionMt5, login, connectDB, downloadData
import logging



# Funzione per convertire numpy types in Python types
def convert_numpy_to_python(value):
    if isinstance(value, np.generic):
        return value.item()  # Usa .item() per ottenere un valore scalare
    return value


def insertInNasdaqActions(symbol, time_frame, rates, cur):
    for rate in rates:
        print(rate)
        try:
            # Sottrai 3 ore da rate['time'] per l'orario italiano
            time_value_it = datetime.fromtimestamp(rate['time']) - timedelta(hours=3)

            # Sottrai 7 ore da rate['time'] per l'orario new yorkese
            time_value_ny = datetime.fromtimestamp(rate['time']) - timedelta(hours=9)


            cur.execute(
                "INSERT INTO nasdaq_actions (symbol, time_frame, time_value_IT, time_value_NY, open_price, high_price, low_price, close_price, tick_volume, spread, real_volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value_IT, time_value_NY, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    time_value_it,
                    time_value_ny,
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



def downloadInsertDB_data(symbol, timeframe, start_date, end_date, cur, conn):
    # Ottenere i dati storici
    logging.info("Entrato nel metodo")
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

    # Controllare se abbiamo ottenuto i dati
    if rates is None:
        print("No data retrieved")
    else:

        if cur is not None and conn is not None:
            print("\nConnessione al database nasdaq_actions avvenuta con successo.\n")
            insertInNasdaqActions(symbol, timeframe, rates, cur)
            conn.commit()
            
            print("Dati relativi al salvtaggio dello storico salvati nel db.\n")
            
    return True





def insertInPurchase (date, ticket, volume, symbol, price, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            cur.execute(
                "INSERT INTO Purchase (date, ticket, volume, symbol, price) "
                "VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT (date, symbol) DO NOTHING",
                (
                    date,
                    ticket,
                    convert_numpy_to_python(volume),
                    symbol,
                    convert_numpy_to_python(price)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        

        conn.commit()
            
        print("Dati relative all'acquisto dell'azione salvati nel db.\n")
        



def insertInSale (date, ticket_pur, ticket_sale, volume, symbol, priceSale, pricePurchase, profitUSD, profitPerc, lossUSD, lossPerc, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            cur.execute(
                "INSERT INTO Sale (date, ticket_pur, ticket_sale, volume, symbol, priceSale, pricePurchase, profit_USD, profit_Perc, loss_USD, loss_Perc)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (date, symbol) DO NOTHING",
                (
                    date,
                    ticket_pur,
                    ticket_sale,
                    convert_numpy_to_python(volume), 
                    symbol,
                    convert_numpy_to_python(priceSale),
                    convert_numpy_to_python(pricePurchase),
                    convert_numpy_to_python(profitUSD),
                    convert_numpy_to_python(profitPerc),
                    convert_numpy_to_python(lossUSD),
                    convert_numpy_to_python(lossPerc)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        

        conn.commit()
            
        print("Dati relativi alla vendita dell'azione salvati nel db.\n")
        


def insertInDataTrader(date, stateAg, initialBalance, balance, profitUSD, profitPerc, lossUSD, lossPerc, deposit, credit, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            cur.execute(
                "INSERT INTO DataTrader (date, stAgent, initialBalance, balance, profitUSD, profitPerc, lossUSD, lossPerc, deposit, credit) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (date) DO NOTHING",
                (
                    date,
                    stateAg.name, 
                    convert_numpy_to_python(initialBalance),
                    convert_numpy_to_python(balance),
                    convert_numpy_to_python(profitUSD),
                    convert_numpy_to_python(profitPerc),
                    convert_numpy_to_python(lossUSD),
                    convert_numpy_to_python(lossPerc),
                    convert_numpy_to_python(deposit),
                    convert_numpy_to_python(credit)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        

        conn.commit()
            
        print("Dati relativi allo stato del trader salvati nel db.\n")
        



def insertInLoginDate(nameSurname, username, server, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            cur.execute(
                "INSERT INTO loginDate (date, nameSurname, username, serverr) "
                "VALUES (%s, %s, %s, %s) "
                "ON CONFLICT (date, username) DO NOTHING",
                (
                    datetime.now(),
                    nameSurname,
                    username,
                    server
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        

        conn.commit()
            
        print("Dati relativi al login dell'utente salvati nel db.\n")
        

