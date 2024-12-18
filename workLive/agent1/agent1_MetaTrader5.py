# Raccolta dei dati e inserimento nel database postgreSQL.


import psycopg2
import time
import numpy as np
import logging
from datetime import datetime, time, timedelta
import time as time_module

import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent1')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent2')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent3')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

from db import insertDataDB, connectDB
from symbols import symbolsAcceptedByTickmill
import session_management, info_order_send
import MetaTrader5 as mt5


"""
Ecco alcune possibili cause per cui non vengono selezionati tutti i dati se l'intervallo di tempo è superiore a 2 anni:

- Limitazioni del Server del Broker: Il server del broker potrebbe non essere in grado di restituire 
    tutti i dati richiesti in un'unica chiamata se l'intervallo di tempo è troppo lungo.
- Limitazioni dell'API di MT5: L'API di MT5 potrebbe avere limiti sulla quantità di dati che 
    può restituire in una singola chiamata.
- Problemi di Prestazioni: Richiedere troppi dati in una sola volta può causare problemi di prestazioni, 
    sia sul lato del client che del server.

Specificare l'intervallo di tempo di cui prendere i dati:
    da un'analisi ho notato che dall'inizio della nascita dell'indice NASDAQ Composite fino al 2017/09/18 i dati ci sono ogni giorno, 
    dopo di che è necessario specificare un intervallo ogni 2 anni altrimenti non vengono trovati i dati
    
    #start_date = datetime(1971, 2, 8) # nascita indice NASDAQ composite
    #end_date = datetime(2017, 9, 18)    
"""

# 2 ore per scaricare tutti i dati.

"""
- Scaricamento Iniziale Completo: La prima volta che esegui il programma, 
    scarica tutti i dati fino a due giorni fa.

- Aggiornamenti Continui: Dopo il primo scaricamento, il programma si aggiorna ogni giorno, 
    iniziando da ieri e fino alla data corrente, per mantenere il database aggiornato con i dati più recenti.

- Controllo dei Giorni della Settimana: Il programma entra in pausa durante il fine settimana, 
    quando i mercati sono chiusi, e riprende il lunedì successivo.

Scenario 1: Prima esecuzione del programma

    Prima esecuzione: Il programma controlla se ci sono dati nel database per ogni simbolo.
    Nessun dato nel database:
        Scarica tutti i dati storici specificati fino a due giorni fa.
    Dati presenti nel database:
        Verifica se last_date (data più recente presente nel database) è inferiore a due giorni fa.
        Se sì, scarica i dati mancanti fino a due giorni fa.
    Inizia il ciclo while:
        Imposta start_date a ieri e end_date a oggi.
        Ogni giorno scarica i dati del giorno precedente (start_date a end_date).

Scenario 2: Interruzione del programma e ripartenza il giorno successivo

    Interruzione del programma: Se il programma si interrompe e viene riavviato il giorno successivo, last_date sarà uguale a ieri.
    Ripartenza del programma:
        last_date sarà uguale a ieri, quindi il programma entrerà nel while loop e inizierà a scaricare i dati di oggi.
        Questo funziona perché il while loop gestisce l'aggiornamento giornaliero dei dati.

        
Scenario 3: Interruzione del programma e ripartenza dopo alcuni giorni

    Interruzione del programma: Se il programma si interrompe e viene riavviato dopo 4 giorni, last_date sarà inferiore di 4 giorni rispetto ad oggi.
    Ripartenza del programma:
        Il programma rileverà che last_date è inferiore a due giorni fa e scaricherà i dati mancanti per i 4 giorni in cui il programma non era in esecuzione.
        Successivamente, entrerà nel while loop per continuare l'aggiornamento giornaliero.

Copertura dei Casi

    Prima esecuzione: Scarica tutti i dati storici fino a due giorni fa.
    Interruzione e ripartenza giornaliera: Il ciclo while gestisce il download giornaliero dei dati.
    Interruzione e ripartenza dopo più giorni: Il controllo su last_date assicura che tutti i dati mancanti vengano scaricati.
"""

