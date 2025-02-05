from pathlib import Path
import csv
import pandas as pd

"""
# Percorso assoluto dello script corrente
project_root = Path(__file__).resolve()

# Risali finché non trovi 'Trading-Agent'
while project_root.name != 'Trading-Agent':
    if project_root == project_root.root:  # Se arrivi alla root del file system
        print("You are not in the right directory")
        break
    project_root = project_root.parent  # Risali di un livello

print(f"Project root: {project_root}")  # Debugging


sys.path.append(str(project_root) + '/db')  #sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
sys.path.append(str(project_root))   #sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')


"""

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
get_path_specify(["db"])
from db import connectDB, insertDataDB




def getSectorSymbols():
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    
    symbolsAccepted = ['AAL', 'AAPL', 'ABNB', 'ACAD', 'ACGL', 'ACIW', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AGIO', 'AKAM', 'ALGN', 'ALRM', 'AMAT', 'AMD', 'AMED', 
               'AMGN', 'AMKR', 'AMZN', 'APLS', 'APPS', 'ARWR', 'ATSG', 'AVGO', 'AZN', 'BCRX', 'BIDU', 'BILI', 'BKNG', 'BL', 'BLMN', 'BMBL', 'BMRN', 
               'BNTX', 'BPMC', 'BRKR', 'CAKE', 'CALM', 'CAR', 'CARG', 'CBRL', 'CDNS', 'CDW', 'CG', 'CGNX', 'CMCSA', 'CME', 'COIN', 'COLM', 'CORT', 
               'COST', 'CROX', 'CRSP', 'CRWD', 'CSCO', 'CSIQ', 'CTAS', 'CTSH', 'CYRX', 'CYTK', 'CZR', 'DASH', 'DBX', 'DDOG', 'DKNG', 'DLO', 'DLTR', 
               'DNLI', 'DOCU', 'EA', 'EBAY', 'EEFT', 'ENPH', 'ENTA', 'ENTG', 'ERII', 'ETSY', 'EVBG', 'EXAS', 'EXPE', 'EYE', 'FANG', 'FAST', 'FIVE', 
               'FLEX', 'FOLD', 'FORM', 'FOX', 'FRPT', 'FSLR', 'FTNT', 'GBDC', 'GDS', 'GH', 'GILD', 'GLNG', 'GLPI', 'GOGL', 'GOOGL', 'GPRE', 'GPRO', 
               'GTLB', 'HAIN', 'HCM', 'HCSG', 'HIBB', 'HOOD', 'HQY', 'HTHT', 'IART', 'IBKR', 'ICLR', 'ILMN', 'INCY', 'INSM', 'INTC', 'IOVA', 'IRDM', 
               'IRTC', 'IRWD', 'ISRG', 'ITRI', 'JACK', 'JD', 'KLIC', 'KRNT', 'KTOS', 'LAUR', 'LBRDK', 'LBTYA', 'LI', 'LITE', 'LIVN', 'LNT', 'LNTH', 
               'LOGI', 'LOPE', 'LPLA', 'LPSN', 'LRCX', 'LSCC', 'LYFT', 'MANH', 'MAR', 'MASI', 'MDB', 'MDLZ', 'MEDP', 'MEOH', 'META', 'MKSI', 'MMSI', 
               'MNRO', 'MNST', 'MPWR', 'MRCY', 'MRNA', 'MSFT', 'MSTR', 'MTCH', 'MTSI', 'MU', 'MYGN', 'NAVI', 'NBIX', 'NDAQ', 'NEOG', 'NFLX', 'NMIH', 
               'NSIT', 'NTCT', 'NTES', 'NTNX', 'NTRA', 'NVCR', 'NVDA', 'NWSA', 'ODP', 'OKTA', 'OLLI', 'OMCL', 'ORLY', 'PAYX', 'PCH', 'PDD', 'PEGA', 
               'PENN', 'PEP', 'PGNY', 'PLAY', 'PLUG', 'POOL', 'POWI', 'PPC', 'PRAA', 'PRGS', 'PTC', 'PTCT', 'PTEN', 'PTON', 'PYPL', 'PZZA', 'QCOM', 
               'QDEL', 'QFIN', 'QLYS', 'RARE', 'RCM', 'REG', 'REGN', 'REYN', 'RGEN', 'RIVN', 'RMBS', 'ROIC', 'ROKU', 'RPD', 'RRR', 'RUN', 'SAGE', 
               'SAIA', 'SANM', 'SBAC', 'SBGI', 'SBLK', 'SBRA', 'SBUX', 'SEDG', 'SFM', 'SGRY', 'SHOO', 'SKYW', 'SLM', 'SMTC', 'SONO', 'SPWR', 'SRCL', 
               'SRPT', 'SSRM', 'STX', 'SWKS', 'SYNA', 'TMUS', 'TRIP', 'TRMB', 'TROW', 'TSCO', 'TSLA', 'TTEK', 'TTMI', 'TTWO', 'TXG', 'TXRH', 'UAL', 
               'UCTT', 'URBN', 'VCYT', 'VECO', 'VIAV', 'VIRT', 'VRNS', 'VRNT', 'VRSK', 'VRSN', 'VRTX', 'VSAT', 'WB', 'WDC', 'WERN', 'WING', 'WIX', 
               'WMG', 'WSC', 'WSFS', 'WWD', 'XP', 'XRAY', 'YY', 'ZD', 'ZG', 'ZI', 'ZLAB', 'ZM']

    # Dizionario per memorizzare i simboli e il settore di appartenenza
    diz = dict()

    # Leggi il file CSV in un DataFrame
    df = pd.read_csv(f'{market_data_path}/csv_files/nasdaq_symbols.csv')

    # Apri il file CSV in modalità lettura
    with open(f'{market_data_path}/csv_files/nasdaq_symbols.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            if col['Symbol'] in symbolsAccepted:
                diz[col['Symbol']] = col['Sector']

    # Ottieni le chiavi del dizionario (i simboli)
    key_diz = list(diz.keys())

    print(diz.keys())
    
    cur.execute("SELECT * FROM sector;")
    sectorsDB = [ sec[0] for sec in cur.fetchall() ]  # Estrai solo il primo elemento di ogni tupla
    
    settori = list(set(diz.values()))
                
    for sett in settori:
        if sett != '':
            if sett not in sectorsDB:
                insertDataDB.insertInSector(str(sett), cur, conn)
    print(settori)

    print(len(key_diz))
    
    cur.close()
    conn.close()
    
    print(diz)

    # Ritorna il dizionario con i simboli e il settore di appartenenza
    return diz, sectorsDB




def getSectorNasdaq():
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    
    # Dizionario per memorizzare i simboli e il settore di appartenenza
    diz = dict()
    
    # Leggi il file CSV in un DataFrame
    #df = pd.read_csv('../marketData/csv_files/nasdaq_symbols_sorted.csv')

    # Apri il file CSV in modalità lettura
    #with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols.csv', mode='r') as file:
    with open(f'{market_data_path}/csv_files/nasdaq_symbols.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            diz[col['Symbol']] = col['Sector']

    # Ottieni le chiavi del dizionario (i simboli)
    key_diz = list(diz.keys())

    print(diz.keys())
    
    cur.execute("SELECT * FROM sectorNasdaq;")
    sectorsDB = [ sec[0] for sec in cur.fetchall() ]  # Estrai solo il primo elemento di ogni tupla
    
    settori = list(set(diz.values()))
                
    for sett in settori:
        if sett != '':
            if sett not in sectorsDB:
                insertDataDB.insertInSector(str(sett), cur, conn)
    print(settori)

    print(len(key_diz))
    
    cur.close()
    conn.close()
    
    print(diz)

    # Ritorna il dizionario con i simboli e il settore di appartenenza
    return diz, sectorsDB
    


def getSectorNyse():
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    
    # Dizionario per memorizzare i simboli e il settore di appartenenza
    diz = dict()
    
    # Leggi il file CSV in un DataFrame
    #df = pd.read_csv('../marketData/csv_files/nasdaq_symbols_sorted.csv')

    # Apri il file CSV in modalità lettura
    with open(f'{market_data_path}/csv_files/nasdaq_symbols.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            diz[col['Symbol']] = col['Sector']

    # Ottieni le chiavi del dizionario (i simboli)
    key_diz = list(diz.keys())

    print(diz.keys())
    
    cur.execute("SELECT * FROM sectorNyse;")
    sectorsDB = [ sec[0] for sec in cur.fetchall() ]  # Estrai solo il primo elemento di ogni tupla
    
    settori = list(set(diz.values()))
                
    for sett in settori:
        if sett != '':
            if sett not in sectorsDB:
                insertDataDB.insertInSectorNyse(str(sett), cur, conn)
    print(settori)

    print(len(key_diz))
    
    cur.close()
    conn.close()
    
    print(diz)

    # Ritorna il dizionario con i simboli e il settore di appartenenza
    return diz, sectorsDB
    







if __name__ == "__main__":
    #getSectorSymbols()
    getSectorNasdaq()
    getSectorNyse()
    