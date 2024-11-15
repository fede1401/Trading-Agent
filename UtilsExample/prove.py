
"""
b = 1
a = 9
c = 2

while True:

    for i in range(0, 4):
        if (b==1):

            if (a == 9):
                print("Uguale a 9")
                a = 2
                c = 4
                continue

            if (a == 9):
                print("ciao")

        if (c== 4):
            print("ciao2")
"""
import MetaTrader5 as mt5
from datetime import datetime
import session_management, info_order_send,symbols.symbolsAcceptedByTickmill as symbolsAcceptedByTickmill, db.connectDB as connectDB, accountInfo, db.insertDataDB as insertDataDB, agentState
import psycopg2
import time
import random
import logging
import pytz
from datetime import datetime, time, timedelta
import time as time_module
import csv
import agent2.agent2 as agent2



# Connessione al server MetaTrader 5 e login e salvataggio nel db per lo storico dei login.        
session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)
        
# Ottenimento operazioni di trading attualmente in corso tramite simbolo azionario
positions = mt5.positions_get(symbol='AMZN')
print(positions)
if positions is not None:

# Per ogni posizione di quell'azione:
    for pos in positions:
        logging.info(f"{pos}\n")


# import MetaTrader5 as mt5
# from datetime import datetime, timedelta
# import psycopg2 
# import numpy as np
# import closeConnectionMt5, login, connectDB, downloadData
# import logging
# import variableLocal
# import login, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send,symbolsAcceptedByTickmill, connectDB, accountInfo, insertDataDB, agentState
# import time
# import random
# import logging
# import pytz
# from datetime import datetime, time, timedelta
# import time as time_module



# # connessione al server MetaTrader 5 e login
# login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)


# # connessione al database
# cur, conn = connectDB.connect_nasdaq()


# # Recupera lo stato dell'agente nel database:
# cur.execute("SELECT ticket FROM Sale")
# salesDB = cur.fetchall()

# sales = []
# for sale in salesDB:
#     sales.append(sale[0])

# a1 = '46206133'
# a2 = '46206134'

# for sal in sales:
#     if sal == a1:
#         print("ciao")
    
#     if sal == a2:
#         print("ciao2")


"""

-----------------------------------------------------------------------------------------------
import MetaTrader5 as mt5
from datetime import datetime


# Specificare il simbolo dell'azione (ad esempio, 'AAPL' per Apple)
#symbol = "AAPL"

# Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri)
#timeframe = mt5.TIMEFRAME_D1

# Specificare l'intervallo di tempo
#start_date = datetime(2024, 5, 20)
#end_date = datetime.now()

############ Ottenimento dati e scrittura su file esterno ###################
def downloadData(symbol, timeframe, start_date, end_date, file ):
    # Ottenere i dati storici
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

    with open('data.txt', 'a') as file1:
        file1.write(f"\n\n{symbol}: \n\n{datetime.now()}\n")

    # Controllare se abbiamo ottenuto i dati
    if rates is None:
        print("No data retrieved")
    else:
        count = 0
        for rate in rates:
            print(rate)
            count += 1
            with open(file, 'a') as file1:
                file1.write(f"{count }: {str(rate)}")
                file1.write('\n')

    return True


-----------------------------------------------------------------------------------------------

import MetaTrader5 as mt5
from datetime import datetime
import session_management, downloadAndInsertDataDB, info_order_send, symbolsAcceptedByTickmill
import psycopg2
import time
import numpy as np
import logging



if __name__ == '__main__':

    # Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri, mt5.TIMEFRAME_M15 ogni 15 minuti)
    timeframe = mt5.TIMEFRAME_M15

    session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)
    symbol = 'AAPL'

    start_date = datetime(2024, 7, 8)
    end_date = datetime(2024, 7, 9)


    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date) 
    print()

    for rate in rates:
        print(rate)
        print(datetime.fromtimestamp(rate['time']))



-----------------------------------------------------------------------------------------------
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)



from datetime import datetime, time, timedelta
import time as time_module
import pytz


# Get the timezone object for New York
tz_NY = pytz.timezone('America/New_York') 

# Get the current time in New York
datetime_NY = datetime.now(tz_NY)

print(datetime_NY.hour, datetime_NY.minute, datetime_NY.second)

# Format the time as a string and print it
print("NY time:", datetime_NY.strftime("%H:%M:%S"))


if (datetime_NY.hour >= 3) & (datetime_NY.hour < 9):
    if (datetime_NY.hour == 3):
        if datetime_NY.minute >= 30:
            print("It's Okay!")



def wait(target_time):
    try:
        # Get the timezone object for New York
        tz_NY = pytz.timezone('America/New_York') 

        # Get the current time in New York
        datetime_NY = datetime.now(tz_NY)

        sleep_duration = (target_time - datetime_NY).total_seconds()

        print(sleep_duration)

        if sleep_duration > 0:
            print(f"Il programma si interromperà fino a: {target_time}")
            time_module.sleep(sleep_duration)
            print("Il programma ha ripreso l'esecuzione.")
        else:
            print("Il tempo target è già passato.")
    except Exception as e:
        print(f"Errore durante l'attesa: {e}")


if __name__ == '__main__':
    try:
        specified_time = time(4, 56)  # Ad esempio, 9:30

        # Get the timezone object for New York
        tz_NY = pytz.timezone('America/New_York') 

        # Get the current time in New York
        datetime_NY = datetime.now(tz_NY)

        target_time = tz_NY.localize(datetime.combine(datetime_NY.date(), specified_time))
        
        print(target_time)
        print()

        # Se l'orario specificato è già passato per oggi, imposta l'orario per il giorno successivo
        if target_time < datetime_NY:
            target_time += timedelta(days=1)

        wait(target_time)

    except Exception as e:
        print(f"Errore durante l'impostazione dell'orario target: {e}")



# Get the timezone object for London
tz_London = pytz.timezone('Europe/London')

# Get the current time in London
datetime_London = datetime.now(tz_London)

# Format the time as a string and print it
print("London time:", datetime_London.strftime("%H:%M:%S"))

#print(set(pytz.all_timezones_set)  )

# Get the timezone for Italy
tz_Italy = pytz.timezone('Europe/Rome')

# Get the current time in Italy
datetime_Italy = datetime.now(tz_Italy)

# Format the time as a string and print it
print("Rome time:", datetime_Italy.strftime("%H:%M:%S"))


"""