def main():
    # Configura il logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        # Connessione al server MetaTrader 5 e login e salvataggio nel db per lo storico dei login.
        session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)

        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate(session_management.name, session_management.account, session_management.server, cur, conn)

        # Ottenimento delle azioni del Nasdaq accettate dal broker TickMill.
        symbols = symbolsAcceptedByTickmill.getSymbolsAcceptedByTickmill()
        print(f"Symbols:{symbols}")

        # Controllo se i simboli azionari sono presenti nel database
        for symbol in symbols:
            logging.info(f"Processing symbol: {symbol}")

            # Si controlla se il simbolo azionario è presente nel MarketWatch e lo si aggiunge 
            info_order_send.checkSymbol(symbol)

            # Nelle query inserire apici '{symbol}' per far sì che vengano trattati come stringhe.

            """
            # Recupera la data meno recente del db
            cur.execute(f"SELECT time_value_it FROM nasdaq_actions WHERE symbol = '{symbol}' ORDER BY time_value_it ASC LIMIT 1")
            old_date = cur.fetchone()

            # Recupera la data più recente del db
            cur.execute(f"SELECT time_value_it FROM nasdaq_actions WHERE symbol = '{symbol}' ORDER BY time_value_it DESC LIMIT 1")
            last_date = cur.fetchone()
            """
             
            # Esegui una sola query per ottenere sia la data più vecchia che quella più recente
            cur.execute(f"SELECT MIN(time_value_it), MAX(time_value_it) FROM nasdaq_actions WHERE symbol = '{symbol}'")
            old_date, last_date = cur.fetchone()

            # Se non ci sono dati nel database, scarica tutti i dati storici fino a 2 giorni fa
            if old_date is None and last_date is None:

                logging.info("Scaricamento dati !\n")

                # Scarico i dati tramite la funzione copy_rates_range e li inserisco nel database
                insertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_D1, datetime(1971, 2, 8), datetime(2017, 9, 18), cur=cur, conn=conn)
                insertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, datetime(2017, 9, 18), datetime(2020, 1, 1), cur=cur, conn=conn)
                insertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, datetime(2020, 1, 1), datetime(2022, 1, 1), cur=cur, conn=conn)
                insertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, datetime(2022, 1, 1), (datetime.now()- timedelta(days=2)), cur=cur, conn=conn)

            else:

                # Scaricamento dei dati di mercato per le date mancanti fino a 2 giorni fa
                if last_date < datetime.now() - timedelta(days=2):
                    logging.info("Scaricamento dati per le azioni con dati mancanti !\n")

                    # Scarico i dati tramite la funzione copy_rates_range e li inserisco nel database: ad esempio se last_date corrisponde a 2024-7-10 e 
                    # datetime.now()- timedelta(days=2) = 2024-7-16, ci siamo persi i dati per le date 11,12,15 poichè (13 e 14 è sabato e domenica)
                    insertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, last_date, datetime.now()- timedelta(days=2), cur=cur, conn=conn)
                
                else:
                    logging.info(f"I dati per il simbolo azionario {symbol} sono già stati scaricati ed inseriti nel db!\n")


        # Aggiornamento delle date per scaricaricare i dati di mercato del giorno precedente
        start_date =  datetime.now()- timedelta(days=1)
        end_date = datetime.now()

        # Ciclo while per scaricare i dati di mercato del giorno precedente
        while True:    
            # Ritorna un intero corrispondente al giorno della settimana ( 0: Monday, ... , 6: Sunday )
            dayOfWeek = datetime.today().weekday() 
            
            # Se il giorno della settimana è sabato o domenica mettiamo in pausa il programma poiché il mercato è chiuso
            if dayOfWeek in {5, 6}:
                days_to_wait = 2 if dayOfWeek == 5 else 1
                logging.info(f"Pausa del trading agent poiché è {'sabato' if dayOfWeek == 5 else 'domenica'}.\n")
                time_module.sleep(days_to_wait * 86400)
                continue

            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now()

            for symbol in symbols:
                logging.info(f"Scaricamento dati per il giorno {start_date} !\n")
                insertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, start_date, end_date, cur, conn)

            logging.info("Dormi per un giorno.")
            time_module.sleep(86400)
            
            
            """
            # Se il giorno della settimana è sabato o domenica mettiamo in pausa il programma poiché il mercato è chiuso
            if dayOfWeek == 5 or dayOfWeek == 6:
                logging.info(f"Pausa del trading agent poiché è sabato o domenica. {dayOfWeek}\n")
                
                # Il programma si interrompe fino a lunedì
                if dayOfWeek == 5:
                    logging.info("Oggi è sabato, il programma si interrompe fino a lunedi.\n")
                    
                    # Calcola il tempo attuale
                    now = datetime.now()
                    
                    # Definisci il tempo corrispondente ai 2 giorni successivi (lunedì)
                    next_day = now + timedelta(days=2)
                    
                    # Calcola la durata in secondi da adesso fino a lunedì
                    seconds_next_day = (next_day - now).total_seconds()
                    logging.info(f"Waiting for {seconds_next_day} seconds until next 2 days.\n")
                    
                    # Metti in pausa il programma
                    time_module.sleep(seconds_next_day)


                if dayOfWeek == 6:
                    logging.info("Oggi è domenica, il programma si interrompe fino a lunedi.\n")

                    # Calcola il tempo attuale
                    now = datetime.now()
                    
                    # Definisci il tempo corrispondente al giorno successivo (lunedì)
                    next_day = now + timedelta(days=1)
                    
                    # Calcola la durata in secondi da adesso fino a lunedì
                    seconds_next_day = (next_day - now).total_seconds()
                    logging.info(f"Waiting for {seconds_next_day} seconds until next day.\n")
                    
                    # Metti in pausa il programma
                    time_module.sleep(seconds_next_day)
        
        
            # Per ogni simbolo azionario del Nasdaq accettato dal broker TickMill si scaricano i dati del giorno precedente
            for symbol in symbols:
                logging.info(f"Processing symbol: {symbol}")

                info_order_send.checkSymbol(symbol)
                
                logging.info(f"Scaricamento dati per il giorno {start_date} !\n")
                # Scarico i dati tramite la funzione copy_rates_range e li inserisco nel database
                insertDataDB.downloadInsertDB_data(symbol, mt5.TIMEFRAME_M15, start_date, end_date, cur=cur, conn=conn)

                
            logging.info("Dormi per un giorno.")
            logging.info(f"Start date: {start_date}")
            logging.info(f"End date: {end_date}")
            
            # sleep di 1 giorno, utilizzare time_modlue per evitare conflitti con il nome del modulo 'time'
            time_module.sleep(86400)

            # Dopo la pausa del programma andrà a scaricare i dati per intero del giorno precedente.
            # Ad esempio, ho lanciato il programma alle ore 15:00 del 16, il programma si 
            # è scaricato tutti i dati della giornata del 15 fino alle 22 itialiane (orario chiusura mercato) 
            # e il giorno successivo che è il 17, andrà a scaricare i dati di oggi 16.

            # Aggiornamento delle date dopo la pausa per scaricaricare i dati di mercato del giorno precedente
            start_date = end_date
            end_date = datetime.now()
            
            """
            
            
    except Exception as e:
        logging.critical(f"Uncaught exception: {e}")
    finally:
        session_management.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")



if __name__ == '__main__':    
    main()
