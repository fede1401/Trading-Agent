import yfinance as yf
import pandas as pd
import csv
import os
import time
#from pathlib import Path
import pandas as pd
from heapq import nlargest

import sys
from pathlib import Path
import logging
import traceback

# Trova dinamicamente la cartella Trading-Agent e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'trading-agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from manage_module import get_path_specify, project_root, main_project, db_path, manage_symbols_path, utils_path, history_market_data_path, capitalization_path, symbols_info_path, marketFiles 



def getMarkCap(marketFiles):    
    """
    Scarica i dati storici di market cap per ogni simbolo.
    
    Args: 
        4- marketFiles: lista di file csv contenenti i simboli delle azioni con le relative informazioni più importanti
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    
    # Funzione che può essere sostituita in qualche file poiché si ripete
    for fmark in marketFiles:
        fmark = str(fmark)
        
        with open(f'{fmark}', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
            # Crea un lettore CSV con DictReader
            csv_reader = csv.DictReader(file)
            
            # Estrai i simboli. Sostituisci '/' con '-' per una corretta formattazione
            symbols = [col['Symbol'].replace('/', '-') for col in csv_reader]
        
        # Per ogni simbolo scarica i dati storici e calcola la market cap (data dalle azioni in circolazione * prezzo di chiusura)
        for sy in symbols:
            # Crea un oggetto Ticker per il simbolo corrente
            stock = yf.Ticker(sy)
                        
            # Se il file market_cap_{sy}.csv esiste già, passa al simbolo successivo
            if fmark == f'{symbols_info_path}/NASDAQ/nasdaq_symbols_sorted.csv"':
                if f"market_cap_{sy}.csv" in os.listdir(f"{capitalization_path}/NASDAQ/all_mark_cap"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
                
            elif fmark == f'{symbols_info_path}/NYSE/nyse_symbols_sorted.csv':
                if f"market_cap_{sy}.csv" in os.listdir(f"{capitalization_path}/NYSE/all_mark_cap"):
                    print(f"Il file market_cap_{sy}.csv esiste già")
                    continue
                
            elif fmark == f'{symbols_info_path}/LARG_COMP_EU/largest_companies_EU.csv':
                if f"market_cap_{sy}.csv" in os.listdir(f"{capitalization_path}/LARG_COMP_EU/all_mark_cap"):
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
            
            # Calcola la market cap storica: numero di azioni in circolazione * prezzo di chiusura
            historical_data["Market Cap"] = historical_data["Close"] * shares_outstanding

            # Salva i dati in un file CSV
            if fmark == f'{symbols_info_path}/NASDAQ/nasdaq_symbols_sorted.csv"':
                historical_data[["Close", "Market Cap"]].to_csv(f"{capitalization_path}/NASDAQ/all_mark_cap/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
                
            elif fmark == f'{symbols_info_path}/NYSE/nyse_symbols_sorted.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{capitalization_path}/NYSE/all_mark_cap/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
                
            elif fmark == f'{symbols_info_path}/LARG_COMP_EU/largest_companies_EU.csv':
                historical_data[["Close", "Market Cap"]].to_csv(f"{capitalization_path}/LARG_COMP_EU/all_mark_cap/market_cap_{sy}.csv")
                print(f"Dati salvati in market_cap_{sy}.csv")
            
            time.sleep(1)

            # Mostra i primi valori
            #print(historical_data[["Close", "Market Cap"]].head())
    return 0
        

def orderMarkCapYears():
    """
    Ordina i file CSV di market cap per anno e li salva in una cartella separata. (/by_year/...)
    Args:
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    market = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
    
    yearFile = ['1999.csv', '2000.csv', '2001.csv', '2002.csv', '2003.csv', '2004.csv', '2005.csv', '2006.csv', '2007.csv', '2008.csv', '2009.csv', '2010.csv', '2011.csv', 
                '2012.csv', '2013.csv', '2014.csv', '2015.csv', '2016.csv', '2017.csv', '2018.csv', '2019.csv', '2020.csv', '2021.csv', '2022.csv', '2023.csv', '2024.csv']
    
    topFiles = ['topVal1999.csv', 'topVal2000.csv', 'topVal2001.csv', 'topVal2002.csv', 'topVal2003.csv', 'topVal2004.csv', 'topVal2005.csv', 'topVal2006.csv', 'topVal2007.csv', 
                'topVal2008.csv', 'topVal2009.csv', 'topVal2010.csv', 'topVal2011.csv', 'topVal2012.csv', 'topVal2013.csv', 'topVal2014.csv', 'topVal2015.csv', 'topVal2016.csv', 
                'topVal2017.csv', 'topVal2018.csv', 'topVal2019.csv', 'topVal2020.csv', 'topVal2021.csv', 'topVal2022.csv', 'topVal2023.csv', 'topVal2024.csv']
    
    countNasd = countNys = countEur = 0
    
    # Conta il numero di file per ogni mercato
    for mark in market:
        for _ in os.listdir(f"{capitalization_path}/{mark}/all_mark_cap"):
            if mark == 'NASDAQ':
                countNasd += 1
            elif mark == 'NYSE':
                countNys += 1
            elif mark == 'LARG_COMP_EU':
                countEur += 1
    
    print("countNasd", ": ", countNasd, ",  " ,"countNys", ": ",  countNys,  ",  " ,"countEu", ": ", countEur)
    
    
    i = 0
    
    # Per ogni mercato:
    for mark in market:
        # Ordina i file csv per anno
        for f in os.listdir(f"{capitalization_path}/{mark}/all_mark_cap"):
            if (f == '.DS_Store'):
            #if (f in yearFile) or (f == '.DS_Store') or (f in topFiles):
                continue
            i += 1
            print(f"{i}, : {f}")
            
            # Va a riempire i file di capitalizzazione di mercato e li ordina per anno.
            with open(f"{capitalization_path}/{mark}/all_mark_cap/{f}", mode='r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    
                    for d in ['1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006', '2007', '2008', '2009', '2010',
                            '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']:
                        
                        v = row['Date'].split('-')[0]
                        if v == d:
                            fileX = open(f"{capitalization_path}/{mark}/by_year/{d}.csv", mode='a')
                            symb = (f.split('.')[0]).split('_')[2]
                            fileX.write(symb + ',' + row['Date'] + ',' + row['Market Cap'] + '\n')
                            fileX.close()
                        #print(row['Symbol'], row['Market Cap'])
            print()

        i = 0
    return 0


def deleteFilesAboutSingleTitles():
    """
    Elimina i file contenenti i dati di market cap per ogni singolo titolo per pulizia.
    Args:
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
    yearFile = ['1999.csv', '2000.csv', '2001.csv', '2002.csv', '2003.csv', '2004.csv', '2005.csv', '2006.csv', '2007.csv', '2008.csv', '2009.csv', '2010.csv', '2011.csv', 
                '2012.csv', '2013.csv', '2014.csv', '2015.csv', '2016.csv', '2017.csv', '2018.csv', '2019.csv', '2020.csv', '2021.csv', '2022.csv', '2023.csv', '2024.csv']

    for m in markets:
        for f in os.listdir(f"{capitalization_path}/{m}/all_mark_cap"):
            os.remove(f"{capitalization_path}/{m}/all_mark_cap/{f}")
    
    return 0

             

def preprocess_topX_for_year():
    """
    Preprocessa i file topX per ogni anno.
    Args:
    
    Returns:
        0: se la funzione è stata eseguita correttamente
    """
    
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU'] #markets = ['LARG_COMP_EU']
    try:
        for m in markets:
            for f in os.listdir(f"{capitalization_path}/{m}/by_year"):
                if f == '.DS_Store': #or f.startswith("top"):
                    continue
                
                with open(f"{capitalization_path}/{m}/by_year/{f}", mode='r') as file:
                    dates = {}
                    for row in file:
                        if row.strip() == 'symbol,date,market_cap':  # Ignora l'header
                            continue
                        
                        # memorizzo le informazioni delle capitalizzazioni di mercato in delle variabili che poi creeranno il dizionario.
                        symb, date, mrkcap = row.strip().split(',')
                        
                        # Elimina l'ora
                        date = date[0:-6]
                        
                        # se la data non è presente nel dizionario, la aggiunge, altrimenti aggiunge il simbolo e la capitalizzazione di mercato alla data corrispondente.
                        if date not in dates:
                            dates[date] = [(symb, float(mrkcap))]
                        else:
                            dates[date].append((symb, float(mrkcap)))
                    
                    # Ordina per market cap decrescente
                    dates = {k: sorted(v, key=lambda x: x[1], reverse=True) for k, v in dates.items()}
                    
                    # Converti in lista di dizionari
                    rows = []
                    for date, values in dates.items():
                        symbol_market_cap_str = "; ".join([f"{symb[0]}" for symb in values])  # Converti lista in stringa
                        rows.append({'date': date, 'symb': symbol_market_cap_str})
                    
                    # Scrivi nel CSV
                    year = f.split('.')[0]
                    output_path = f"{capitalization_path}/{m}/top_value/topVal{year}.csv"
                    
                    with open(output_path, mode='w', newline='') as file:
                        fieldnames = ['date', 'symb']
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(rows)  # Ora è nel formato corretto!
        
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
        
    finally:
        logging.info(f"Preprocessing completato.")
        return 0





if __name__ == '__main__':
    # Esegui le funzioni : getMarkCap, orderMarkCapYears, deleteFilesAboutSingleTitles, preprocess_topX_for_year   
    #getMarkCap(marketFiles)
    #orderMarkCapYears()
    deleteFilesAboutSingleTitles()
    #preprocess_topX_for_year()
