import MetaTrader5 as mt5
from datetime import datetime


# Vengono definite delle variabili necessarie per il login alla piattaforma MetaTrader5
# Se l'inizializzazione e la connessione non vanno a buon fine c'è un messaggio di errore, altrimenti
# vengono scritte su un file le informazioni dell'account e della piattaforma MetaTrader5


############ variabili programma ###################
# path = 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
# login = 25114472
# password = 'j8+fCg&E2A_('
# server = 'TickmillEU-Demo'
#############################################



def login_metaTrader5(account, password, server):
    if not mt5.initialize(): # Questa funzione inizializza la libreria MetaTrader 5.
        print("Failed to initialize, error code: ", mt5.last_error())
        return False
    
    else:  
        # Tentiamo di effettuare il login a MT5 utilizzando le credenziali fornite (login, password e server). 
        if not mt5.login(account, password=password, server=server):
            print("Failed to login, error code: ", mt5.last_error())
            return False
        
        else:
            account_info = mt5.account_info()
            
            with open('fileTXT\\info_account.txt', 'w') as file:
                file.write(str(account_info))

            print(account_info)

    # dislay data on connection status, server name and trading account
    #print(mt5.terminal_info())
    
    # display data on MetaTrader 5 version
    #print(mt5.version())

    with open('fileTXT\\sessione.txt', 'w') as file:
        # write data about connection status, server name and trading account
        file.write(f"{datetime.now()} {mt5.terminal_info()}\n")
        
        # write data about MetaTrader 5 version
        file.write(f"{datetime.now()} {mt5.version()}\n")

    return True