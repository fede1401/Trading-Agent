import sys

import agent2.main_agent2_purchaseALL
import agent3.agent3_SimulationMulMarket
import agent4.agent4_simulation
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical/agent1_downloadANDinsertDATA_DB')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical/agent2')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical/agent3')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical/agent4')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical/agent5_variationNumberTitle')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical/agent6_selectionSector')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical')


import agent2 as agent2
import agent3 as agent3
import agent4 as agent4
import utils
import agent5_variationNumberTitle as agent5
from agent5_variationNumberTitle import main_agent5 as agent5
from agent6_selectionSector import main_agent6 as agent6
import agentState
from db import insertDataDB, connectDB
from symbols import getSector, getSymbols
import logging
from datetime import datetime, time, timedelta
import time as time_module
import csv
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np




def main():
    cur, conn = connectDB.connect_nasdaq()
    datesToTrade1 = utils.generateiRandomDates2(cur, 100)
    
    """cur.execute("select initial_date, end_date from testing where id=1 order by initial_date;")
    datesToTrade1 = {(d[0].strftime('%Y-%m-%d %H:%M:%S'), d[0], d[1].strftime('%Y-%m-%d %H:%M:%S')) for d in cur.fetchall()} 
    datesToTrade1 = list(datesToTrade1)
    datesToTrade1.append(('2008-11-17 00:00:00', datetime.strptime('2008-11-17 00:00:00', '%Y-%m-%d %H:%M:%S'), '2009-11-17 00:00:00'))
    datesToTrade1.append(('2023-05-19 00:00:00', datetime.strptime('2023-05-19 00:00:00', '%Y-%m-%d %H:%M:%S'), '2023-05-19 00:00:00'))
    print(datesToTrade1)
    """

    print(datesToTrade1)
    
    insertDataDB.insertInMiddleProfit(0, "------", roi=0, devstandard = 0, var= 0, middleProfitUSD =0,
                                                  middleSale = 0, middlePurchase = 0, middleTimeSale = 0, middletitleBetterProfit = '----',
                                                    middletitleWorseProfit = 0, notes='---', cur=cur, conn=conn)
    cur.close()
    conn.close()

    agent2.main_agent2_purchaseALL.main(datesToTrade1)
    ###########################
    agent3.agent3_SimulationMulMarket.main(datesToTrade1)
    ###########################
    agent4.agent4_simulation.main(datesToTrade1)
    ###########################
    agent5.main(datesToTrade1)
    ###########################
    
    dizNasdaq = dict()
    # Apri il file CSV in modalità lettura
    with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            if col['Sector'] not in dizNasdaq:
                dizNasdaq[col['Sector']] = [col['Symbol']]
            else:
                dizNasdaq[col['Sector']].append(col['Symbol'])
                
    #print(dizNasdaq)
    
    for sector in dizNasdaq:
        print(f"{sector}: {len(dizNasdaq[sector])}\n")
            
    ##############################
    
    # Analogo per Nyse
    
    print("\n")
    
    dizNyse = dict()
    # Apri il file CSV in modalità lettura
    with open('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/marketData/csv_files/nyse_symbols_sorted.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            if col['Sector'] not in dizNyse:
                dizNyse[col['Sector']] = [col['Symbol']]
            else:
                dizNyse[col['Sector']].append(col['Symbol'])
                
    #print(dizNyse)
    
    for sector in dizNyse:
        print(f"{sector}: {len(dizNyse[sector])}\n")
    
    agent6.main(datesToTrade1, dizNasdaq, dizNyse, perc=0.5)
    
    print("Fine simulazione")
    return

if __name__ == '__main__':
    main()


