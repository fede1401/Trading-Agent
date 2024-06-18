import csv
import MetaTrader5 as mt5
import login, variableLocal
import pandas as pd


def symbolsNasdaqCSV():    
    # Open the CSV file for reading
    with open('nasdaq_symbols.csv', mode='r') as file:
        # Create a CSV reader with DictReader
        csv_reader = csv.DictReader(file)
    
        # Initialize an empty list to store the dictionaries
        symbols =[]

        for col in csv_reader:
            symbols.append(col['Symbol']) 

    return symbols
    

def getSymbolsAcceptedByTickmill():
    symbols = symbolsNasdaqCSV()

    symbolsAccepted = []
    for s in symbols:
        symbol_info = mt5.symbol_info(s)

        if symbol_info == None:
            continue

        else: # symbolo != None
            if not symbol_info.visible:
                print(s, "is not visible, trying to switch on")
                
                if not mt5.symbol_select(s,True):
                    print("symbol_select({}}) failed, exit",s)
                    continue

                else:
                    symbolsAccepted.append(s)
            
            else:
                symbolsAccepted.append(s)
    return symbolsAccepted        


def getSymbolsCapDesc():
    symbolsTotal = symbolsNasdaqCSV()

    symbolsAccepted = getSymbolsAcceptedByTickmill(symbolsTotal)
    print(symbolsAccepted)

    diz = dict()

    # Leggi il file CSV in un DataFrame
    df = pd.read_csv('nasdaq_symbols.csv')

    # Ordina il DataFrame in base alla colonna desiderata in ordine decrescente
    # Supponiamo che la colonna si chiami 'column_name'
    df_sorted = df.sort_values(by='Market Cap', ascending=False)

    # Salva il DataFrame ordinato in un nuovo file CSV (o sovrascrivi il file esistente)
    df_sorted.to_csv('nasdaq_symbols_sorted.csv', index=False)


    with open('nasdaq_symbols_sorted.csv', mode='r') as file:
        # Create a CSV reader with DictReader
        csv_sort_reader = csv.DictReader(file)

        for col in csv_sort_reader:
            if col['Symbol'] in symbolsAccepted:
                diz [col['Symbol']] = col['Market Cap']

        
        key_diz = list(diz.keys())

            
    print(key_diz)
    print(len(key_diz))

    # print("Intersect:")
    # for element in key_diz:
    #     if element not in symbolsAccepted:
    #         print(element)

    # for element2 in symbolsAccepted:
    #     if element2 not in key_diz:
    #         print(element2)

    return key_diz


def get5PercentSymbolsCapDesc():
    symbol_cap_desc = getSymbolsCapDesc()

    # Calcola il 5% del numero totale di simboli
    n = len(symbol_cap_desc)
    n_5 = int(n * 0.05)

    return symbol_cap_desc[0:n_5]





if __name__ == '__main__':
    login.login_metaTrader5(account=variableLocal.account , password=variableLocal.password, server=variableLocal.server)

    symbols = symbolsNasdaqCSV()
    
    symbolsAccepted = getSymbolsAcceptedByTickmill()
    print(len(symbolsAccepted))

    getSymbolsCapDesc()

