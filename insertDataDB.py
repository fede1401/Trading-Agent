import MetaTrader5 as mt5
from datetime import datetime
import psycopg2 
import numpy as np
import closeConnectionMt5, login, connectDB, downloadData


# Funzione per convertire numpy types in Python types
def convert_numpy_to_python(value):
    if isinstance(value, np.generic):
        return value.item()  # Usa .item() per ottenere un valore scalare
    return value



def insertInPurchase (date, ticket, volume, symbol, price, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq_actions avvenuta con successo.\n\n\n")
        
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
            
        print("Dati salvati nel db.\n\n\n")
        #cur.close()
        #conn.close()



def insertInSale (date, ticket, volume, symbol, priceSale, pricePurchase, profitUSD, profitPerc, time_for_profit, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq_actions avvenuta con successo.\n\n\n")
        
        try:
            cur.execute(
                "INSERT INTO Sale (date, ticket, volume, symbol, priceSale, pricePurchase, profitUSD, profitPerc, time_for_profit)"
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (date, symbol) DO NOTHING",
                (
                    date,
                    ticket,
                    convert_numpy_to_python(volume), 
                    symbol,
                    convert_numpy_to_python(priceSale),
                    convert_numpy_to_python(pricePurchase),
                    convert_numpy_to_python(profitUSD),
                    convert_numpy_to_python(profitPerc),
                    convert_numpy_to_python(time_for_profit)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        

        conn.commit()
            
        print("Dati salvati nel db.\n\n\n")
        #cur.close()
        #conn.close()



def insertInDataTrader(date, stateAg, initialBalance, balance, profitUSD, profitPerc, deposit, credit, cur, conn):
    if cur is not None and conn is not None:
        print("\nConnessione al database nasdaq_actions avvenuta con successo.\n\n\n")
        
        try:
            cur.execute(
                "INSERT INTO DataTrader (date, stAgent, initialBalance, balance, profitUSD, profitPerc, deposit, credit) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (date) DO NOTHING",
                (
                    date,
                    stateAg.name, 
                    convert_numpy_to_python(initialBalance),
                    convert_numpy_to_python(balance),
                    convert_numpy_to_python(profitUSD),
                    convert_numpy_to_python(profitPerc),
                    convert_numpy_to_python(deposit),
                    convert_numpy_to_python(credit)
                )
            )
        except Exception as e:
            print("Errore durante l'inserimento dei dati: ", e)
        

        conn.commit()
            
        print("Dati salvati nel db.\n\n\n")
        #cur.close()
        #conn.close()
