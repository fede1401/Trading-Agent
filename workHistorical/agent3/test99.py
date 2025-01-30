# import MetaTrader5 as mt5
import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical')


import agentState
from db import insertDataDB, connectDB
from utils import generateiRandomDates, getLastIdTest, clearSomeTablesDB, getValueMiddlePrice
from symbols import getSector, getSymbols
import psycopg2
import time
import random
import logging
import pytz
from datetime import datetime, time, timedelta
import time as time_module
import csv
import math
from dateutil.relativedelta import relativedelta
import pandas as pd
import traceback
import numpy as np



"""
def getSymbolsDispoible(cur, symbols, market, initial_date, endDate):
    try:
        # Recupero dei simboli azionari disponibili per le date di trading scelte. 
        cur.execute(f"SELECT distinct(symbol) FROM larg_comp_eu_actions WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
        # symbolDisp = [sy[0] for sy in resSymbolDisp if sy[0] in symbols]
        symbolDisp = []
        symb100 = symbols[0:100]
        for sy in cur.fetchall():
            if sy[0] in symbols:
                if len(symbolDisp) < 100:
                    if sy[0] in symb100:
                        symbolDisp.append(sy[0])
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return symbolDisp


cur, conn = connectDB.connect_nasdaq()            
symbols = getSymbols.getSymbolsLargestCompEU(350)


datesToTrade1 = [('1999-06-24 00:00:00', datetime(1999, 6, 24, 0, 0), '2000-06-24 00:00:00'), ('1999-07-16 00:00:00', datetime(1999, 7, 16, 0, 0), '2000-07-16 00:00:00'), ('1999-09-08 00:00:00', datetime(1999, 9, 8, 0, 0), '2000-09-08 00:00:00'), ('2001-08-08 00:00:00', datetime(2001, 8, 8, 0, 0), '2002-08-08 00:00:00'), ('2001-09-24 00:00:00', datetime(2001, 9, 24, 0, 0), '2002-09-24 00:00:00'), ('2001-09-24 00:00:00', datetime(2001, 9, 24, 0, 0), '2002-09-24 00:00:00'), ('2002-11-01 00:00:00', datetime(2002, 11, 1, 0, 0), '2003-11-01 00:00:00'), ('2002-11-18 00:00:00', datetime(2002, 11, 18, 0, 0), '2003-11-18 00:00:00'), ('2004-01-09 00:00:00', datetime(2004, 1, 9, 0, 0), '2005-01-09 00:00:00'), ('2004-08-18 00:00:00', datetime(2004, 8, 18, 0, 0), '2005-08-18 00:00:00'), ('2006-11-02 00:00:00', datetime(2006, 11, 2, 0, 0), '2007-11-02 00:00:00'), ('2006-11-15 00:00:00', datetime(2006, 11, 15, 0, 0), '2007-11-15 00:00:00'), ('2007-10-22 00:00:00', datetime(2007, 10, 22, 0, 0), '2008-10-22 00:00:00'), ('2008-12-05 00:00:00', datetime(2008, 12, 5, 0, 0), '2009-12-05 00:00:00'), ('2009-04-16 00:00:00', datetime(2009, 4, 16, 0, 0), '2010-04-16 00:00:00'), ('2009-10-20 00:00:00', datetime(2009, 10, 20, 0, 0), '2010-10-20 00:00:00'), ('2009-11-23 00:00:00', datetime(2009, 11, 23, 0, 0), '2010-11-23 00:00:00'), ('2010-07-16 00:00:00', datetime(2010, 7, 16, 0, 0), '2011-07-16 00:00:00'), ('2011-06-09 00:00:00', datetime(2011, 6, 9, 0, 0), '2012-06-09 00:00:00'), ('2011-07-28 00:00:00', datetime(2011, 7, 28, 0, 0), '2012-07-28 00:00:00'), ('2011-09-20 00:00:00', datetime(2011, 9, 20, 0, 0), '2012-09-20 00:00:00'), ('2012-11-19 00:00:00', datetime(2012, 11, 19, 0, 0), '2013-11-19 00:00:00'), ('2012-12-20 00:00:00', datetime(2012, 12, 20, 0, 0), '2013-12-20 00:00:00'), ('2013-03-01 00:00:00', datetime(2013, 3, 1, 0, 0), '2014-03-01 00:00:00'), ('2013-06-28 00:00:00', datetime(2013, 6, 28, 0, 0), '2014-06-28 00:00:00'), ('2013-08-12 00:00:00', datetime(2013, 8, 12, 0, 0), '2014-08-12 00:00:00'), ('2014-01-13 00:00:00', datetime(2014, 1, 13, 0, 0), '2015-01-13 00:00:00'), ('2014-01-21 00:00:00', datetime(2014, 1, 21, 0, 0), '2015-01-21 00:00:00'), ('2014-01-30 00:00:00', datetime(2014, 1, 30, 0, 0), '2015-01-30 00:00:00'), ('2015-03-04 00:00:00', datetime(2015, 3, 4, 0, 0), '2016-03-04 00:00:00'), ('2015-03-13 00:00:00', datetime(2015, 3, 13, 0, 0), '2016-03-13 00:00:00'), ('2015-03-16 00:00:00', datetime(2015, 3, 16, 0, 0), '2016-03-16 00:00:00'), ('2015-03-26 00:00:00', datetime(2015, 3, 26, 0, 0), '2016-03-26 00:00:00'), ('2015-04-28 00:00:00', datetime(2015, 4, 28, 0, 0), '2016-04-28 00:00:00'), ('2015-05-14 00:00:00', datetime(2015, 5, 14, 0, 0), '2016-05-14 00:00:00'), ('2015-09-15 00:00:00', datetime(2015, 9, 15, 0, 0), '2016-09-15 00:00:00'), ('2016-02-23 00:00:00', datetime(2016, 2, 23, 0, 0), '2017-02-23 00:00:00'), ('2016-03-18 00:00:00', datetime(2016, 3, 18, 0, 0), '2017-03-18 00:00:00'), ('2016-04-06 00:00:00', datetime(2016, 4, 6, 0, 0), '2017-04-06 00:00:00'), ('2016-10-06 00:00:00', datetime(2016, 10, 6, 0, 0), '2017-10-06 00:00:00'), ('2017-02-15 00:00:00', datetime(2017, 2, 15, 0, 0), '2018-02-15 00:00:00'), ('2017-03-15 00:00:00', datetime(2017, 3, 15, 0, 0), '2018-03-15 00:00:00'), ('2017-05-01 00:00:00', datetime(2017, 5, 1, 0, 0), '2018-05-01 00:00:00'), ('2017-08-14 00:00:00', datetime(2017, 8, 14, 0, 0), '2018-08-14 00:00:00'), ('2017-08-15 00:00:00', datetime(2017, 8, 15, 0, 0), '2018-08-15 00:00:00'), ('2017-08-16 00:00:00', datetime(2017, 8, 16, 0, 0), '2018-08-16 00:00:00'), ('2017-10-30 00:00:00', datetime(2017, 10, 30, 0, 0), '2018-10-30 00:00:00'), ('2018-02-14 00:00:00', datetime(2018, 2, 14, 0, 0), '2019-02-14 00:00:00'), ('2018-03-29 00:00:00', datetime(2018, 3, 29, 0, 0), '2019-03-29 00:00:00'), ('2018-05-14 00:00:00', datetime(2018, 5, 14, 0, 0), '2019-05-14 00:00:00'), ('2018-06-04 00:00:00', datetime(2018, 6, 4, 0, 0), '2019-06-04 00:00:00'), ('2018-08-09 00:00:00', datetime(2018, 8, 9, 0, 0), '2019-08-09 00:00:00'), ('2019-03-14 00:00:00', datetime(2019, 3, 14, 0, 0), '2020-03-14 00:00:00'), ('2019-05-03 00:00:00', datetime(2019, 5, 3, 0, 0), '2020-05-03 00:00:00'), ('2019-05-17 00:00:00', datetime(2019, 5, 17, 0, 0), '2020-05-17 00:00:00'), ('2019-06-17 00:00:00', datetime(2019, 6, 17, 0, 0), '2020-06-17 00:00:00'), ('2019-06-27 00:00:00', datetime(2019, 6, 27, 0, 0), '2020-06-27 00:00:00'), ('2020-01-10 00:00:00', datetime(2020, 1, 10, 0, 0), '2021-01-10 00:00:00'), ('2020-01-31 00:00:00', datetime(2020, 1, 31, 0, 0), '2021-01-31 00:00:00'), ('2020-03-27 00:00:00', datetime(2020, 3, 27, 0, 0), '2021-03-27 00:00:00'), ('2020-05-26 00:00:00', datetime(2020, 5, 26, 0, 0), '2021-05-26 00:00:00'), ('2020-05-27 00:00:00', datetime(2020, 5, 27, 0, 0), '2021-05-27 00:00:00'), ('2020-08-05 00:00:00', datetime(2020, 8, 5, 0, 0), '2021-08-05 00:00:00'), ('2020-08-17 00:00:00', datetime(2020, 8, 17, 0, 0), '2021-08-17 00:00:00'), ('2020-09-11 00:00:00', datetime(2020, 9, 11, 0, 0), '2021-09-11 00:00:00'), ('2020-10-21 00:00:00', datetime(2020, 10, 21, 0, 0), '2021-10-21 00:00:00'), ('2021-02-10 00:00:00', datetime(2021, 2, 10, 0, 0), '2022-02-10 00:00:00'), ('2021-03-30 00:00:00', datetime(2021, 3, 30, 0, 0), '2022-03-30 00:00:00'), ('2021-04-14 00:00:00', datetime(2021, 4, 14, 0, 0), '2022-04-14 00:00:00'), ('2021-07-08 00:00:00', datetime(2021, 7, 8, 0, 0), '2022-07-08 00:00:00'), ('2021-08-11 00:00:00', datetime(2021, 8, 11, 0, 0), '2022-08-11 00:00:00'), ('2021-08-12 00:00:00', datetime(2021, 8, 12, 0, 0), '2022-08-12 00:00:00'), ('2021-08-18 00:00:00', datetime(2021, 8, 18, 0, 0), '2022-08-18 00:00:00'), ('2021-10-28 00:00:00', datetime(2021, 10, 28, 0, 0), '2022-10-28 00:00:00'), ('2021-11-04 00:00:00', datetime(2021, 11, 4, 0, 0), '2022-11-04 00:00:00'), ('2021-11-04 00:00:00', datetime(2021, 11, 4, 0, 0), '2022-11-04 00:00:00'), ('2021-11-11 00:00:00', datetime(2021, 11, 11, 0, 0), '2022-11-11 00:00:00'), ('2021-12-28 00:00:00', datetime(2021, 12, 28, 0, 0), '2022-12-28 00:00:00'), ('2022-01-07 00:00:00', datetime(2022, 1, 7, 0, 0), '2023-01-07 00:00:00'), ('2022-02-08 00:00:00', datetime(2022, 2, 8, 0, 0), '2023-02-08 00:00:00'), ('2022-04-04 00:00:00', datetime(2022, 4, 4, 0, 0), '2023-04-04 00:00:00'), ('2022-05-10 00:00:00', datetime(2022, 5, 10, 0, 0), '2023-05-10 00:00:00'), ('2022-05-26 00:00:00', datetime(2022, 5, 26, 0, 0), '2023-05-26 00:00:00'), ('2022-06-15 00:00:00', datetime(2022, 6, 15, 0, 0), '2023-06-15 00:00:00'), ('2022-06-21 00:00:00', datetime(2022, 6, 21, 0, 0), '2023-06-21 00:00:00'), ('2022-10-17 00:00:00', datetime(2022, 10, 17, 0, 0), '2023-10-17 00:00:00'), ('2022-12-29 00:00:00', datetime(2022, 12, 29, 0, 0), '2023-12-29 00:00:00'), ('2023-01-09 00:00:00', datetime(2023, 1, 9, 0, 0), '2024-01-09 00:00:00'), ('2023-01-20 00:00:00', datetime(2023, 1, 20, 0, 0), '2024-01-20 00:00:00'), ('2023-03-03 00:00:00', datetime(2023, 3, 3, 0, 0), '2024-03-03 00:00:00'), ('2023-03-10 00:00:00', datetime(2023, 3, 10, 0, 0), '2024-03-10 00:00:00'), ('2023-03-22 00:00:00', datetime(2023, 3, 22, 0, 0), '2024-03-22 00:00:00'), ('2023-04-13 00:00:00', datetime(2023, 4, 13, 0, 0), '2024-04-13 00:00:00'), ('2023-04-20 00:00:00', datetime(2023, 4, 20, 0, 0), '2024-04-20 00:00:00'), ('2023-04-28 00:00:00', datetime(2023, 4, 28, 0, 0), '2024-04-28 00:00:00'), ('2023-05-24 00:00:00', datetime(2023, 5, 24, 0, 0), '2024-05-24 00:00:00'), ('2023-08-15 00:00:00', datetime(2023, 8, 15, 0, 0), '2024-08-15 00:00:00'), ('2023-08-24 00:00:00', datetime(2023, 8, 24, 0, 0), '2024-08-24 00:00:00'), ('2023-09-08 00:00:00', datetime(2023, 9, 8, 0, 0), '2024-09-08 00:00:00'), ('2023-10-25 00:00:00', datetime(2023, 10, 25, 0, 0), '2024-10-25 00:00:00')]


print(symbols, '\n')
for d in datesToTrade1:
    sres = getSymbolsDispoible(cur, symbols, 'nyse', d[0], d[2])
    print(d[0], d[2], sres, len(sres))
    
"""

