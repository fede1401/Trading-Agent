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
Il codice scarica dati di borsa per una lista di titoli specifici (NASDAQ, NYSE, o LARG_COMP_EU), li salva in file CSV e li registra in un database. In maniera semplificata, il processo svolto può essere riassunto così:

1. **Scelta del mercato**:  In base al mercato specificato (es. `'NASDAQ'`), ottiene una lista di simboli azionari (`symbols`) e definisce una directory per salvare i dati.

2. **Controllo e download dei dati**:
   - Per ciascun simbolo nella lista:
     - Controlla se esiste già un file CSV con i dati del titolo.
     - Se il file esiste, verifica se i dati sono aggiornati fino al giorno precedente:
       - Se aggiornati, salta il download.
       - Se non aggiornati, scarica i dati mancanti a partire dall'ultima data registrata.
     - Se il file non esiste, scarica tutti i dati disponibili.
   - I dati vengono scaricati utilizzando `yfinance` e salvati nel file CSV.

3. **Inserimento nel database**:
   - Per ogni riga del file CSV:
     - Estrae informazioni rilevanti (es. simbolo, prezzo di apertura, chiusura, ecc.).
     - Inserisce i dati nel database corrispondente al mercato (`NASDAQ`, `NYSE`, o `LARG_COMP_EU`).

4. **Chiusura delle connessioni**: Chiude la connessione al database e termina il programma.

### Funzionamento delle funzioni principali:
- **`downloadANDSaveStocksData`**: Scarica i dati dei titoli azionari e li salva in file CSV.
- **`fillDB`**: Legge i file CSV e inserisce i dati nel database.
- **`main`**: Coordina l'esecuzione, impostando il mercato da processare, gestendo la connessione al database e lanciando le funzioni principali.

### Elementi chiave:
- **Directory di salvataggio dei dati**: Differenziata per mercato.
- **Check di aggiornamento**: Si assicura che i dati siano sempre aggiornati.
- **Integrazione con il database**: Inserisce i dati scaricati nel database appropriato.
- **Gestione robusta**: Previene errori grazie al logging e al controllo delle eccezioni.
"""

    

def downloadANDSaveStocksData(cur, conn, market):
    if market == 'NASDAQ':
        symbols = getSymbols.getSymbolsNasdaq(400)
        #data_dir = Path('./marketData') # ---> ./ per debug
        data_dir = Path('../../marketData/NASDAQ') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'NYSE':
        symbols = getSymbols.getSymbolsNyse(400)
        #data_dir = Path('./marketData/NYSE') # ---> ./ per debug
        data_dir = Path('../../marketData/NYSE') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'LARG_COMP_EU':
        symbols = getSymbols.getSymbolsLargestCompEU(400)
        #data_dir = Path('./marketData/LARG_COMP_EU') # ---> ./ per debug
        data_dir = Path('../../marketData/LARG_COMP_EU') # ---> ./ per esec
        data_dir.mkdir(exist_ok=True)
    
    for titol in symbols:
        file_path = data_dir / f"{titol}.csv"
        print(file_path)
        if file_path.exists() and file_path.is_file() :
            
            df = pd.read_csv(file_path, header=None)
            ultima_riga = df.iloc[-1].tolist()
            print(f"Ultima riga {ultima_riga}")
            if ultima_riga[0] == 'Date':
                print(f'{titol} withoud stock data')
                start_date = None
                continue
            
            # Verifica se la data è più vecchia di 1 giorno
            x = (datetime.now() - timedelta(days=1))
            y = datetime.now()
            #last_date = datetime.strptime(ultima_riga[0].split('+')[0], '%Y-%m-%d %H:%M:%S')
            last_date = datetime.strptime(ultima_riga[0], '%Y-%m-%d')
            x = x.replace(hour=0, minute=0, second=0, microsecond=0)
            y = y.replace(hour=0, minute=0, second=0, microsecond=0)
            x = x.strftime('%Y-%m-%d')
            y = y.strftime('%Y-%m-%d')

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
                data.to_csv(file_path, mode='a')
                #data.to_csv(file_path, mode='a', header=None)
                print(f"---------------")
                fillDB(str(file_path), cur, conn, market=market)
                print(f"Data for {titol} savely successfully in DB.")
            
            else:
                data = yf.download(titol, period="max", interval='1d')
                if not data.empty:
                    data.to_csv(file_path, mode='w')
                    #sdata.to_csv(file_path, mode='w', header=None)
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
                    symbol = filename.split('/')[4]
                    #symbol = filename.split('/')[0]
                    print(symbol)
                    symbol = symbol.split('.')[0]
                    print(symbol)
                    # price 0, close 1, high 2, low 3, open 4, volume 5
                    time_value_it = time_value_ny = infoF[0]
                    close_price = infoF[1]
                    open_price = infoF[4]
                    high_price = infoF[2]
                    low_price = infoF[3]
                    time_frame = '1d'
                    #rate = [open_price, high_price, low_price, close_price, 0, 0, 0, time_value_it[0:len(time_value_it)-6], time_value_ny[0:len(time_value_it)-6]]
                    rate = [open_price, high_price, low_price, close_price, 0, 0, 0, time_value_it, time_value_ny]
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
        #downloadANDSaveStocksData(cur, conn, 'NASDAQ')
    
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