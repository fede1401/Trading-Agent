from datetime import datetime, timedelta
import psycopg2 
import numpy as np
#import db.connectDB as connectDB
import logging
#import MetaTrader5 as mt5


# Funzione per convertire tipi di dati numpy in tipi di dati Python
def convert_numpy_to_python(value):
    if isinstance(value, np.generic):
        return value.item() # Restituisce un valore scalare dal tipo numpy
    return value # Restituisce direttamente il valore se non è di tipo numpy

################################################################################################

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
        finally:
            # Chiude la connessione al database
            cur.close()
            


################################################################################################


# Funzione per inserire i dati dei titoli azionari del NASDAQ scaricati con Yahoo!Finance nel database
def insertInNasdaqFromYahoo(symbol, time_frame, rate, cur, conn):
    try:
            # Calcola il tempo in formato italiano (sottrae 3 ore dall'orario UNIX)
            #time_value_it = datetime.fromtimestamp(rate['time']) - timedelta(hours=3)

            # Calcola il tempo in formato newyorkese (sottrae 9 ore dall'orario UNIX)
            #time_value_ny = datetime.fromtimestamp(rate['time']) - timedelta(hours=9)

            # Esegue l'inserimento nella tabella nasdaq_actions
            cur.execute(
                "INSERT INTO nasdaq_actions (symbol, time_frame, time_value_IT, time_value_NY, open_price, high_price, low_price, close_price, tick_volume, spread, real_volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value_IT, time_value_NY, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.strptime(rate[7], '%Y-%m-%d %H:%M:%S'),
                    datetime.strptime(rate[8], '%Y-%m-%d %H:%M:%S'),
                    convert_numpy_to_python(rate[0]),
                    convert_numpy_to_python(rate[1]),
                    convert_numpy_to_python(rate[2]),
                    convert_numpy_to_python(rate[3]),
                    convert_numpy_to_python(rate[4]),
                    convert_numpy_to_python(rate[5]),
                    convert_numpy_to_python(rate[6])
                )
            )        
            
    except Exception as e:
        print("Errore durante l'inserimento dei dati: ", e)
    
    # Conferma la transazione e stampa un messaggio
    conn.commit()
    
    print(f"Dati relativi al salvataggio di {symbol} nella data: {datetime.strptime(rate[7], '%Y-%m-%d %H:%M:%S')} salvati nel db.\n")
    
    return 0

################################################################################################################################################################################################

# Funzione per inserire i dati dei titoli azionari del NYSE scaricati con Yahoo!Finance nel database
def insertInNyseFromYahoo(symbol, time_frame, rate, cur, conn):
    try:
            # Calcola il tempo in formato italiano (sottrae 3 ore dall'orario UNIX)
            #time_value_it = datetime.fromtimestamp(rate['time']) - timedelta(hours=3)

            # Calcola il tempo in formato newyorkese (sottrae 9 ore dall'orario UNIX)
            #time_value_ny = datetime.fromtimestamp(rate['time']) - timedelta(hours=9)

            # Esegue l'inserimento nella tabella nasdaq_actions
            cur.execute(
                "INSERT INTO nyse_actions (symbol, time_frame, time_value_IT, time_value_NY, open_price, high_price, low_price, close_price, tick_volume, spread, real_volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value_IT, time_value_NY, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.strptime(rate[7], '%Y-%m-%d %H:%M:%S'),
                    datetime.strptime(rate[8], '%Y-%m-%d %H:%M:%S'),
                    convert_numpy_to_python(rate[0]),
                    convert_numpy_to_python(rate[1]),
                    convert_numpy_to_python(rate[2]),
                    convert_numpy_to_python(rate[3]),
                    convert_numpy_to_python(rate[4]),
                    convert_numpy_to_python(rate[5]),
                    convert_numpy_to_python(rate[6])
                )
            )        
            
    except Exception as e:
        print("Errore durante l'inserimento dei dati: ", e)
    
    # Conferma la transazione e stampa un messaggio
    conn.commit()
    
    print(f"Dati relativi al salvataggio di {symbol} nella data: {datetime.strptime(rate[7], '%Y-%m-%d %H:%M:%S')} salvati nel db.\n")
    
    return 0


################################################################################################################################################################################################


