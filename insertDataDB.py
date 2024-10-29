from datetime import datetime, timedelta
import psycopg2 
import numpy as np
import connectDB
import logging
#import MetaTrader5 as mt5



# Funzione per convertire tipi di dati numpy in tipi di dati Python
def convert_numpy_to_python(value):
    if isinstance(value, np.generic):
        return value.item() # Restituisce un valore scalare dal tipo numpy
    return value # Restituisce direttamente il valore se non è di tipo numpy


# Funzione per inserire i dati delle azioni NASDAQ nel database
def insertInNasdaqActions(symbol, time_frame, rates, cur):
    for rate in rates:
        print(rate)
        try:
            # Calcola il tempo in formato italiano (sottrae 3 ore dall'orario UNIX)
            time_value_it = datetime.fromtimestamp(rate['time']) - timedelta(hours=3)

            # Calcola il tempo in formato newyorkese (sottrae 9 ore dall'orario UNIX)
            time_value_ny = datetime.fromtimestamp(rate['time']) - timedelta(hours=9)

            # Esegue l'inserimento nella tabella nasdaq_actions
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


# Funzione per scaricare i dati storici e inserirli nel database
def downloadInsertDB_data(symbol, timeframe, start_date, end_date, cur, conn):
    # Ottiene i dati storici dal MetaTrader5
    logging.info("Entrato nel metodo")
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

    # Controllare se abbiamo ottenuto i dati
    if rates is None:
        print("No data retrieved")
    else:
        # Se ci sono dati, li inserisce nel database
        if cur is not None and conn is not None:
            print("\nConnessione al database nasdaq_actions avvenuta con successo.\n")
            insertInNasdaqActions(symbol, timeframe, rates, cur)
            conn.commit()
            
            print("Dati relativi al salvtaggio dello storico salvati nel db.\n")
            
    return True




# Funzione per inserire un acquisto di un simbolo azionario nel database
def insertInPurchase (date, ticket, volume, symbol, price, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella Purchase
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
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        print("Dati relative all'acquisto dell'azione salvati nel db.\n")
        


# Funzione per inserire una vendita (chiusura di una posizione) di un simbolo azionario nel database
def insertInSale (date, ticket_pur, ticket_sale, volume, symbol, priceSale, pricePurchase, profitUSD, profitPerc, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella Sale
            cur.execute(
                "INSERT INTO Sale (date, ticket_pur, ticket_sale, volume, symbol, priceSale, pricePurchase, profit_USD, profit_Perc)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
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
                    convert_numpy_to_python(profitPerc)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        print("Dati relativi alla vendita dell'azione salvati nel db.\n")
        

# Funzione per inserire dati relativi allo stato del trader nel database
def insertInDataTrader(date, stateAg, initialBalance, balance, equity, margin, profitUSD, profitPerc, deposit, credit, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella DataTrader
            cur.execute(
                "INSERT INTO DataTrader (date, stAgent, initialBalance, balance, equity, margin, profitUSD, profitPerc, deposit, credit) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ",
                (
                    date,
                    stateAg.name, 
                    convert_numpy_to_python(initialBalance),
                    convert_numpy_to_python(balance),
                    convert_numpy_to_python(equity),
                    convert_numpy_to_python(margin),
                    convert_numpy_to_python(profitUSD),
                    convert_numpy_to_python(profitPerc),
                    convert_numpy_to_python(deposit),
                    convert_numpy_to_python(credit)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        print("Dati relativi allo stato del trader salvati nel db.\n")
        


# Funzione per inserire dati relativi al login dell'utente nel database
def insertInLoginDate(nameSurname, username, server, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella loginDate
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
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        print("Dati relativi al login dell'utente salvati nel db.\n")
        


def insertInSector(nome, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella loginDate
            cur.execute(
                "INSERT INTO Sector (nome) "
                "VALUES (%s) "
                "ON CONFLICT (nome) DO NOTHING",
                (
                    nome,
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        print("Dati relativi al  salvati nel db.\n")
