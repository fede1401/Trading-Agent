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
#import torch  # PyTorch per calcoli su GPU (se applicabile)




def main():
    cur, conn = connectDB.connect_nasdaq()
    #datesToTrade1 = utils.generateiRandomDates2(cur, 100)
    
    """cur.execute("select initial_date, end_date from testing where id=1 order by initial_date;")
    datesToTrade1 = {(d[0].strftime('%Y-%m-%d %H:%M:%S'), d[0], d[1].strftime('%Y-%m-%d %H:%M:%S')) for d in cur.fetchall()} 
    datesToTrade1 = list(datesToTrade1)
    datesToTrade1.append(('2008-11-17 00:00:00', datetime.strptime('2008-11-17 00:00:00', '%Y-%m-%d %H:%M:%S'), '2009-11-17 00:00:00'))
    datesToTrade1.append(('2023-05-19 00:00:00', datetime.strptime('2023-05-19 00:00:00', '%Y-%m-%d %H:%M:%S'), '2023-05-19 00:00:00'))
    print(datesToTrade1)
    """
    datesToTrade1 = [('1992-08-12 00:00:00', datetime(1992, 8, 12, 0, 0), '1993-08-12 00:00:00'), ('1999-10-05 00:00:00', datetime(1999, 10, 5, 0, 0), '2000-10-05 00:00:00'), ('2000-06-13 00:00:00', datetime(2000, 6, 13, 0, 0), '2001-06-13 00:00:00'), ('2001-01-08 00:00:00', datetime(2001, 1, 8, 0, 0), '2002-01-08 00:00:00'), ('2001-04-11 00:00:00', datetime(2001, 4, 11, 0, 0), '2002-04-11 00:00:00'), ('2001-08-22 00:00:00', datetime(2001, 8, 22, 0, 0), '2002-08-22 00:00:00'), ('2002-02-19 00:00:00', datetime(2002, 2, 19, 0, 0), '2003-02-19 00:00:00'), ('2002-08-13 00:00:00', datetime(2002, 8, 13, 0, 0), '2003-08-13 00:00:00'), ('2004-11-26 00:00:00', datetime(2004, 11, 26, 0, 0), '2005-11-26 00:00:00'), ('2004-12-17 00:00:00', datetime(2004, 12, 17, 0, 0), '2005-12-17 00:00:00'), ('2005-07-27 00:00:00', datetime(2005, 7, 27, 0, 0), '2006-07-27 00:00:00'), ('2006-07-18 00:00:00', datetime(2006, 7, 18, 0, 0), '2007-07-18 00:00:00'), ('2007-08-27 00:00:00', datetime(2007, 8, 27, 0, 0), '2008-08-27 00:00:00'), ('2008-10-08 00:00:00', datetime(2008, 10, 8, 0, 0), '2009-10-08 00:00:00'), ('2008-10-30 00:00:00', datetime(2008, 10, 30, 0, 0), '2009-10-30 00:00:00'), ('2009-09-10 00:00:00', datetime(2009, 9, 10, 0, 0), '2010-09-10 00:00:00'), ('2009-12-11 00:00:00', datetime(2009, 12, 11, 0, 0), '2010-12-11 00:00:00'), ('2010-02-18 00:00:00', datetime(2010, 2, 18, 0, 0), '2011-02-18 00:00:00'), ('2010-04-12 00:00:00', datetime(2010, 4, 12, 0, 0), '2011-04-12 00:00:00'), ('2010-05-17 00:00:00', datetime(2010, 5, 17, 0, 0), '2011-05-17 00:00:00'), ('2010-05-28 00:00:00', datetime(2010, 5, 28, 0, 0), '2011-05-28 00:00:00'), ('2010-06-25 00:00:00', datetime(2010, 6, 25, 0, 0), '2011-06-25 00:00:00'), ('2010-11-16 00:00:00', datetime(2010, 11, 16, 0, 0), '2011-11-16 00:00:00'), ('2011-02-11 00:00:00', datetime(2011, 2, 11, 0, 0), '2012-02-11 00:00:00'), ('2011-03-15 00:00:00', datetime(2011, 3, 15, 0, 0), '2012-03-15 00:00:00'), ('2011-03-23 00:00:00', datetime(2011, 3, 23, 0, 0), '2012-03-23 00:00:00'), ('2011-08-22 00:00:00', datetime(2011, 8, 22, 0, 0), '2012-08-22 00:00:00'), ('2012-09-25 00:00:00', datetime(2012, 9, 25, 0, 0), '2013-09-25 00:00:00'), ('2013-04-22 00:00:00', datetime(2013, 4, 22, 0, 0), '2014-04-22 00:00:00'), ('2013-09-09 00:00:00', datetime(2013, 9, 9, 0, 0), '2014-09-09 00:00:00'), ('2013-12-11 00:00:00', datetime(2013, 12, 11, 0, 0), '2014-12-11 00:00:00'), ('2013-12-12 00:00:00', datetime(2013, 12, 12, 0, 0), '2014-12-12 00:00:00'), ('2014-04-21 00:00:00', datetime(2014, 4, 21, 0, 0), '2015-04-21 00:00:00'), ('2014-12-08 00:00:00', datetime(2014, 12, 8, 0, 0), '2015-12-08 00:00:00'), ('2014-12-26 00:00:00', datetime(2014, 12, 26, 0, 0), '2015-12-26 00:00:00'), ('2015-02-24 00:00:00', datetime(2015, 2, 24, 0, 0), '2016-02-24 00:00:00'), ('2015-02-26 00:00:00', datetime(2015, 2, 26, 0, 0), '2016-02-26 00:00:00'), ('2015-05-07 00:00:00', datetime(2015, 5, 7, 0, 0), '2016-05-07 00:00:00'), ('2015-08-21 00:00:00', datetime(2015, 8, 21, 0, 0), '2016-08-21 00:00:00'), ('2015-11-11 00:00:00', datetime(2015, 11, 11, 0, 0), '2016-11-11 00:00:00'), ('2016-04-18 00:00:00', datetime(2016, 4, 18, 0, 0), '2017-04-18 00:00:00'), ('2016-06-21 00:00:00', datetime(2016, 6, 21, 0, 0), '2017-06-21 00:00:00'), ('2017-07-06 00:00:00', datetime(2017, 7, 6, 0, 0), '2018-07-06 00:00:00'), ('2017-08-31 00:00:00', datetime(2017, 8, 31, 0, 0), '2018-08-31 00:00:00'), ('2017-09-20 00:00:00', datetime(2017, 9, 20, 0, 0), '2018-09-20 00:00:00'), ('2017-10-10 00:00:00', datetime(2017, 10, 10, 0, 0), '2018-10-10 00:00:00'), ('2018-03-08 00:00:00', datetime(2018, 3, 8, 0, 0), '2019-03-08 00:00:00'), ('2018-06-19 00:00:00', datetime(2018, 6, 19, 0, 0), '2019-06-19 00:00:00'), ('2018-08-31 00:00:00', datetime(2018, 8, 31, 0, 0), '2019-08-31 00:00:00'), ('2018-10-10 00:00:00', datetime(2018, 10, 10, 0, 0), '2019-10-10 00:00:00'), ('2018-11-23 00:00:00', datetime(2018, 11, 23, 0, 0), '2019-11-23 00:00:00'), ('2018-12-24 00:00:00', datetime(2018, 12, 24, 0, 0), '2019-12-24 00:00:00'), ('2019-02-12 00:00:00', datetime(2019, 2, 12, 0, 0), '2020-02-12 00:00:00'), ('2019-03-18 00:00:00', datetime(2019, 3, 18, 0, 0), '2020-03-18 00:00:00'), ('2019-04-03 00:00:00', datetime(2019, 4, 3, 0, 0), '2020-04-03 00:00:00'), ('2019-07-19 00:00:00', datetime(2019, 7, 19, 0, 0), '2020-07-19 00:00:00'), ('2019-08-23 00:00:00', datetime(2019, 8, 23, 0, 0), '2020-08-23 00:00:00'), ('2019-09-27 00:00:00', datetime(2019, 9, 27, 0, 0), '2020-09-27 00:00:00'), ('2019-10-04 00:00:00', datetime(2019, 10, 4, 0, 0), '2020-10-04 00:00:00'), ('2019-10-22 00:00:00', datetime(2019, 10, 22, 0, 0), '2020-10-22 00:00:00'), ('2019-12-09 00:00:00', datetime(2019, 12, 9, 0, 0), '2020-12-09 00:00:00'), ('2020-05-12 00:00:00', datetime(2020, 5, 12, 0, 0), '2021-05-12 00:00:00'), ('2020-06-29 00:00:00', datetime(2020, 6, 29, 0, 0), '2021-06-29 00:00:00'), ('2020-07-01 00:00:00', datetime(2020, 7, 1, 0, 0), '2021-07-01 00:00:00'), ('2020-07-22 00:00:00', datetime(2020, 7, 22, 0, 0), '2021-07-22 00:00:00'), ('2020-10-12 00:00:00', datetime(2020, 10, 12, 0, 0), '2021-10-12 00:00:00'), ('2020-10-29 00:00:00', datetime(2020, 10, 29, 0, 0), '2021-10-29 00:00:00'), ('2020-12-11 00:00:00', datetime(2020, 12, 11, 0, 0), '2021-12-11 00:00:00'), ('2021-06-25 00:00:00', datetime(2021, 6, 25, 0, 0), '2022-06-25 00:00:00'), ('2021-08-04 00:00:00', datetime(2021, 8, 4, 0, 0), '2022-08-04 00:00:00'), ('2021-09-29 00:00:00', datetime(2021, 9, 29, 0, 0), '2022-09-29 00:00:00'), ('2021-10-05 00:00:00', datetime(2021, 10, 5, 0, 0), '2022-10-05 00:00:00'), ('2021-10-11 00:00:00', datetime(2021, 10, 11, 0, 0), '2022-10-11 00:00:00'), ('2021-11-10 00:00:00', datetime(2021, 11, 10, 0, 0), '2022-11-10 00:00:00'), ('2022-01-11 00:00:00', datetime(2022, 1, 11, 0, 0), '2023-01-11 00:00:00'), ('2022-01-26 00:00:00', datetime(2022, 1, 26, 0, 0), '2023-01-26 00:00:00'), ('2022-02-03 00:00:00', datetime(2022, 2, 3, 0, 0), '2023-02-03 00:00:00'), ('2022-04-06 00:00:00', datetime(2022, 4, 6, 0, 0), '2023-04-06 00:00:00'), ('2022-04-18 00:00:00', datetime(2022, 4, 18, 0, 0), '2023-04-18 00:00:00'), ('2022-06-02 00:00:00', datetime(2022, 6, 2, 0, 0), '2023-06-02 00:00:00'), ('2022-06-08 00:00:00', datetime(2022, 6, 8, 0, 0), '2023-06-08 00:00:00'), ('2022-06-08 00:00:00', datetime(2022, 6, 8, 0, 0), '2023-06-08 00:00:00'), ('2022-06-17 00:00:00', datetime(2022, 6, 17, 0, 0), '2023-06-17 00:00:00'), ('2022-06-23 00:00:00', datetime(2022, 6, 23, 0, 0), '2023-06-23 00:00:00'), ('2022-07-19 00:00:00', datetime(2022, 7, 19, 0, 0), '2023-07-19 00:00:00'), ('2022-08-17 00:00:00', datetime(2022, 8, 17, 0, 0), '2023-08-17 00:00:00'), ('2022-09-09 00:00:00', datetime(2022, 9, 9, 0, 0), '2023-09-09 00:00:00'), ('2022-09-19 00:00:00', datetime(2022, 9, 19, 0, 0), '2023-09-19 00:00:00'), ('2023-01-19 00:00:00', datetime(2023, 1, 19, 0, 0), '2024-01-19 00:00:00'), ('2023-01-23 00:00:00', datetime(2023, 1, 23, 0, 0), '2024-01-23 00:00:00'), ('2023-02-02 00:00:00', datetime(2023, 2, 2, 0, 0), '2024-02-02 00:00:00'), ('2023-03-20 00:00:00', datetime(2023, 3, 20, 0, 0), '2024-03-20 00:00:00'), ('2023-03-30 00:00:00', datetime(2023, 3, 30, 0, 0), '2024-03-30 00:00:00'), ('2023-05-04 00:00:00', datetime(2023, 5, 4, 0, 0), '2024-05-04 00:00:00'), ('2023-05-04 00:00:00', datetime(2023, 5, 4, 0, 0), '2024-05-04 00:00:00'), ('2023-06-30 00:00:00', datetime(2023, 6, 30, 0, 0), '2024-06-30 00:00:00'), ('2023-08-28 00:00:00', datetime(2023, 8, 28, 0, 0), '2024-08-28 00:00:00'), ('2023-08-30 00:00:00', datetime(2023, 8, 30, 0, 0), '2024-08-30 00:00:00'), ('2023-10-10 00:00:00', datetime(2023, 10, 10, 0, 0), '2024-10-10 00:00:00'), ('2023-11-17 00:00:00', datetime(2023, 11, 17, 0, 0), '2024-11-17 00:00:00')]


    print(datesToTrade1)

    cur.close()
    conn.close()

    #device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    #print(f"Using device: {device}")

    # Esempio: Allocazione di dati su GPU
    #data = torch.tensor([1.0, 2.0, 3.0], device=device)
    #result = data * 2  # Operazione GPU

    agent2.main_agent2_purchaseALL.main(datesToTrade1) # 23:23:27,064 6 gennaio
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


