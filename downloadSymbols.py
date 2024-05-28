import MetaTrader5 as mt5
from datetime import datetime
import psycopg2 # https://www.youtube.com/watch?v=miEFm1CyjfM

import login_mt5, closeConnectionMt5, downloadData


############ variabili programma ###################
path = 'C:\\Program Files\\MetaTrader 5\\terminal64.exe'
login = 25114472
password = 'j8+fCg&E2A_('
server = 'TickmillEU-Demo'
#############################################


login_mt5.login_metaTrader5(login, password, server)


############ Ottenimento dati Apple e scrittura su file esterno ###################

# Specificare il simbolo dell'azione (ad esempio, 'AAPL' per Apple)
symbol = "AAPL"

# Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri)
timeframe = mt5.TIMEFRAME_D1

# Specificare l'intervallo di tempo
start_date = datetime(2024, 5, 20)
end_date = datetime.now()

downloadData.downloadData(symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date, file="\\fileTXT\\")
#############################################



############ Ottenimento dati indice Nasdaq e scrittura su file esterno ###################

# Specificare il simbolo dell'azione (ad esempio, 'AAPL' per Apple)
symbol = "NDAQ"

# Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri)
timeframe = mt5.TIMEFRAME_D1

# Specificare l'intervallo di tempo
start_date = datetime(1996, 1, 1)
end_date = datetime.now()

downloadData.downloadData(symbol=symbol, timeframe=timeframe, start_date=start_date, end_date=end_date, file="\\fileTXT\\")
#############################################




# Chiudere la connessione
closeConnectionMt5.closeConnection()

