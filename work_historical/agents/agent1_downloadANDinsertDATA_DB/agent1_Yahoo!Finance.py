import yfinance as yf
import os
import pandas as pd
import logging
from datetime import datetime, time, timedelta


import sys
from pathlib import Path


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

get_path_specify([db_path, f'{main_project}/symbols', ])

from database import insertDataDB as db, connectDB  as connectDB
from work_historical.symbols import manage_symbol as manage_symbol



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
    """
    Scaricamento dei dati e salvataggio nel database: per lo scaricamento viene controllato se in precedenza i dati fossero già scaricati:
    - se i dati sono già scaricati, vengono scaricati solo i dati mancanti a partire dall'ultimo giorno scaricato
    - se i dati non sono scaricati, vengono scaricati tutti i dati storici
    
    Args:
        - cur: cursore per il database
        - conn: connessione al database
        - market: mercato di riferimento (es. 'NASDAQ', 'NYSE', 'LARG_COMP_EU')
        
    Returns:
        - 0: se il processo è completato con successo
    """

    if market == 'NASDAQ':
        # selezione dei simboli azionari per la borsa NASDAQ
        symbols = manage_symbol.get_symbols('NASDAQ', -1)
        
        data_dir = Path(f'{history_market_data_path}/NASDAQ') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'NYSE':
        # selezione dei simboli azionari per la borsa NYSE
        symbols = manage_symbol.get_symbols('NYSE', -1)
        
        data_dir = Path(f'{history_market_data_path}/NYSE') # ---> ./ per esecuzione da terminale in path '/agent1'
        data_dir.mkdir(exist_ok=True)
        
    elif market == 'LARG_COMP_EU':
        # selezione dei simboli azionari per la borsa LARG_COMP_EU
        symbols = manage_symbol.get_symbols('LARG_COMP_EU', -1)

        data_dir = Path(f'{history_market_data_path}/LARG_COMP_EU') # ---> ./ per esec
        data_dir.mkdir(exist_ok=True)
    
    # Scarica i dati per ciascun simbolo
    for titol in symbols:
        # Definizione del percorso del file CSV in cui salvare i dati
        file_path = data_dir / f"{titol}.csv"
        print(file_path)
        
        # Verifica se il file esiste già: significa che i dati sono già stati scaricati in precedenza
        if file_path.exists() and file_path.is_file() :
            
            # viene caricato il file in un DataFrame Pandas, specificando che non ci sono intestazioni
            df = pd.read_csv(file_path, header=None)
            
            # viene presa l'ultima riga del dataframe e viene trasformato in una lista di valori
            ultima_riga = df.iloc[-1].tolist()
            print(f"Ultima riga {ultima_riga}")
            
            # se l'ultimo valore della colonna "Date" è uguale a "Date", significa che il file è vuoto
            if ultima_riga[0] == 'Date':
                print(f'{titol} withoud stock data')
                
                # viene definita la data di partenza per scaricare i dati: in questo caso None e il periodo sarà 'max'
                start_date = None
                continue
            
            # Verifica se la data è più vecchia di 1 giorno:
            x = (datetime.now() - timedelta(days=1)) # data di 1 giorno fa
            y = datetime.now()                       # data odierna
            
            # viene trasformata la data dell'ultima riga in un oggetto datetime, con il formato specificato
            last_date = datetime.strptime(ultima_riga[0], '%Y-%m-%d')
            
            # vengono formattate le date a mezzanotte per un confronto corretto
            x = x.replace(hour=0, minute=0, second=0, microsecond=0)
            y = y.replace(hour=0, minute=0, second=0, microsecond=0)
            x = x.strftime('%Y-%m-%d')
            y = y.strftime('%Y-%m-%d')

            # se l'ultima data è uguale a ieri o oggi, non scaricare nuovamente i dati
            if last_date == x or last_date == y:
                # i dati sono già aggiornati fino a ieri/oggi
                print(f'{titol} already downloaded')
                continue
            else:
                # viene impostata la data di partenza per scaricare i dati mancanti a partire dal giorno successivo all'ultimo scaricato
                start_date = last_date + timedelta(days=1)
        
        # Se il file non esiste, scarica l'intero storico
        else:
            logging.info(f"No file found for {titol}, downloading full dataset.")
                    
            # viene definita la data di partenza per scaricare i dati: in questo caso None e il periodo sarà 'max'
            start_date = None
            
        try:
            # se start_date non è None, vengono scaricati i dati mancanti a partire da start_date
            if start_date:
                data = yf.download(titol, start=start_date.strftime('%Y-%m-%d'), interval='1d', auto_adjust=False)
                data.to_csv(file_path, mode='a')
                #data.to_csv(file_path, mode='a', header=None)
                print(f"---------------")
                
                # vengono inseriti i dati nel database
                fillDB(str(file_path), cur, conn, market=market)
                print(f"Data for {titol} savely successfully in DB.")
            
            # se start_date è None, vengono scaricati tutti i dati storici: grazie al parametro period='max'
            else:
                data = yf.download(titol, period="max", interval='1d', auto_adjust=False)
                if not data.empty:
                    data.to_csv(file_path, mode='w')
                    
                    # vengono inseriti i dati nel database
                    fillDB(str(file_path), cur, conn, market=market)
                    logging.info(f"Data for {titol} updated successfully in DB.")
        
        except Exception as e:
            logging.error(f"Error downloading data for {titol}: {e}")
            
    return 0



