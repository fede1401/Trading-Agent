import MetaTrader5 as mt5


############ inizializzazione tool ###################
print(mt5.initialize())
#############################################

# Viene effettuata l'inizializzazione : viene aperta la piattaforma MetaTrader5 (Questa funzione inizializza la libreria MetaTrader 5.)

# Chiudere la connessione
mt5.shutdown()

