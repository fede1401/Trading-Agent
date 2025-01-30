"""
    element = driver.find_element(by=By.XPATH, value='//*[@id="search-input"]' ) 
    element.send_keys("AAPL")    
    element.submit()
    time.sleep(1) 
"""

"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv


with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:

    # Crea un lettore CSV con DictReader
    csv_reader = csv.DictReader(file)
    
    symbols = [col['Symbol'] for col in csv_reader]


# (Opzionale) Imposta il path a chromedriver se non è nel PATH
chrome_driver_path = "/Users/federico/Documents/chromedriver-mac-arm64/chromedriver"

# Crea un oggetto Service per ChromeDriver
service = Service(executable_path=chrome_driver_path)

# (Opzionale) Imposta opzioni per Chrome, ad es. aprirlo in modalità headless
options = webdriver.ChromeOptions()

# Avvia il browser
driver = webdriver.Chrome(service=service, options=options)

diz = {}
symbolNotFound = []

try:
    driver.get("https://companiesmarketcap.com")
    # Attendi la presenza del pulsante e clicca per chiudere il banner    
    spam = driver.find_element(by=By.XPATH, value='//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]' ) 
    spam.click()
    
    for sy in symbols:
    
        #search_box = wait.until(EC.presence_of_element_located((By.ID, "search-input")))
        search_box = driver.find_element(by=By.ID, value='search-input')
        search_box.click()
        search_box.clear()
        search_box.send_keys(sy)
        
        time.sleep(1)
        
        try:
            clickable = driver.find_element(by=By.XPATH, value='//*[@id="typeahead-search-results"]/a')
            clickable.click()
        except Exception as e:
            symbolNotFound.append(sy)
            continue
        
        time.sleep(1)

        try:
            spam2 = driver.find_element(by=By.XPATH, value='//*[@id="dismiss-button"]/div/svg/path[1]' )
            spam2.click()
        except Exception as e:
            pass  # nessun banner
        
        table = driver.find_element(by=By.XPATH, value='//*[@id="cmkt"]/div[3]/div[2]/div[3]/table')
        rows = table.find_elements(by=By.TAG_NAME, value='tr')
        
        # 3. Itera sulle righe
        all_data = []
        for row in rows:
            # 4. Trova le celle (td)
            #cells = row.find_elements(By.CSS_SELECTOR, "td")
            cells = row.text.split(' ')
            if cells[0] == 'Year':
                continue
            
            # Se la tabella ha 3 colonne
            year = cells[0]
            mrkcap = cells[1]+cells[2]
            
            all_data.append((year, mrkcap))
            
            if diz.get(sy) == None:
                diz[sy] = []
                diz[sy].append((year, mrkcap))
            else:
                diz[sy].append((year, mrkcap))
        
        #search_box.submit()  # o Keys.ENTER
        
        print(sy)
        print(diz.get(sy))
        print()

        # Opzionalmente, puoi attendere il caricamento dei risultati:
        time.sleep(0.1)

finally:
    # Chiudi il browser
    driver.quit()
    print(diz)
"""

"""
#!/usr/bin/env python
try:
    # For Python 3.0 and later
    from urllib.request import Request, urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

import certifi
import json
import time
import csv
import numpy as np

def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:

    # Crea un lettore CSV con DictReader
    csv_reader = csv.DictReader(file)
    
    symbols = [col['Symbol'] for col in csv_reader]

# for sy in symbols:
#     url = (f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{sy}?&from=1999-01-01&to=2000-01-01&apikey=pUIXDJjV4fbrI5lhIQjvIgmnHeQOTk7A")

#     data = get_jsonparsed_data(url)
#     for d in data:
#         print(d['date'], d['marketCap'])


dates = [("1999-01-01", "2000-01-01"), ("2000-01-01", "2001-01-01"), ("2001-01-01", "2002-01-01"), ("2002-01-01", "2003-01-01"), 
         ("2003-01-01", "2004-01-01"), ("2004-01-01", "2005-01-01"), ("2005-01-01", "2006-01-01"), ("2006-01-01", "2007-01-01"), 
         ("2007-01-01", "2008-01-01"), ("2008-01-01", "2009-01-01"), ("2009-01-01", "2010-01-01"), ("2010-01-01", "2011-01-01"), 
         ("2011-01-01", "2012-01-01"), ("2012-01-01", "2013-01-01"), ("2013-01-01", "2014-01-01"), ("2014-01-01", "2015-01-01"), 
         ("2015-01-01", "2016-01-01"), ("2016-01-01", "2017-01-01"), ("2017-01-01", "2018-01-01"), ("2018-01-01", "2019-01-01"), 
         ("2019-01-01", "2020-01-01"), ("2020-01-01", "2021-01-01"), ("2021-01-01", "2022-01-01"), ("2022-01-01", "2023-01-01"),
          ("2023-01-01", "2024-01-01")
    ] 

for date in dates:
    with open(f'/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/marketCap/{date[0]}-{date[1]}.csv', mode='a') as file:
        writer = csv.writer(file)
        writer.writerow(["symbol", "date", "marketCap"])
        
        for sy in symbols:
            url = (f"https://financialmodelingprep.com/api/v3/historical-market-capitalization/{sy}?&from={date[0]}&to={date[1]}&apikey=pUIXDJjV4fbrI5lhIQjvIgmnHeQOTk7A")

            data = get_jsonparsed_data(url)
                #print(d['date'], d['marketCap'])
            marketCap = [d['marketCap'] for d in data]
                
            marketCapMean = np.mean(marketCap)
                
                #with open(f'/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/marketCap/{date[0]}-{date[1]}.csv', mode='a') as file1:
                    #writer = csv.writer(file)
                    #writer.writerow(["symbol", "date", "marketCap"])
                    #for d in data:
                    #    writer.writerow([sy, d['date'], d['marketCap']])
            writer.writerow([sy, date[1], marketCapMean])
                
            time.sleep(1)
        time.sleep(1)
    print()




    
