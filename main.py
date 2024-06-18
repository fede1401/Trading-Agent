import MetaTrader5 as mt5
from datetime import datetime
import psycopg2 # https://www.youtube.com/watch?v=miEFm1CyjfM
import numpy as np
import closeConnectionMt5, login, connectDB, downloadData, downloadAndInsertDataDB, variableLocal


############################################
# Specificare il simbolo dell'azione (ad esempio, 'AAPL' per Apple, 'NFLX' per Netflix)
symbol = "NFLX"

# Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri)
timeframe = mt5.TIMEFRAME_D1

# Specificare l'intervallo di tempo
start_date = datetime(2000, 5, 25)
end_date = datetime.now()

file = 'dati_Apple.txt'
############################################


def main():
    if login.login_metaTrader5(variableLocal.account, variableLocal.password, variableLocal.server):
        downloadAndInsertDataDB.downloadInsertDB_data(symbol, timeframe, start_date, end_date)
        closeConnectionMt5.closeConnection()



if __name__ == '__main__':
    main()
    #connectDB()