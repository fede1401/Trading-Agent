import yfinance as yf
import os
import fnmatch
import pandas as pd
#import db.insertDataDB as db, db.connectDB as connectDB
import logging
from datetime import datetime, time, timedelta
import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')
from db import insertDataDB as db, connectDB  as connectDB

from symbols import getSymbols as getSymbols
from pathlib import Path


"""
La funzione `downloadANDSaveStocksDataYahooFinance` utilizza la libreria `yfinance` per scaricare i dati storici di mercato di una lista di simboli e salvarli in file CSV nella cartella `marketData`.

Funzionamento:
1. Scarica i dati storici di ciascun simbolo. Se un file CSV esiste già per un simbolo, scarica solo i dati mancanti fino al giorno precedente rispetto alla data odierna.
2. Se il file CSV non esiste, scarica l'intero storico ("max") e crea un nuovo file.
3. I dati scaricati vengono salvati in CSV e successivamente inseriti nel database tramite la funzione `fillDB()`.
4. La funzione è ottimizzata per evitare di scaricare nuovamente dati già presenti e aggiornati.

Note:
- Il codice verifica se i dati esistenti sono aggiornati alla data di ieri o di oggi. In tal caso, il download viene saltato.
- È possibile ottimizzare ulteriormente l'inserimento nel database affinché vengano aggiunti solo i nuovi record, senza duplicare quelli già presenti.
"""

    
"""
def downloadANDSaveStocksDataYahooFinance(cur, conn):
    
    symbols = getSymbols.getSymbolsTotal()
    #for titol in symbols:
    #    ticker = yf.Ticker(titol)
    #    data = ticker.history(period="max", interval='1d', actions=False)# Get the historical data
    #    data.to_csv(f'marketData/{titol}1.csv')

    
    for titol in symbols:
        
        #print(os.listdir('../marketData'))
        #print(os.listdir('./marketData')) ---> ./ per debug
        
        titolCSV = titol + '.csv'
        
        #if titolCSV in os.listdir('../marketData'):
        if titolCSV in os.listdir('./marketData'):
                
            # Carica il file CSV in un DataFrame, ignorando le intestazioni se necessario
            df = pd.read_csv(f"./marketData/{titolCSV}", header=None)
            #df = pd.read_csv(f"../marketData/{titolCSV}", header=None)
            
            # Leggi solo l'ultima riga, convertendola in una lista per escludere i nomi delle colonne
            ultima_riga = df.iloc[-1].tolist()

            print(ultima_riga)
            if ultima_riga[0] == 'Date':
                print(f'{titol} withoud stock data')
                continue
            
            # Verifica se la data è più vecchia di 1 giorno
            x = (datetime.now() - timedelta(days=1))
            y = datetime.now()
            last_date = datetime.strptime(ultima_riga[0].split('+')[0], '%Y-%m-%d %H:%M:%S')
            x = x.replace(hour=0, minute=0, second=0, microsecond=0)
            y = y.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if last_date == x or last_date == y:
                # Scarica nuovamente i dati
                print(f'{titol} already downloaded')
                continue
            else:
                print(f'{titol} not downloaded')
                data = yf.download(titol, period="max", interval='1d')
                #data.to_csv(f'../marketData/{titol}.csv')
                data.to_csv(f'./marketData/{titol}.csv')
                print(f"Downloaded {titol}")
                #filename = '../marketData/'+titol+'.csv'
                filename = './marketData/'+titol+'.csv'
                fillDB(filename, cur, conn)
                print(f"Save {titol} in DB")
                
                
        else:
            data = yf.download(titol, period="max", interval='1d')
            data.to_csv(f'../marketData/{titol}.csv')
            #data.to_csv(f'./marketData/{titol}.csv')
            print(f"Downloaded {titol}")
            #filename = '../marketData/'+titol+'.csv'
            filename = './marketData/'+titol+'.csv'
            fillDB(filename, cur, conn)
            print(f"Save {titol} in DB")
    return 0
        
"""