"""

import yfinance as yf
import pandas as pd
import csv
import os
import time
#from pathlib import Path

import sys
from pathlib import Path


# Trova dinamicamente la cartella Trading-Agent e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'Trading-Agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from config import get_path_specify, project_root, marketFiles, market_data_path

# Ora possiamo importare `config`
#get_path_specify(["marketData", "csv_files", "marketCap"])





#marketFiles = [#'/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols_sorted.csv', 
#               '/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nyse_symbols_sorted.csv',
#               '/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/largest_companies_EU.csv'
#               ]




def getMarkCap(marketFiles):
    
    for fmark in marketFiles:
        fmark = str(fmark)
        
        with open(f'{fmark}', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:

            # Crea un lettore CSV con DictReader
            csv_reader = csv.DictReader(file)
            
            symbols = [col['Symbol'].replace('/', '-') for col in csv_reader]

        for sy in symbols:
            # Seleziona il titolo
            #ticker = "AAPL"
            stock = yf.Ticker(sy)
            
            #print(os.listdir("/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/marketCap"))
            
            if fmark == f'{market_data_path}/csv_files/nasdaq_symbols_sorted.csv':
                if f"market_cap_{sy}.csv" in os.listdir(f"{market_data_path}/csv_files/marketCap/NASDAQ"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
                
            elif fmark == f'{market_data_path}/csv_files/nyse_symbols_sorted.csv':
                if f"market_cap_{sy}.csv" in os.listdir(f"{market_data_path}/csv_files/marketCap/NYSE"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
                
            elif fmark == f'{market_data_path}/csv_files/largest_companies_EU.csv':
                if f"market_cap_{sy}.csv" in os.listdir(f"{market_data_path}/csv_files/marketCap/LARG_COMP_EU"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
            
            # Ottieni il numero di azioni in circolazione
            shares_outstanding = stock.info.get("sharesOutstanding")
            
            if shares_outstanding == None:
                print(f"Shares outstanding non trovato per {sy}")
                continue
            
            # Scarica i prezzi storici
            historical_data = stock.history(period="max")  # Ultimi 5 anni

            if historical_data.empty:
                print(f"Dati storici non trovati per {sy}")
                continue
            
            # Calcola la market cap storica
            historical_data["Market Cap"] = historical_data["Close"] * shares_outstanding

            if fmark == f'{market_data_path}/csv_files/nasdaq_symbols_sorted.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{market_data_path}/csv_files/marketCap/NASDAQ/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
                
            elif fmark == f'{market_data_path}market_data_path/csv_files/nyse_symbols_sorted.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{market_data_path}/csv_files/marketCap/NYSE/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
                
            elif fmark == f'{market_data_path}/csv_files/largest_companies_EU.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{market_data_path}/csv_files/marketCap/LARG_COMP_EU/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
            
            time.sleep(0.3)

            # Mostra i primi valori
            #print(historical_data[["Close", "Market Cap"]].head())
    return 0
        

def orderMarkCapYears():
    market = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
    year = ['1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
    
    yearFile = ['1999.csv', '2000.csv', '2001.csv', '2002.csv', '2003.csv', '2004.csv', '2005.csv', '2006.csv', '2007.csv', '2008.csv', '2009.csv', '2010.csv', '2011.csv', '2012.csv', '2013.csv', '2014.csv', '2015.csv', '2016.csv', '2017.csv', '2018.csv', '2019.csv', '2020.csv', '2021.csv', '2022.csv', '2023.csv']
    
    countNasd = countNys = countEur = 0
    
    for mark in market:
        for _ in os.listdir(f"{market_data_path}/csv_files/marketCap/{mark}"):
            if mark == 'NASDAQ':
                countNasd += 1
            elif mark == 'NYSE':
                countNys += 1
            elif mark == 'LARG_COMP_EU':
                countEur += 1
    
    print("countNasd", ": ", countNasd, ",  " ,"countNys", ": ",  countNys,  ",  " ,"countEu", ": ", countEur)
    
    
    i = 0
    
    for mark in market:
        # Ordina i file csv per anno
        for f in os.listdir(f"{market_data_path}/csv_files/marketCap/{mark}"):
            if (f in yearFile) or (f == '.DS_Store'):
                continue
            i += 1
            print(f"{i}, : {f}")
            with open(f"{project_root}/marketData/csv_files/marketCap/{mark}/{f}", mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    
                    for d in ['1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010',
                            '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023']:
                        
                        v = row['Date'].split('-')[0]
                        if v == d:
                            fileX = open(f"{project_root}/marketData/csv_files/marketCap/{mark}/{d}.csv", mode='a')
                            symb = (f.split('.')[0]).split('_')[2]
                            fileX.write(symb + ',' + row['Date'] + ',' + row['Market Cap'] + '\n')
                        
                        
                        #print(row['Symbol'], row['Market Cap'])
            print()

        i = 0


if __name__ == '__main__':
    
        
    #marketFiles = [#'/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols_sorted.csv', 
    #           '/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nyse_symbols_sorted.csv',
    #           '/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/largest_companies_EU.csv'
    #           ]

    #marketFiles = [f"{project_root}/marketData/csv_files/nasdaq_symbols_sorted.csv", 
    #               f"{project_root}/marketData/csv_files/nyse_symbols_sorted.csv",
    #               f"{project_root}/marketData/csv_files/largest_companies_EU.csv"
    #              ]

    #getMarkCap(marketFiles)
    orderMarkCapYears()
