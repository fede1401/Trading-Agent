import MetaTrader5 as mt5
from datetime import datetime
import insertDataDB


############ variabili locali programma ###################
path = 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
account = 25142282
password = 'xJ5P=vC,(S|!'
server = 'TickmillEU-Demo'
name = 'Federico Ferdinandi'
#############################################


# Funzione per inizializzare, stabilire una connessione con MetaTrader5 e aprire la piattaforma.
def initializeMT5():
    # Inizializza MetaTrader5 e stampa il risultato dell'inizializzazione
    print(mt5.initialize())

    # Chiude la connessione dopo l'inizializzazione
    closeConnection()




# Funzione per il login ad un account di trading a MetaTrader5
def login_metaTrader5(account, password, server):

    # Inizializza e stabilisce una connessione con MetaTrader5
    if not mt5.initialize(): 
        # Se l'inizializzazione fallisce, stampa il codice dell'errore e ritorna False
        print("Failed to initialize, error code: ", mt5.last_error())
        return False
    
    else:  
        # Se l'inizializzazione ha successo tentiamo di effettuare il login a MT5 utilizzando le credenziali fornite (login, password e server). 
        if not mt5.login(account, password=password, server=server):
            # Se il login fallisce, stampa il codice dell'errore e ritorna False
            print("Failed to login, error code: ", mt5.last_error())
            return False
        
        else:
            # Se il login ha successo, ottiene le informazioni sull'account
            account_info = mt5.account_info()
            
            # Scrive le informazioni dell'account su un file
            with open('fileTXT\\info_account.txt', 'w') as file:
                file.write(str(account_info))

            # Stampa le informazioni dell'account
            print(account_info)

    # Scrive le informazioni sulla sessione su un file 'sessione.txt'
    with open('fileTXT\\sessione.txt', 'w') as file:
        # Scrive lo stato della connessione, il nome del server e l'account di trading        
        file.write(f"{datetime.now()} {mt5.terminal_info()}\n")
        
        # Scrive la versione di MetaTrader 5
        file.write(f"{datetime.now()} {mt5.version()}\n")

    return True




# Funzione per chiudere la connessione a MetaTrader5
def closeConnection():
    mt5.shutdown()
    print("Connessione chiusa")