"""
all_dates = ticker.quarterly_income_stmt.columns

#print(all_dates)
total_shares = ticker.quarterly_income_stmt['2024-09-30']['Basic Average Shares']


stock_price = ticker.history(start='2023-09-26', end='2023-09-26')
market_cap = stock_price * total_shares


# Dati di conto economico annuali
annual_financials = ticker.financials

# Visualizza le date (colonne) disponibili
print("Date disponibili (anni fiscali):", annual_financials.columns)

# Puoi elencare le voci (righe) disponibili
print("\nVoci disponibili:")
print(annual_financials.index)

# Esempio: estrarre 'Basic Average Shares' (se presente) per un anno specifico
# Supponendo che tra le colonne ci sia '2022-09-24', puoi fare:
basic_shares_2022 = annual_financials.loc['Basic Average Shares', '2022-09-24']
print("\nBasic Average Shares 2022:", basic_shares_2022)


import yfinance as yf

import pandas as pd

# 1. Definisci il ticker
symbol = "AAPL"  # Esempio: Apple
ticker = yf.Ticker(symbol)

# 2. Scarica i bilanci annuali (conto economico)
annual_financials = ticker.financials  # DataFrame con date (colonne) e voci (righe)
print("=== Bilancio Annuale: ===")
print(annual_financials)

# 3. Scarica i prezzi storici dal 1999 in poi
price_data = ticker.history(start="1999-01-01", end="2025-01-01")
# price_data è un DataFrame con indice = date, e colonne: Open, High, Low, Close, ...
# Di default sono prezzi giornalieri

print("\n=== Prezzi Storici (head): ===")
print(price_data.head())

# 4. Loop sulle colonne (che rappresentano fine anno fiscale)
market_caps = []  # Collezioniamo i risultati qui

for fiscal_date_str in annual_financials.columns:
    # Esempio: "2022-09-24"

    # Controllo se esiste la riga "Basic Average Shares" nel bilancio
    if "Basic Average Shares" in annual_financials.index:
        shares = annual_financials.loc["Basic Average Shares", fiscal_date_str]
    else:
        shares = None
    
    # Se shares è NaN o None, salto
    if shares is None or pd.isna(shares):
        continue
    
    # Converto la stringa della colonna in un oggetto datetime (pandas)
    fiscal_date = pd.to_datetime(fiscal_date_str)
    
    # 5. Trova un prezzo vicino a quella data nei dati storici
    # Potrebbe non esistere la riga esatta, usiamo nearest o forward/backfill
    # get_loc con method='nearest' può lanciare eccezioni se la data è fuori range, gestiamolo con try/except
    try:
        idx = price_data.index.get_loc(fiscal_date, method='nearest')
        nearest_date = price_data.index[idx]
    except KeyError:
        # Se fuori range, saltiamo
        continue
    
    # 6. Recupero il prezzo di chiusura (o adjusted close, se preferisci)
    # yfinance .history() di solito fornisce 'Close', 'Open', 'High', 'Low', 'Volume', 'Dividends', 'Stock Splits'
    # Se vuoi l'adjusted close puoi usare price_data['Close'] (in yfinance
    # spesso è già l'adjusted, dipende dalla versione). Per sicurezza controlla .info
    close_price = price_data.loc[nearest_date, "Close"]
    
    # 7. Calcolo la (pseudo) Market Cap
    # ATTENZIONE: "Basic Average Shares" è in genere un numero enorme (Apple: miliardi di azioni).
    # Spesso yfinance fornisce questi dati "già moltiplicati / in migliaia / in milioni".
    # Controlla i valori per evitare errori di scala.
    mc = close_price * shares
    
    # Salvo i risultati in un dict
    result = {
        "Fiscal Year End": fiscal_date_str,
        "Nearest Price Date": nearest_date.date(),
        "Basic Average Shares": shares,
        "Close Price": close_price,
        "Market Cap": mc
    }
    market_caps.append(result)

# 8. Creiamo un DataFrame con i risultati
mc_df = pd.DataFrame(market_caps)
mc_df.sort_values("Fiscal Year End", inplace=True)  # Ordina cronologicamente
print("\n=== (Pseudo) Market Cap su base annuale ===")
print(mc_df)
"""


#https://companiesmarketcap.com/apple/marketcap/


with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
    # Crea un lettore CSV con DictReader
    csv_reader = csv.DictReader(file)
    
    # Inizializza una lista vuota per memorizzare i simboli
    symbols = [col['Symbol'] for col in csv_reader]
    
# Ritorna la lista dei simboli
print(symbols)