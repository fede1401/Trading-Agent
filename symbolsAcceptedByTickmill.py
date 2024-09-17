import csv
import MetaTrader5 as mt5
import session_management, insertDataDB, connectDB
import pandas as pd
import time

# Ricordarsi nella documentazione che l'utente per eseguire gli agent, deve creare la cartella csv_files e inserire all'interno
# il file nasdaq_symbols.csv scaricato dal sito del nasdaq.com

# Funzione per leggere i simboli Nasdaq da un file CSV
def symbolsNasdaqCSV():    
    # Apri il file CSV in modalità lettura
    with open('csv_files/nasdaq_symbols.csv', mode='r') as file:
        
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
    
        # Inizializza una lista vuota per memorizzare i simboli
        symbols =[]

        # Aggiungi ogni simbolo dalla colonna 'Symbol' del CSV alla lista
        for col in csv_reader:
            symbols.append(col['Symbol']) 

    # Ritorna la lista dei simboli
    return symbols



# Funzione per ottenere i simboli accettati dal broker Tickmill
def getSymbolsAcceptedByTickmill():

    # Ottieni la lista dei simboli accettati dal broker Tickmill
    symbols = symbolsNasdaqCSV()

    # Inizializza una lista vuota per memorizzare i simboli accettati
    symbolsAccepted = []
    for s in symbols:
        # Ottieni le informazioni sul simbolo da MetaTrader5
        symbol_info = mt5.symbol_info(s)

        # Se il simbolo non esiste, passa al prossimo simbolo
        if symbol_info == None:
            continue

        # Se il simbolo esiste
        else:
            # Controlla se il simbolo è visibile nel MarketWatch
            if not symbol_info.visible:
                print(s, "is not visible, trying to switch on")
                
                # Se il simbolo non è visibile, prova a renderlo visibile
                if not mt5.symbol_select(s,True):
                    print("symbol_select({}}) failed, exit", s)
                    continue
                else:
                    # Se riesce, aggiungi il simbolo alla lista dei simboli accettati
                    symbolsAccepted.append(s)
            else:
                # Se il simbolo è già visibile, aggiungilo direttamente alla lista
                symbolsAccepted.append(s)

    # Ritorna la lista dei simboli accettati
    return symbolsAccepted



# Funzione per ottenere i simboli ordinati per capitalizzazione di mercato in ordine decrescente
def getSymbolsCapDesc():
    # Ottieni i simboli accettati dal broker Tickmill
    symbolsAccepted = getSymbolsAcceptedByTickmill()
    print(symbolsAccepted)

    # Dizionario per memorizzare i simboli e la loro capitalizzazione di mercato
    diz = dict()

    # Leggi il file CSV in un DataFrame
    df = pd.read_csv('csv_files/nasdaq_symbols.csv')

    # Ordina il DataFrame in base alla colonna 'Market Cap' in ordine decrescente
    df_sorted = df.sort_values(by='Market Cap', ascending=False)

    # Salva il DataFrame ordinato in un nuovo file CSV
    df_sorted.to_csv('csv_files/nasdaq_symbols_sorted.csv', index=False)

    # Apri il file CSV ordinato in modalità lettura
    with open('csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_sort_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e la loro capitalizzazione di mercato al dizionario
        for col in csv_sort_reader:
            if col['Symbol'] in symbolsAccepted:
                diz[col['Symbol']] = col['Market Cap']

    # Ottieni le chiavi del dizionario (i simboli)
    key_diz = list(diz.keys())

    print(len(key_diz))

    # Ritorna i simboli ordinati per capitalizzazione di mercato
    return key_diz


# Funzione per ottenere il 5% dei simboli con la capitalizzazione di mercato più alta
def get5PercentSymbolsCapDesc():
    # Ottieni i simboli ordinati per capitalizzazione di mercato
    symbol_cap_desc = getSymbolsCapDesc()

    # Calcola il 5% del numero totale di simboli
    n = len(symbol_cap_desc)
    n_5 = int(n * 0.05)

    # Ritorna il 5% dei simboli con la capitalizzazione di mercato più alta
    return symbol_cap_desc[0:n_5]



def getSectorSymbols():
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()

    # Connessione al server MetaTrader 5 e login e salvataggio nel db per lo storico dei login.
    session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)
        
    # Inserimento dei dati relativi al login nel database
    insertDataDB.insertInLoginDate(session_management.name, session_management.account, session_management.server, cur, conn)

    # Ottieni i simboli accettati dal broker Tickmill
    symbolsAccepted = getSymbolsAcceptedByTickmill()

    # Dizionario per memorizzare i simboli e il settore di appartenenza
    diz = dict()

    # Leggi il file CSV in un DataFrame
    df = pd.read_csv('csv_files/nasdaq_symbols.csv')

    # Apri il file CSV in modalità lettura
    with open('csv_files/nasdaq_symbols.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            if col['Symbol'] in symbolsAccepted:
                diz[col['Symbol']] = col['Sector']

    # Ottieni le chiavi del dizionario (i simboli)
    key_diz = list(diz.keys())

    print(diz.keys())

    settoriDupl = diz.values()
    settori = []
    for sett in settoriDupl:
        if sett not in settori:
            settori.append(sett)
            insertDataDB.insertInSector(str(sett), cur, conn)

    
    print(settori)

    print(len(key_diz))

    # Ritorna il dizionario con i simboli e il settore di appartenenza
    return diz




# Codice eseguibile solo se il file è eseguito come script principale
if __name__ == '__main__':
    # Effettua il login su MetaTrader5 usando le credenziali dal modulo session_management
    #session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)

    # Ottieni i simboli dal file CSV
    #symbols = symbolsNasdaqCSV()
    #print(symbols)
    
    # Ottieni i simboli accettati dal broker Tickmill
    #symbolsAccepted = getSymbolsAcceptedByTickmill()
    #print(len(symbolsAccepted))

    # Ottieni i simboli ordinati per capitalizzazione di mercato
    # getSymbolsCapDesc()

    sector = getSectorSymbols()
    print(sector)