def downloadANDSaveStocksDataYahooFinanceNASDAQ(cur, conn):
    
    symbols = getSymbols.getSymbolsTotal()
    #data_dir = Path('./marketData') # ---> ./ per debug
    data_dir = Path('../marketData/NASDAQ') # ---> ./ per esecuzione da terminale in path '/agent1'
    data_dir.mkdir(exist_ok=True)
    
    for titol in symbols:
        file_path = data_dir / f"{titol}.csv"
        if file_path.exists() and file_path.is_file() :
            
            df = pd.read_csv(file_path, header=None)
            ultima_riga = df.iloc[-1].tolist()
            if ultima_riga[0] == 'Date':
                print(f'{titol} withoud stock data')
                start_date = None
                continue
            
            # Verifica se la data è più vecchia di 1 giorno
            x = (datetime.now() - timedelta(days=1))
            y = datetime.now()
            last_date = datetime.strptime(ultima_riga[0].split('+')[0], '%Y-%m-%d %H:%M:%S')
            x = x.replace(hour=0, minute=0, second=0, microsecond=0)
            y = y.replace(hour=0, minute=0, second=0, microsecond=0)

            if last_date == x or last_date == y:
                # Scarica nuovamente i dati
                print(f'{titol} already downloaded')
                continue
            else:
                start_date = last_date + timedelta(days=1)
        
        else:
            logging.info(f"No file found for {titol}, downloading full dataset.")
            start_date = None
            
        try:
            if start_date:
                data = yf.download(titol, start=start_date.strftime('%Y-%m-%d'), interval='1d')
                data.to_csv(file_path, mode='a', header=None)
                fillDB(str(file_path), cur, conn)
                print(f"Data for {titol} savely successfully in DB.")
            
            else:
                data = yf.download(titol, period="max", interval='1d')
                if not data.empty:
                    data.to_csv(file_path, mode='w', header=None)
                    fillDB(str(file_path), cur, conn)
                    logging.info(f"Data for {titol} updated successfully in DB.")
        
        except Exception as e:
            logging.error(f"Error downloading data for {titol}: {e}")
            
    return 0
            

def fillDB(filename, cur, conn):
    with open(filename, 'r') as file:
        # Read each line in the file
        for line in file:
            # Print each line
            infoF = line.split(',')
            if infoF[0] != 'Date' and infoF[0] != 'Ticker' and infoF[0] != 'Price':
                symbol = filename.split('/')[2]
                symbol = symbol.split('.')[0]
                time_value_it = time_value_ny = infoF[0]
                close_price = infoF[2]
                open_price = infoF[5]
                high_price = infoF[3]
                low_price = infoF[4]
                time_frame = '1d'
                rate = [open_price, high_price, low_price, close_price, 0, 0, 0, time_value_it[0:len(time_value_it)-6], time_value_ny[0:len(time_value_it)-6]]
                print(symbol, rate, '\n')
                db.insertInNasdaqFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                            
        # close the file   
        file.close()
    return 0

        