def fillDB(filename, cur, conn, market):
    """
    Funzione per l'inserimento dei dati nel database: 
    - per ogni file csv contenente i dati di mercato:
        - si scarta la riga di header
        - si estraggono i campi di interesse e si inseriscono nel database (grazie a funzioni specifiche per ogni mercato)
    
    Args:
        - filename (str): nome del file csv contenente i dati.
        - cur: cursore per il database
        - conn: connessione al database
        - market: mercato di riferimento (es. 'NASDAQ', 'NYSE', 'LARG_COMP_EU')
    
    Returns:
        - 0: se l'inserimento è completato con successo
    """
    
    with open(filename, 'r') as file:    
        # per ogni riga del file csv c'è l'inserimento dei dati in un record del database
        for line in file:
                # viene splittata la riga in base al carattere ',' e vengono presi i valori
                infoF = line.split(',')
                # viene controllato che la riga non sia l'intestazione del file, in tal caso non viene inserita nel database
                if infoF[0] != 'Date' and infoF[0] != 'Ticker' and infoF[0] != 'Price':
                    # vengono presi i valori della riga --> price 0, close 1, high 2, low 3, open 4, volume 5
                    
                    symbol = filename.split('/')[4]
                    symbol = symbol.split('.')[0]
                    
                    time_value_it = time_value_ny = infoF[0]
                    
                    close_price = infoF[2]
                    open_price = infoF[5]
                    high_price = infoF[3]
                    low_price = infoF[4]
                    
                    time_frame = '1d'
                    
                    # array che raggruppa i valori per poi inserirli nel DB.
                    rate = [open_price, high_price, low_price, close_price, 0, 0, 0, time_value_it, time_value_ny]
                    print(symbol, rate, '\n')
                    
                    # a seconda del mercato di riferimento vengono inseriti i dati nel database
                    if market == 'NASDAQ':
                        db.insertInNasdaqFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                    elif market == 'NYSE':
                        db.insertInNyseFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                    elif market == 'LARG_COMP_EU':
                        db.insertInLargeCompEUFromYahoo(symbol, time_frame, rate, cur=cur, conn=conn)
                                
        # chiurusra del file
        file.close()
    return 0
       

                

def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()
        
        # Scarica e salva i dati per i mercati specificati
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
    main()  # Eseguire il trading agent