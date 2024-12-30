
import pandas as pd
import csv
import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData')


    
    
    
# Funzione per leggere i simboli Nasdaq da un file CSV
def symbolsNyseCSV():    
    # Apri il file CSV in modalità lettura
    with open('csv_files/nyse_symbols.csv', mode='r') as file:
        
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
    
        # Inizializza una lista vuota per memorizzare i simboli
        symbols =[]

        # Aggiungi ogni simbolo dalla colonna 'Symbol' del CSV alla lista
        for col in csv_reader:
            symbols.append(col['Symbol']) 

    # Ritorna la lista dei simboli
    return symbols


# Funzione per ottenere i simboli ordinati per capitalizzazione di mercato in ordine decrescente
def getSymbolsNYSECapDesc():
    # Ottieni i simboli accettati dal broker Tickmill
    symbolsAccepted = symbolsNyseCSV()
    #print(symbolsAccepted)

    # Dizionario per memorizzare i simboli e la loro capitalizzazione di mercato
    diz = dict()

    # Leggi il file CSV in un DataFrame
    df = pd.read_csv('csv_files/nyse_symbols.csv')

    # Ordina il DataFrame in base alla colonna 'Market Cap' in ordine decrescente
    df_sorted = df.sort_values(by='Market Cap', ascending=False)

    # Salva il DataFrame ordinato in un nuovo file CSV
    df_sorted.to_csv('csv_files/nyse_symbols_sorted.csv', index=False)

    # Apri il file CSV ordinato in modalità lettura
    with open('csv_files/nyse_symbols_sorted.csv', mode='r') as file:
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


    
# Funzione per ottenere i tot simboli della borsa del Nasdaq in ordine di capitalizzazione di mercato decrescente.
def getSymbolsNasdaq(i):
    # Apri il file CSV in modalità lettura
    with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
    #with open('marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file: # se dobbiamo utilizzarlo per il file agent1_YAHOO!Finance.py, altrimenti: with open('../marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:


        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
    
        # Inizializza una lista vuota per memorizzare i simboli
        symbols =[]

        # Aggiungi ogni simbolo dalla colonna 'Symbol' del CSV alla lista
        for col in csv_reader:
            symbols.append(col['Symbol']) 
            if len(symbols) == i:
                break
    # Ritorna la lista dei simboli
    return symbols
    
    
def getSymbolsNyse(i):
    # Apri il file CSV in modalità lettura
    with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nyse_symbols_sorted.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
    
        # Inizializza una lista vuota per memorizzare i simboli
        symbols =[]

        # Aggiungi ogni simbolo dalla colonna 'Symbol' del CSV alla lista
        for col in csv_reader:
            symbols.append(col['Symbol']) 
            if len(symbols) == i:
                break
    # Ritorna la lista dei simboli
    return symbols


def getSymbolsLargestCompEU(i):
    # Apri il file CSV in modalità lettura
    with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/largest_companies_EU.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
    
        # Inizializza una lista vuota per memorizzare i simboli
        symbols =[]

        # Aggiungi ogni simbolo dalla colonna 'Symbol' del CSV alla lista
        for col in csv_reader:
            symbols.append(col['Symbol']) 
            if len(symbols) == i:
                break
    # Ritorna la lista dei simboli
    return symbols
    
    

#symbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX']
#symbols = ['AAPL', 'MSFT', 'ADBE', 'AMD', 'COST', 'AZN', 'ADBE', 'CMCSA', 'QCOM', 'TMUS', 'MU']

if __name__ == '__main__':
    #symbols_nyse = print(symbolsNyseCSV())
    #symbols_largCompEU = print(symbolsLargestCompEUCSV())
    #symbolsNyseCSV = print(getSymbolsNYSECapDesc())
    #print(getSymbolsNYSECapDesc())
    print(getSymbolsLargestCompEU(100))