def downloadANDSaveStocksData(cur, conn, market):
    if market == 'NASDAQ':
        symbols = getSymbols.getSymbolsNasda100()
        #data_dir = Path('./marketData') # ---> ./ per debug
        data_dir = Path('../marketData/NASDAQ') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'NYSE':
        symbols = getSymbols.getSymbolsNyse100()
        #data_dir = Path('./marketData/NYSE') # ---> ./ per debug
        data_dir = Path('../marketData/NYSE') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'LARG_COMP_EU':
        symbols = getSymbols.getSymbolsLargestCompEU100()
        #data_dir = Path('./marketData/LARG_COMP_EU') # ---> ./ per debug
        data_dir = Path('../marketData/LARG_COMP_EU') # ---> ./ per esec
        data_dir.mkdir(exist_ok=True)
    
    for titol in symbols:
        file_path = data_dir / f"{titol}.csv"
        print(file_path)
        if file_path.exists() and file_path.is_file() :
            
            df = pd.read_csv(file_path, header=None)
            ultima_riga = df.iloc[-1].tolist()
            if ultima_riga[0] == 'Date':
                print(f'{titol} withoud stock data')
                start_date = None
                continue
            
            # Verifica se la data è più vecchia di 1 giorno
            x = (datetime.now() - timedelta(days=1))
            y = datetime.now()
            last_date = datetime.strptime(ultima_riga[0].split('+')[0], '%Y-%m-%d %H:%M:%S')
            x = x.replace(hour=0, minute=0, second=0, microsecond=0)
            y = y.replace(hour=0, minute=0, second=0, microsecond=0)

            if last_date == x or last_date == y:
                # Scarica nuovamente i dati
                print(f'{titol} already downloaded')
                continue
            else:
                start_date = last_date + timedelta(days=1)
        
        else:
            logging.info(f"No file found for {titol}, downloading full dataset.")
            start_date = None
            
        try:
            if start_date:
                data = yf.download(titol, start=start_date.strftime('%Y-%m-%d'), interval='1d')
                data.to_csv(file_path, mode='a', header=None)
                fillDB(str(file_path), cur, conn, market=market)
                print(f"Data for {titol} savely successfully in DB.")
            
            else:
                data = yf.download(titol, period="max", interval='1d')
                if not data.empty:
                    data.to_csv(file_path, mode='w', header=None)
                    fillDB(str(file_path), cur, conn, market=market)
                    logging.info(f"Data for {titol} updated successfully in DB.")
        
        except Exception as e:
            logging.error(f"Error downloading data for {titol}: {e}")
            
    return 0



def fillDB(filename, cur, conn, market):
    with open(filename, 'r') as file:    
        # Read each line in the file
        for line in file:
                # Print each line
                infoF = line.split(',')
                if infoF[0] != 'Date' and infoF[0] != 'Ticker' and infoF[0] != 'Price':
                    symbol = filename.split('/')[3]
                    print(symbol)
                    symbol = symbol.split('.')[0]
                    print(symbol)
                    time_value_it = time_value_ny = infoF[0]
                    close_price = infoF[2]
                    open_price = infoF[5]
                    high_price = infoF[3]
                    low_price = infoF[4]
                    time_frame = '1d'
                    rate = [open_price, high_price, low_price, close_price, 0, 0, 0, time_value_it[0:len(time_value_it)-6], time_value_ny[0:len(time_value_it)-6]]
                    print(symbol, rate, '\n')
                    
                    if market == 'NASDAQ':
                        db.insertInNasdaqFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                    elif market == 'NYSE':
                        db.insertInNyseFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                    elif market == 'LARG_COMP_EU':
                        db.insertInLargeCompEUFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                                
        # close the file   
        file.close()
    return 0
       



"""def fillDB(cur, conn):
    for path, dirs, files in os.walk('../marketData'):
        for f in fnmatch.filter(files,'*.csv'):
            fullname = os.path.abspath(os.path.join(path,f))
            # open the file
            with open(fullname, 'r') as file:
                # Read each line in the file
                for line in file:
                    # Print each line
                    infoF = line.split(',')
                    if infoF[0] != 'Date' and infoF[0] != 'Ticker' and infoF[0] != 'Price':
                        symbol = f.split('.')[0]
                        time_value_it = time_value_ny = infoF[0]
                        close_price = infoF[2]
                        open_price = infoF[5]
                        high_price = infoF[3]
                        low_price = infoF[4]
                        time_frame = '1d'
                        rate = [open_price, high_price, low_price, close_price, 0, 0, 0, time_value_it[0:len(time_value_it)-6], time_value_ny[0:len(time_value_it)-6]]
                        db.insertInNasdaqFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                            
                # close the file   
                file.close()
    return 0
"""    

                

def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()
        
        # download dati
        #downloadANDSaveStocksDataYahooFinanceNASDAQ(cur, conn)
        market = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
        for m in market:
            downloadANDSaveStocksData(cur, conn, m)
    
    except Exception as e:
        logging.critical(f"Uncaught exception: {e}")
    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
    
    # Chiudi il cursore e la connessione
    cur.close()
    conn.close()
    
    return 0



if __name__ == '__main__':
    #downloadStocksDataYahooFinance()
    #fillDB()
    main()  # Eseguire il trading agent