# Funzione per inserire i dati dei titoli azionari del NYSE scaricati con Yahoo!Finance nel database
def insertInLargeCompEUFromYahoo(symbol, time_frame, rate, cur, conn):
    try:
            # Calcola il tempo in formato italiano (sottrae 3 ore dall'orario UNIX)
            #time_value_it = datetime.fromtimestamp(rate['time']) - timedelta(hours=3)

            # Calcola il tempo in formato newyorkese (sottrae 9 ore dall'orario UNIX)
            #time_value_ny = datetime.fromtimestamp(rate['time']) - timedelta(hours=9)

            # Esegue l'inserimento nella tabella nasdaq_actions
            cur.execute(
                "INSERT INTO larg_comp_eu_actions (symbol, time_frame, time_value_IT, time_value_NY, open_price, high_price, low_price, close_price, tick_volume, spread, real_volume) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, time_value_IT, time_value_NY, time_frame) DO NOTHING",
                (
                    symbol,
                    time_frame,
                    datetime.strptime(rate[7], '%Y-%m-%d %H:%M:%S'),
                    datetime.strptime(rate[8], '%Y-%m-%d %H:%M:%S'),
                    convert_numpy_to_python(rate[0]),
                    convert_numpy_to_python(rate[1]),
                    convert_numpy_to_python(rate[2]),
                    convert_numpy_to_python(rate[3]),
                    convert_numpy_to_python(rate[4]),
                    convert_numpy_to_python(rate[5]),
                    convert_numpy_to_python(rate[6])
                )
            )        
            
    except Exception as e:
        print("Errore durante l'inserimento dei dati: ", e)
    
    # Conferma la transazione e stampa un messaggio
    conn.commit()
    
    print(f"Dati relativi al salvataggio di {symbol} nella data: {datetime.strptime(rate[7], '%Y-%m-%d %H:%M:%S')} salvati nel db.\n")
    
    return 0

################################################################################################################################################################################################

# Funzione per inserire un acquisto di un simbolo azionario nel database
def insertInPurchase (date, ticket, volume, symbol, price, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella Purchase
            cur.execute(
                "INSERT INTO Purchase (datePur, now, ticket, volume, symbol, price) "
                "VALUES (%s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (datePur, now, symbol) DO NOTHING",
                (
                    date,
                    datetime.now(),
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
            
        #print("Dati relative all'acquisto dell'azione salvati nel db.\n")

        
################################################################################################################################################################################################


# Funzione per inserire una vendita (chiusura di una posizione) di un simbolo azionario nel database
def insertInSale (dateSal, datePur, ticket_pur, ticket_sale, volume, symbol, priceSale, pricePurchase, profitUSD, profitPerc, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella Sale
            cur.execute(
                "INSERT INTO Sale (dateSal, datePur, now, ticket_pur, ticket_sale, volume, symbol, priceSale, pricePurchase, profit_USD, profit_Perc)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (dateSal, now, symbol) DO NOTHING",
                (
                    dateSal,
                    datePur,
                    datetime.now(),
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
            
        #print("Dati relativi alla vendita dell'azione salvati nel db.\n")

       
################################################################################################################################################################################################ 


# Funzione per inserire dati relativi allo stato del trader nel database
def insertInDataTrader(date, stateAg, initialBalance, balance, equity, margin, profitUSD, profitPerc, deposit, credit, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella DataTrader
            cur.execute(
                "INSERT INTO DataTrader (date, now, stAgent, initialBalance, balance, equity, margin, profitUSD, profitPerc, deposit, credit) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ",
                (
                    date,
                    datetime.now(),
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
            
        #print("Dati relativi allo stato del trader salvati nel db.\n")
        

################################################################################################################################################################################################


# Funzione per inserire dati relativi al login dell'utente nel database
def insertInLoginDate(nameSurname, username, server, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
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
            
        #print("Dati relativi al login dell'utente salvati nel db.\n")
        

################################################################################################################################################################################################


def insertInSector(nome, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
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


################################################################################################################################################################################################


def insertInTesting(id, agent, numberTest, initial_date, end_date, profit, market, notes, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella loginDate
            cur.execute(
                "INSERT INTO Testing (id, agent, numberTest, initial_date, end_date, profit, market, notes) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s ) ",
                (
                    convert_numpy_to_python(id),
                    agent, 
                    convert_numpy_to_python(numberTest),
                    initial_date, 
                    end_date,
                    convert_numpy_to_python(profit),
                    market,
                    notes
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        #print("Dati relativi al  salvati nel db.\n")


################################################################################################################################################################################################


def insertInMiddleProfit(testId, agent, middleProfit, devst, notes, cur, conn):
    if cur is not None and conn is not None:
        #print("\nConnessione al database nasdaq avvenuta con successo.\n")
        
        try:
            # Esegue l'inserimento nella tabella loginDate
            cur.execute(
                "INSERT INTO MiddleProfit (testId, agent, middleProfit, devstandard, notes) "
                "VALUES (%s, %s, %s, %s, %s) ",
                (
                    convert_numpy_to_python(testId),
                    agent, 
                    convert_numpy_to_python(middleProfit),
                    convert_numpy_to_python(devst),
                    notes
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        
        # Conferma la transazione e stampa un messaggio
        conn.commit()
            
        #print("Dati relativi al  salvati nel db.\n")


################################################################################################################################################################################################