

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

