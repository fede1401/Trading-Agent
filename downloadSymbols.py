import MetaTrader5 as mt5
from datetime import datetime
import psycopg2 # https://www.youtube.com/watch?v=miEFm1CyjfM

import login, closeConnectionMt5, downloadData, variableLocal


login.login_metaTrader5(variableLocal.login, variableLocal.password, variableLocal.server)


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

