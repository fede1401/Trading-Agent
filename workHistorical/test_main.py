import sys

from datetime import datetime
import csv

#import torch  # PyTorch per calcoli su GPU (se applicabile)
import logging

import os
from pathlib import Path

import agent2.agent2_selectRandom

# Trova dinamicamente la cartella Trading-Agent e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'Trading-Agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

import agent2.agent2_markCapDayInitial
import agent2.agent2_markCapDayPurchase
import workHistorical.agent2.agent2_markCapDayInitial
from config import get_path_specify, project_root

# Ora possiamo importare `config`
get_path_specify(["db", "symbols", "workHistorical", "utils"])

# Importa i moduli personalizzati
from db import connectDB


sys.path.append(f'{current_path}/workHistorical')
sys.path.append(f'{current_path}/workHistorical/agent1_downloadANDinsertDATA_DB')
sys.path.append(f'{current_path}/workHistorical/agent2')
sys.path.append(f'{current_path}/workHistorical/agent3')
sys.path.append(f'{current_path}/workHistorical/agent4')
sys.path.append(f'{current_path}/workHistorical/agent5_variationNumberTitle')
sys.path.append(f'{current_path}/workHistorical/agent6_selectionSector')
sys.path.append(f'{current_path}/workHistorical/agent7_larger_time_window')


import agent2.agent2_fast
import agent3.agent3_fast
import agent4.agent4_fast

import agent2 as agent2
import agent3 as agent3
#import agent4 as agent4
#import agent5_variationNumberTitle as agent5
#from agent5_variationNumberTitle import main_agent5 as agent5
#from agent6_selectionSector import main_agent6 as agent6
#from agent4.agent4_fast import main as main4
#from agent5_variationNumberTitle.agent5_fast import main as main5
#from agent6_selectionSector.agent6_fast import main as main6
#from agent7_larger_time_window.agent7_fast import main as main7
#from agent8_variations_initial_budget.agent8_fast import main as main8

import agent3.agent3_markCapDayInitial
import agent3.agent3_markCapDayPurchase
import agent3.agent3_selectRandom

import agent4.agent4_markCapDayInitial
import agent4.agent4_markCapDayPurchase
import agent4.agent4_selectRandom

import agent5_variationNumberTitle.agent5_markCapDayInitial
import agent5_variationNumberTitle.agent5_markCapDayPurchase
import agent5_variationNumberTitle.agent5_selectRandom

import agent7_larger_time_window.agent7_markCapDayInitial
import agent7_larger_time_window.agent7_markCapDayPurchase
import agent7_larger_time_window.agent7_selectRandom

from config import get_path_specify, market_data_path, project_root
import traceback
from utils import generateiRandomDates2



def main():
    cur, conn = connectDB.connect_nasdaq()
    #datesToTrade1 = generateiRandomDates2(cur, 80)
    
    
    """cur.execute("select initial_date, end_date from testing where id=1 order by initial_date;")
    datesToTrade1 = {(d[0].strftime('%Y-%m-%d %H:%M:%S'), d[0], d[1].strftime('%Y-%m-%d %H:%M:%S')) for d in cur.fetchall()} 
    datesToTrade1 = list(datesToTrade1)
    datesToTrade1.append(('2008-11-17 00:00:00', datetime.strptime('2008-11-17 00:00:00', '%Y-%m-%d %H:%M:%S'), '2009-11-17 00:00:00'))
    datesToTrade1.append(('2023-05-19 00:00:00', datetime.strptime('2023-05-19 00:00:00', '%Y-%m-%d %H:%M:%S'), '2023-05-19 00:00:00'))
    print(datesToTrade1)
    """
    #datesToTrade1 = [('1992-08-12 00:00:00', datetime(1992, 8, 12, 0, 0), '1993-08-12 00:00:00'), ('1999-10-05 00:00:00', datetime(1999, 10, 5, 0, 0), '2000-10-05 00:00:00'), ('2000-06-13 00:00:00', datetime(2000, 6, 13, 0, 0), '2001-06-13 00:00:00'), ('2001-01-08 00:00:00', datetime(2001, 1, 8, 0, 0), '2002-01-08 00:00:00'), ('2001-04-11 00:00:00', datetime(2001, 4, 11, 0, 0), '2002-04-11 00:00:00'), ('2001-08-22 00:00:00', datetime(2001, 8, 22, 0, 0), '2002-08-22 00:00:00'), ('2002-02-19 00:00:00', datetime(2002, 2, 19, 0, 0), '2003-02-19 00:00:00'), ('2002-08-13 00:00:00', datetime(2002, 8, 13, 0, 0), '2003-08-13 00:00:00'), ('2004-11-26 00:00:00', datetime(2004, 11, 26, 0, 0), '2005-11-26 00:00:00'), ('2004-12-17 00:00:00', datetime(2004, 12, 17, 0, 0), '2005-12-17 00:00:00'), ('2005-07-27 00:00:00', datetime(2005, 7, 27, 0, 0), '2006-07-27 00:00:00'), ('2006-07-18 00:00:00', datetime(2006, 7, 18, 0, 0), '2007-07-18 00:00:00'), ('2007-08-27 00:00:00', datetime(2007, 8, 27, 0, 0), '2008-08-27 00:00:00'), ('2008-10-08 00:00:00', datetime(2008, 10, 8, 0, 0), '2009-10-08 00:00:00'), ('2008-10-30 00:00:00', datetime(2008, 10, 30, 0, 0), '2009-10-30 00:00:00'), ('2009-09-10 00:00:00', datetime(2009, 9, 10, 0, 0), '2010-09-10 00:00:00'), ('2009-12-11 00:00:00', datetime(2009, 12, 11, 0, 0), '2010-12-11 00:00:00'), ('2010-02-18 00:00:00', datetime(2010, 2, 18, 0, 0), '2011-02-18 00:00:00'), ('2010-04-12 00:00:00', datetime(2010, 4, 12, 0, 0), '2011-04-12 00:00:00'), ('2010-05-17 00:00:00', datetime(2010, 5, 17, 0, 0), '2011-05-17 00:00:00'), ('2010-05-28 00:00:00', datetime(2010, 5, 28, 0, 0), '2011-05-28 00:00:00'), ('2010-06-25 00:00:00', datetime(2010, 6, 25, 0, 0), '2011-06-25 00:00:00'), ('2010-11-16 00:00:00', datetime(2010, 11, 16, 0, 0), '2011-11-16 00:00:00'), ('2011-02-11 00:00:00', datetime(2011, 2, 11, 0, 0), '2012-02-11 00:00:00'), ('2011-03-15 00:00:00', datetime(2011, 3, 15, 0, 0), '2012-03-15 00:00:00'), ('2011-03-23 00:00:00', datetime(2011, 3, 23, 0, 0), '2012-03-23 00:00:00'), ('2011-08-22 00:00:00', datetime(2011, 8, 22, 0, 0), '2012-08-22 00:00:00'), ('2012-09-25 00:00:00', datetime(2012, 9, 25, 0, 0), '2013-09-25 00:00:00'), ('2013-04-22 00:00:00', datetime(2013, 4, 22, 0, 0), '2014-04-22 00:00:00'), ('2013-09-09 00:00:00', datetime(2013, 9, 9, 0, 0), '2014-09-09 00:00:00'), ('2013-12-11 00:00:00', datetime(2013, 12, 11, 0, 0), '2014-12-11 00:00:00'), ('2013-12-12 00:00:00', datetime(2013, 12, 12, 0, 0), '2014-12-12 00:00:00'), ('2014-04-21 00:00:00', datetime(2014, 4, 21, 0, 0), '2015-04-21 00:00:00'), ('2014-12-08 00:00:00', datetime(2014, 12, 8, 0, 0), '2015-12-08 00:00:00'), ('2014-12-26 00:00:00', datetime(2014, 12, 26, 0, 0), '2015-12-26 00:00:00'), ('2015-02-24 00:00:00', datetime(2015, 2, 24, 0, 0), '2016-02-24 00:00:00'), ('2015-02-26 00:00:00', datetime(2015, 2, 26, 0, 0), '2016-02-26 00:00:00'), ('2015-05-07 00:00:00', datetime(2015, 5, 7, 0, 0), '2016-05-07 00:00:00'), ('2015-08-21 00:00:00', datetime(2015, 8, 21, 0, 0), '2016-08-21 00:00:00'), ('2015-11-11 00:00:00', datetime(2015, 11, 11, 0, 0), '2016-11-11 00:00:00'), ('2016-04-18 00:00:00', datetime(2016, 4, 18, 0, 0), '2017-04-18 00:00:00'), ('2016-06-21 00:00:00', datetime(2016, 6, 21, 0, 0), '2017-06-21 00:00:00'), ('2017-07-06 00:00:00', datetime(2017, 7, 6, 0, 0), '2018-07-06 00:00:00'), ('2017-08-31 00:00:00', datetime(2017, 8, 31, 0, 0), '2018-08-31 00:00:00'), ('2017-09-20 00:00:00', datetime(2017, 9, 20, 0, 0), '2018-09-20 00:00:00'), ('2017-10-10 00:00:00', datetime(2017, 10, 10, 0, 0), '2018-10-10 00:00:00'), ('2018-03-08 00:00:00', datetime(2018, 3, 8, 0, 0), '2019-03-08 00:00:00'), ('2018-06-19 00:00:00', datetime(2018, 6, 19, 0, 0), '2019-06-19 00:00:00'), ('2018-08-31 00:00:00', datetime(2018, 8, 31, 0, 0), '2019-08-31 00:00:00'), ('2018-10-10 00:00:00', datetime(2018, 10, 10, 0, 0), '2019-10-10 00:00:00'), ('2018-11-23 00:00:00', datetime(2018, 11, 23, 0, 0), '2019-11-23 00:00:00'), ('2018-12-24 00:00:00', datetime(2018, 12, 24, 0, 0), '2019-12-24 00:00:00'), ('2019-02-12 00:00:00', datetime(2019, 2, 12, 0, 0), '2020-02-12 00:00:00'), ('2019-03-18 00:00:00', datetime(2019, 3, 18, 0, 0), '2020-03-18 00:00:00'), ('2019-04-03 00:00:00', datetime(2019, 4, 3, 0, 0), '2020-04-03 00:00:00'), ('2019-07-19 00:00:00', datetime(2019, 7, 19, 0, 0), '2020-07-19 00:00:00'), ('2019-08-23 00:00:00', datetime(2019, 8, 23, 0, 0), '2020-08-23 00:00:00'), ('2019-09-27 00:00:00', datetime(2019, 9, 27, 0, 0), '2020-09-27 00:00:00'), ('2019-10-04 00:00:00', datetime(2019, 10, 4, 0, 0), '2020-10-04 00:00:00'), ('2019-10-22 00:00:00', datetime(2019, 10, 22, 0, 0), '2020-10-22 00:00:00'), ('2019-12-09 00:00:00', datetime(2019, 12, 9, 0, 0), '2020-12-09 00:00:00'), ('2020-05-12 00:00:00', datetime(2020, 5, 12, 0, 0), '2021-05-12 00:00:00'), ('2020-06-29 00:00:00', datetime(2020, 6, 29, 0, 0), '2021-06-29 00:00:00'), ('2020-07-01 00:00:00', datetime(2020, 7, 1, 0, 0), '2021-07-01 00:00:00'), ('2020-07-22 00:00:00', datetime(2020, 7, 22, 0, 0), '2021-07-22 00:00:00'), ('2020-10-12 00:00:00', datetime(2020, 10, 12, 0, 0), '2021-10-12 00:00:00'), ('2020-10-29 00:00:00', datetime(2020, 10, 29, 0, 0), '2021-10-29 00:00:00'), ('2020-12-11 00:00:00', datetime(2020, 12, 11, 0, 0), '2021-12-11 00:00:00'), ('2021-06-25 00:00:00', datetime(2021, 6, 25, 0, 0), '2022-06-25 00:00:00'), ('2021-08-04 00:00:00', datetime(2021, 8, 4, 0, 0), '2022-08-04 00:00:00'), ('2021-09-29 00:00:00', datetime(2021, 9, 29, 0, 0), '2022-09-29 00:00:00'), ('2021-10-05 00:00:00', datetime(2021, 10, 5, 0, 0), '2022-10-05 00:00:00'), ('2021-10-11 00:00:00', datetime(2021, 10, 11, 0, 0), '2022-10-11 00:00:00'), ('2021-11-10 00:00:00', datetime(2021, 11, 10, 0, 0), '2022-11-10 00:00:00'), ('2022-01-11 00:00:00', datetime(2022, 1, 11, 0, 0), '2023-01-11 00:00:00'), ('2022-01-26 00:00:00', datetime(2022, 1, 26, 0, 0), '2023-01-26 00:00:00'), ('2022-02-03 00:00:00', datetime(2022, 2, 3, 0, 0), '2023-02-03 00:00:00'), ('2022-04-06 00:00:00', datetime(2022, 4, 6, 0, 0), '2023-04-06 00:00:00'), ('2022-04-18 00:00:00', datetime(2022, 4, 18, 0, 0), '2023-04-18 00:00:00'), ('2022-06-02 00:00:00', datetime(2022, 6, 2, 0, 0), '2023-06-02 00:00:00'), ('2022-06-08 00:00:00', datetime(2022, 6, 8, 0, 0), '2023-06-08 00:00:00'), ('2022-06-08 00:00:00', datetime(2022, 6, 8, 0, 0), '2023-06-08 00:00:00'), ('2022-06-17 00:00:00', datetime(2022, 6, 17, 0, 0), '2023-06-17 00:00:00'), ('2022-06-23 00:00:00', datetime(2022, 6, 23, 0, 0), '2023-06-23 00:00:00'), ('2022-07-19 00:00:00', datetime(2022, 7, 19, 0, 0), '2023-07-19 00:00:00'), ('2022-08-17 00:00:00', datetime(2022, 8, 17, 0, 0), '2023-08-17 00:00:00'), ('2022-09-09 00:00:00', datetime(2022, 9, 9, 0, 0), '2023-09-09 00:00:00'), ('2022-09-19 00:00:00', datetime(2022, 9, 19, 0, 0), '2023-09-19 00:00:00'), ('2023-01-19 00:00:00', datetime(2023, 1, 19, 0, 0), '2024-01-19 00:00:00'), ('2023-01-23 00:00:00', datetime(2023, 1, 23, 0, 0), '2024-01-23 00:00:00'), ('2023-02-02 00:00:00', datetime(2023, 2, 2, 0, 0), '2024-02-02 00:00:00'), ('2023-03-20 00:00:00', datetime(2023, 3, 20, 0, 0), '2024-03-20 00:00:00'), ('2023-03-30 00:00:00', datetime(2023, 3, 30, 0, 0), '2024-03-30 00:00:00'), ('2023-05-04 00:00:00', datetime(2023, 5, 4, 0, 0), '2024-05-04 00:00:00'), ('2023-05-04 00:00:00', datetime(2023, 5, 4, 0, 0), '2024-05-04 00:00:00'), ('2023-06-30 00:00:00', datetime(2023, 6, 30, 0, 0), '2024-06-30 00:00:00'), ('2023-08-28 00:00:00', datetime(2023, 8, 28, 0, 0), '2024-08-28 00:00:00'), ('2023-08-30 00:00:00', datetime(2023, 8, 30, 0, 0), '2024-08-30 00:00:00'), ('2023-10-10 00:00:00', datetime(2023, 10, 10, 0, 0), '2024-10-10 00:00:00'), ('2023-11-17 00:00:00', datetime(2023, 11, 17, 0, 0), '2024-11-17 00:00:00')]
    #datesToTrade1 = [('1999-06-24 00:00:00', datetime(1999, 6, 24, 0, 0), '2000-06-24 00:00:00'), ('1999-07-16 00:00:00', datetime(1999, 7, 16, 0, 0), '2000-07-16 00:00:00'), ('1999-09-08 00:00:00', datetime(1999, 9, 8, 0, 0), '2000-09-08 00:00:00'), ('2001-08-08 00:00:00', datetime(2001, 8, 8, 0, 0), '2002-08-08 00:00:00'), ('2001-09-24 00:00:00', datetime(2001, 9, 24, 0, 0), '2002-09-24 00:00:00'), ('2002-11-01 00:00:00', datetime(2002, 11, 1, 0, 0), '2003-11-01 00:00:00'), ('2002-11-18 00:00:00', datetime(2002, 11, 18, 0, 0), '2003-11-18 00:00:00'), ('2004-01-09 00:00:00', datetime(2004, 1, 9, 0, 0), '2005-01-09 00:00:00'), ('2004-08-18 00:00:00', datetime(2004, 8, 18, 0, 0), '2005-08-18 00:00:00'), ('2006-11-02 00:00:00', datetime(2006, 11, 2, 0, 0), '2007-11-02 00:00:00'), ('2006-11-15 00:00:00', datetime(2006, 11, 15, 0, 0), '2007-11-15 00:00:00'), ('2009-04-16 00:00:00', datetime(2009, 4, 16, 0, 0), '2010-04-16 00:00:00'), ('2009-10-20 00:00:00', datetime(2009, 10, 20, 0, 0), '2010-10-20 00:00:00'), ('2009-11-23 00:00:00', datetime(2009, 11, 23, 0, 0), '2010-11-23 00:00:00'), ('2010-07-16 00:00:00', datetime(2010, 7, 16, 0, 0), '2011-07-16 00:00:00'), ('2011-06-09 00:00:00', datetime(2011, 6, 9, 0, 0), '2012-06-09 00:00:00'), ('2011-07-28 00:00:00', datetime(2011, 7, 28, 0, 0), '2012-07-28 00:00:00'), ('2011-09-20 00:00:00', datetime(2011, 9, 20, 0, 0), '2012-09-20 00:00:00'), ('2012-11-19 00:00:00', datetime(2012, 11, 19, 0, 0), '2013-11-19 00:00:00'), ('2012-12-20 00:00:00', datetime(2012, 12, 20, 0, 0), '2013-12-20 00:00:00'), ('2013-03-01 00:00:00', datetime(2013, 3, 1, 0, 0), '2014-03-01 00:00:00'), ('2013-06-28 00:00:00', datetime(2013, 6, 28, 0, 0), '2014-06-28 00:00:00'), ('2013-08-12 00:00:00', datetime(2013, 8, 12, 0, 0), '2014-08-12 00:00:00'), ('2014-01-13 00:00:00', datetime(2014, 1, 13, 0, 0), '2015-01-13 00:00:00'), ('2014-01-21 00:00:00', datetime(2014, 1, 21, 0, 0), '2015-01-21 00:00:00'), ('2014-01-30 00:00:00', datetime(2014, 1, 30, 0, 0), '2015-01-30 00:00:00'), ('2015-03-04 00:00:00', datetime(2015, 3, 4, 0, 0), '2016-03-04 00:00:00'), ('2015-03-13 00:00:00', datetime(2015, 3, 13, 0, 0), '2016-03-13 00:00:00'), ('2015-03-16 00:00:00', datetime(2015, 3, 16, 0, 0), '2016-03-16 00:00:00'), ('2015-03-26 00:00:00', datetime(2015, 3, 26, 0, 0), '2016-03-26 00:00:00'), ('2015-04-28 00:00:00', datetime(2015, 4, 28, 0, 0), '2016-04-28 00:00:00'), ('2015-05-14 00:00:00', datetime(2015, 5, 14, 0, 0), '2016-05-14 00:00:00'), ('2015-09-15 00:00:00', datetime(2015, 9, 15, 0, 0), '2016-09-15 00:00:00'), ('2016-02-23 00:00:00', datetime(2016, 2, 23, 0, 0), '2017-02-23 00:00:00'), ('2016-03-18 00:00:00', datetime(2016, 3, 18, 0, 0), '2017-03-18 00:00:00'), ('2016-04-06 00:00:00', datetime(2016, 4, 6, 0, 0), '2017-04-06 00:00:00'), ('2016-10-06 00:00:00', datetime(2016, 10, 6, 0, 0), '2017-10-06 00:00:00'), ('2017-02-15 00:00:00', datetime(2017, 2, 15, 0, 0), '2018-02-15 00:00:00'), ('2017-03-15 00:00:00', datetime(2017, 3, 15, 0, 0), '2018-03-15 00:00:00'), ('2017-05-01 00:00:00', datetime(2017, 5, 1, 0, 0), '2018-05-01 00:00:00'), ('2017-08-14 00:00:00', datetime(2017, 8, 14, 0, 0), '2018-08-14 00:00:00'), ('2017-08-15 00:00:00', datetime(2017, 8, 15, 0, 0), '2018-08-15 00:00:00'), ('2017-08-16 00:00:00', datetime(2017, 8, 16, 0, 0), '2018-08-16 00:00:00'), ('2017-10-30 00:00:00', datetime(2017, 10, 30, 0, 0), '2018-10-30 00:00:00'), ('2018-02-14 00:00:00', datetime(2018, 2, 14, 0, 0), '2019-02-14 00:00:00'), ('2018-03-29 00:00:00', datetime(2018, 3, 29, 0, 0), '2019-03-29 00:00:00'), ('2018-05-14 00:00:00', datetime(2018, 5, 14, 0, 0), '2019-05-14 00:00:00'), ('2018-06-04 00:00:00', datetime(2018, 6, 4, 0, 0), '2019-06-04 00:00:00'), ('2018-08-09 00:00:00', datetime(2018, 8, 9, 0, 0), '2019-08-09 00:00:00'), ('2019-03-14 00:00:00', datetime(2019, 3, 14, 0, 0), '2020-03-14 00:00:00'), ('2019-05-03 00:00:00', datetime(2019, 5, 3, 0, 0), '2020-05-03 00:00:00'), ('2019-05-17 00:00:00', datetime(2019, 5, 17, 0, 0), '2020-05-17 00:00:00'), ('2019-06-17 00:00:00', datetime(2019, 6, 17, 0, 0), '2020-06-17 00:00:00'), ('2019-06-27 00:00:00', datetime(2019, 6, 27, 0, 0), '2020-06-27 00:00:00'), ('2020-01-10 00:00:00', datetime(2020, 1, 10, 0, 0), '2021-01-10 00:00:00'), ('2020-01-31 00:00:00', datetime(2020, 1, 31, 0, 0), '2021-01-31 00:00:00'), ('2020-03-27 00:00:00', datetime(2020, 3, 27, 0, 0), '2021-03-27 00:00:00'), ('2020-05-26 00:00:00', datetime(2020, 5, 26, 0, 0), '2021-05-26 00:00:00'), ('2020-05-27 00:00:00', datetime(2020, 5, 27, 0, 0), '2021-05-27 00:00:00'), ('2020-08-05 00:00:00', datetime(2020, 8, 5, 0, 0), '2021-08-05 00:00:00'), ('2020-08-17 00:00:00', datetime(2020, 8, 17, 0, 0), '2021-08-17 00:00:00'), ('2020-09-11 00:00:00', datetime(2020, 9, 11, 0, 0), '2021-09-11 00:00:00'), ('2020-10-21 00:00:00', datetime(2020, 10, 21, 0, 0), '2021-10-21 00:00:00'), ('2021-02-10 00:00:00', datetime(2021, 2, 10, 0, 0), '2022-02-10 00:00:00'), ('2021-03-30 00:00:00', datetime(2021, 3, 30, 0, 0), '2022-03-30 00:00:00'), ('2021-04-14 00:00:00', datetime(2021, 4, 14, 0, 0), '2022-04-14 00:00:00'), ('2021-07-08 00:00:00', datetime(2021, 7, 8, 0, 0), '2022-07-08 00:00:00'), ('2021-08-11 00:00:00', datetime(2021, 8, 11, 0, 0), '2022-08-11 00:00:00'), ('2021-08-18 00:00:00', datetime(2021, 8, 18, 0, 0), '2022-08-18 00:00:00'), ('2021-10-28 00:00:00', datetime(2021, 10, 28, 0, 0), '2022-10-28 00:00:00'), ('2021-11-11 00:00:00', datetime(2021, 11, 11, 0, 0), '2022-11-11 00:00:00'), ('2021-12-28 00:00:00', datetime(2021, 12, 28, 0, 0), '2022-12-28 00:00:00'), ('2022-01-07 00:00:00', datetime(2022, 1, 7, 0, 0), '2023-01-07 00:00:00'), ('2022-02-08 00:00:00', datetime(2022, 2, 8, 0, 0), '2023-02-08 00:00:00'), ('2022-04-04 00:00:00', datetime(2022, 4, 4, 0, 0), '2023-04-04 00:00:00'), ('2022-05-10 00:00:00', datetime(2022, 5, 10, 0, 0), '2023-05-10 00:00:00'), ('2022-05-26 00:00:00', datetime(2022, 5, 26, 0, 0), '2023-05-26 00:00:00'), ('2022-06-15 00:00:00', datetime(2022, 6, 15, 0, 0), '2023-06-15 00:00:00'), ('2022-10-17 00:00:00', datetime(2022, 10, 17, 0, 0), '2023-10-17 00:00:00'), ('2022-12-29 00:00:00', datetime(2022, 12, 29, 0, 0), '2023-12-29 00:00:00'), ('2023-01-09 00:00:00', datetime(2023, 1, 9, 0, 0), '2024-01-09 00:00:00'), ('2023-01-20 00:00:00', datetime(2023, 1, 20, 0, 0), '2024-01-20 00:00:00'), ('2023-03-03 00:00:00', datetime(2023, 3, 3, 0, 0), '2024-03-03 00:00:00'), ('2023-03-22 00:00:00', datetime(2023, 3, 22, 0, 0), '2024-03-22 00:00:00'), ('2023-04-13 00:00:00', datetime(2023, 4, 13, 0, 0), '2024-04-13 00:00:00'), ('2023-04-28 00:00:00', datetime(2023, 4, 28, 0, 0), '2024-04-28 00:00:00'), ('2023-05-24 00:00:00', datetime(2023, 5, 24, 0, 0), '2024-05-24 00:00:00'), ('2023-08-15 00:00:00', datetime(2023, 8, 15, 0, 0), '2024-08-15 00:00:00'), ('2023-08-24 00:00:00', datetime(2023, 8, 24, 0, 0), '2024-08-24 00:00:00'), ('2023-09-08 00:00:00', datetime(2023, 9, 8, 0, 0), '2024-09-08 00:00:00'), ('2023-10-25 00:00:00', datetime(2023, 10, 25, 0, 0), '2024-10-25 00:00:00')]
    #datesToTrade1 = [('2020-08-05 00:00:00', datetime(2020, 8, 5, 0, 0), '2021-08-05 00:00:00')]
    datesToTrade1 = [('1999-12-17 00:00:00', datetime(1999, 12, 17, 0, 0), '2000-12-17 00:00:00'), ('2000-05-19 00:00:00', datetime(2000, 5, 19, 0, 0), '2001-05-19 00:00:00'), ('2000-06-07 00:00:00', datetime(2000, 6, 7, 0, 0), '2001-06-07 00:00:00'), ('2000-10-24 00:00:00', datetime(2000, 10, 24, 0, 0), '2001-10-24 00:00:00'), ('2002-04-29 00:00:00', datetime(2002, 4, 29, 0, 0), '2003-04-29 00:00:00'), ('2002-09-30 00:00:00', datetime(2002, 9, 30, 0, 0), '2003-09-30 00:00:00'), ('2002-11-25 00:00:00', datetime(2002, 11, 25, 0, 0), '2003-11-25 00:00:00'), ('2003-07-10 00:00:00', datetime(2003, 7, 10, 0, 0), '2004-07-10 00:00:00'), ('2004-06-02 00:00:00', datetime(2004, 6, 2, 0, 0), '2005-06-02 00:00:00'), ('2004-08-30 00:00:00', datetime(2004, 8, 30, 0, 0), '2005-08-30 00:00:00'), ('2005-11-23 00:00:00', datetime(2005, 11, 23, 0, 0), '2006-11-23 00:00:00'), ('2006-03-03 00:00:00', datetime(2006, 3, 3, 0, 0), '2007-03-03 00:00:00'), ('2006-12-29 00:00:00', datetime(2006, 12, 29, 0, 0), '2007-12-29 00:00:00'),  ('2009-05-18 00:00:00', datetime(2009, 5, 18, 0, 0), '2010-05-18 00:00:00'), ('2009-06-29 00:00:00', datetime(2009, 6, 29, 0, 0), '2010-06-29 00:00:00'), ('2011-03-24 00:00:00', datetime(2011, 3, 24, 0, 0), '2012-03-24 00:00:00'), ('2011-06-03 00:00:00', datetime(2011, 6, 3, 0, 0), '2012-06-03 00:00:00'), ('2011-09-29 00:00:00', datetime(2011, 9, 29, 0, 0), '2012-09-29 00:00:00'), ('2012-08-24 00:00:00', datetime(2012, 8, 24, 0, 0), '2013-08-24 00:00:00'), ('2013-03-19 00:00:00', datetime(2013, 3, 19, 0, 0), '2014-03-19 00:00:00'), ('2014-05-14 00:00:00', datetime(2014, 5, 14, 0, 0), '2015-05-14 00:00:00'), ('2014-08-26 00:00:00', datetime(2014, 8, 26, 0, 0), '2015-08-26 00:00:00'), ('2014-10-14 00:00:00', datetime(2014, 10, 14, 0, 0), '2015-10-14 00:00:00'), ('2015-12-09 00:00:00', datetime(2015, 12, 9, 0, 0), '2016-12-09 00:00:00'), ('2016-02-09 00:00:00', datetime(2016, 2, 9, 0, 0), '2017-02-09 00:00:00'), ('2016-04-07 00:00:00', datetime(2016, 4, 7, 0, 0), '2017-04-07 00:00:00'), ('2016-05-04 00:00:00', datetime(2016, 5, 4, 0, 0), '2017-05-04 00:00:00'), ('2016-06-03 00:00:00', datetime(2016, 6, 3, 0, 0), '2017-06-03 00:00:00'), ('2016-08-11 00:00:00', datetime(2016, 8, 11, 0, 0), '2017-08-11 00:00:00'), ('2017-03-07 00:00:00', datetime(2017, 3, 7, 0, 0), '2018-03-07 00:00:00'), ('2017-12-06 00:00:00', datetime(2017, 12, 6, 0, 0), '2018-12-06 00:00:00'), ('2018-02-02 00:00:00', datetime(2018, 2, 2, 0, 0), '2019-02-02 00:00:00'), ('2018-03-21 00:00:00', datetime(2018, 3, 21, 0, 0), '2019-03-21 00:00:00'), ('2018-04-16 00:00:00', datetime(2018, 4, 16, 0, 0), '2019-04-16 00:00:00'), ('2018-07-06 00:00:00', datetime(2018, 7, 6, 0, 0), '2019-07-06 00:00:00'), ('2018-07-06 00:00:00', datetime(2018, 7, 6, 0, 0), '2019-07-06 00:00:00'), ('2018-11-16 00:00:00', datetime(2018, 11, 16, 0, 0), '2019-11-16 00:00:00'), ('2019-02-22 00:00:00', datetime(2019, 2, 22, 0, 0), '2020-02-22 00:00:00'), ('2019-04-05 00:00:00', datetime(2019, 4, 5, 0, 0), '2020-04-05 00:00:00'), ('2019-04-11 00:00:00', datetime(2019, 4, 11, 0, 0), '2020-04-11 00:00:00'), ('2019-04-22 00:00:00', datetime(2019, 4, 22, 0, 0), '2020-04-22 00:00:00'), ('2019-05-09 00:00:00', datetime(2019, 5, 9, 0, 0), '2020-05-09 00:00:00'), ('2019-07-11 00:00:00', datetime(2019, 7, 11, 0, 0), '2020-07-11 00:00:00'), ('2019-08-06 00:00:00', datetime(2019, 8, 6, 0, 0), '2020-08-06 00:00:00'), ('2019-09-20 00:00:00', datetime(2019, 9, 20, 0, 0), '2020-09-20 00:00:00'), ('2019-11-14 00:00:00', datetime(2019, 11, 14, 0, 0), '2020-11-14 00:00:00'), ('2020-03-31 00:00:00', datetime(2020, 3, 31, 0, 0), '2021-03-31 00:00:00'), ('2020-05-20 00:00:00', datetime(2020, 5, 20, 0, 0), '2021-05-20 00:00:00'), ('2020-06-10 00:00:00', datetime(2020, 6, 10, 0, 0), '2021-06-10 00:00:00'), ('2020-07-21 00:00:00', datetime(2020, 7, 21, 0, 0), '2021-07-21 00:00:00'), ('2020-08-26 00:00:00', datetime(2020, 8, 26, 0, 0), '2021-08-26 00:00:00'), ('2020-12-01 00:00:00', datetime(2020, 12, 1, 0, 0), '2021-12-01 00:00:00'), ('2020-12-11 00:00:00', datetime(2020, 12, 11, 0, 0), '2021-12-11 00:00:00'), ('2021-02-12 00:00:00', datetime(2021, 2, 12, 0, 0), '2022-02-12 00:00:00'), ('2021-02-26 00:00:00', datetime(2021, 2, 26, 0, 0), '2022-02-26 00:00:00'), ('2021-03-18 00:00:00', datetime(2021, 3, 18, 0, 0), '2022-03-18 00:00:00'), ('2021-06-02 00:00:00', datetime(2021, 6, 2, 0, 0), '2022-06-02 00:00:00'), ('2021-08-06 00:00:00', datetime(2021, 8, 6, 0, 0), '2022-08-06 00:00:00'), ('2021-09-14 00:00:00', datetime(2021, 9, 14, 0, 0), '2022-09-14 00:00:00'), ('2021-11-10 00:00:00', datetime(2021, 11, 10, 0, 0), '2022-11-10 00:00:00'), ('2022-01-11 00:00:00', datetime(2022, 1, 11, 0, 0), '2023-01-11 00:00:00'), ('2022-04-14 00:00:00', datetime(2022, 4, 14, 0, 0), '2023-04-14 00:00:00'), ('2022-07-13 00:00:00', datetime(2022, 7, 13, 0, 0), '2023-07-13 00:00:00'), ('2022-08-10 00:00:00', datetime(2022, 8, 10, 0, 0), '2023-08-10 00:00:00'), ('2022-09-02 00:00:00', datetime(2022, 9, 2, 0, 0), '2023-09-02 00:00:00'), ('2022-09-14 00:00:00', datetime(2022, 9, 14, 0, 0), '2023-09-14 00:00:00'), ('2022-11-09 00:00:00', datetime(2022, 11, 9, 0, 0), '2023-11-09 00:00:00'), ('2022-12-02 00:00:00', datetime(2022, 12, 2, 0, 0), '2023-12-02 00:00:00'), ('2023-01-04 00:00:00', datetime(2023, 1, 4, 0, 0), '2024-01-04 00:00:00'), ('2023-01-09 00:00:00', datetime(2023, 1, 9, 0, 0), '2024-01-09 00:00:00'), ('2023-03-06 00:00:00', datetime(2023, 3, 6, 0, 0), '2024-03-06 00:00:00'), ('2023-03-10 00:00:00', datetime(2023, 3, 10, 0, 0), '2024-03-10 00:00:00'), ('2023-03-13 00:00:00', datetime(2023, 3, 13, 0, 0), '2024-03-13 00:00:00'), ('2023-09-20 00:00:00', datetime(2023, 9, 20, 0, 0), '2024-09-20 00:00:00'), ('2023-10-11 00:00:00', datetime(2023, 10, 11, 0, 0), '2024-10-11 00:00:00')]

    #print(datesToTrade1)
    
    Path = f'{project_root}/logs'
    if not os.path.exists(Path):
        os.mkdir(f'{project_root}/logs')
    
    logging.basicConfig(filename=f'{project_root}/logs/test.log', level=logging.INFO,  format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info(f"Start program: {datetime.now()}")
    
    marksCap = ['topVal1999', 'topVal2000', 'topVal2001', 'topVal2002', 'topVal2003', 'topVal2004', 'topVal2005', 
                'topVal2006', 'topVal2007', 'topVal2009', 'topVal2010', 'topVal2011', 'topVal2012', 
                'topVal2013', 'topVal2014', 'topVal2015', 'topVal2016', 'topVal2017', 'topVal2018', 'topVal2019', 
                'topVal2020', 'topVal2021', 'topVal2022', 'topVal2023', 'topVal2024']
    # da inserire 'topVal2008'
    
    markets = ['NASDAQ', 'NYSE', 'LARG_COMP_EU']
    
    dizMarkCap = {}
    for mark in markets:
        dizMarkCap[mark] = {}
        for top in marksCap:
            with open(f'{market_data_path}/csv_files/marketCap/{mark}/{top}.csv', mode='r') as file:
                year = top[-4:]
                if mark not in dizMarkCap[mark]:
                    dizMarkCap[mark][year] = {}
                for row in csv.DictReader(file):
                    if row['date'] not in dizMarkCap[mark][year]:
                        dizMarkCap[mark][year][row['date'][0:-6]] = []
                    dizMarkCap[mark][year][row['date'][0:-6]].append(row['symb'])
    
    
    # Recupero dei simboli azionari disponibili per le date di trading scelte in "symbolDisp"
    symbolsDispoInDatesNasd = {}
    symbolsDispoInDatesNyse = {}
    symbolsDispoInDatesLarge = {} 
    #markets = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']  #
    markets = ['larg_comp_eu_actions']
    for mark in markets:
        for date in datesToTrade1:
            # Recupero dei simboli azionari disponibili per le date di trading scelte in "symbolDisp"
            cur.execute(f"SELECT distinct(symbol) FROM {mark} WHERE time_value_it BETWEEN '{date[0]}' AND '{date[2]}';")
            if mark == 'nasdaq_actions':
                symbolsDispoInDatesNasd[date[1]] = [sy[0] for sy in cur.fetchall()]
            elif mark == 'nyse_actions':
                symbolsDispoInDatesNyse[date[1]] = [sy[0] for sy in cur.fetchall()]
            else:
                symbolsDispoInDatesLarge[date[1]] = [sy[0] for sy in cur.fetchall()]
                
                
    # Recupero dei prezzi di apertura e chiusura per i simboli azionari disponibili nelle date di trading scelte in "priceDisp"
    pricesDispoInDatesNasd = {}
    pricesDispoInDatesNyse = {}
    pricesDispoInDatesLarge = {}
    #markets = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']
    markets = ['larg_comp_eu_actions']
    for mark in markets:
        for date in datesToTrade1:
                
                """if mark == 'nasdaq_actions':
                    last_date_year = (list(dizMarkCap['NASDAQ'][date[2][0:4]])[-1])
                    symbolsF = (dizMarkCap['NASDAQ'][date[2][0:4]][last_date_year])[0].split(';') 
                    symbolsF = symbolsF[0:500]
                    
                if mark == 'nyse_actions':
                    last_date_year = (list(dizMarkCap['NYSE'][date[2][0:4]])[-1])
                    symbolsF = (dizMarkCap['NYSE'][date[2][0:4]][last_date_year])[0].split(';')
                    symbolsF = symbolsF[0:500]
                
                if mark == 'larg_comp_eu_actions':
                    last_date_year = (list(dizMarkCap['LARG_COMP_EU'][date[2][0:4]])[-1])
                    symbolsF = (dizMarkCap['LARG_COMP_EU'][date[2][0:4]][last_date_year])[0].split(';')
                    symbolsF = symbolsF[0:500]
                """    
            
                # Recupero dei prezzi di apertura e chiusura per i simboli azionari disponibili nelle date di trading scelte in "priceDisp"
                cur.execute(f"SELECT symbol, time_value_it, open_price, high_price FROM {mark} WHERE time_value_it BETWEEN '{date[0]}' AND '{date[2]}'")
                #cur.execute( f"SELECT symbol, time_value_it, open_price, high_price FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")

                if mark == 'nasdaq_actions':
                    prices_dict = {}
                    for symbol, time_value_it, open_price, high_price in cur.fetchall():
                        prices_dict[(symbol, time_value_it.strftime('%Y-%m-%d %H:%M:%S'))] = (open_price, high_price)    
                    pricesDispoInDatesNasd[date[1]] = [prices_dict]
                elif mark == 'nyse_actions':
                    prices_dict = {}
                    for symbol, time_value_it, open_price, high_price in cur.fetchall():
                        prices_dict[(symbol, time_value_it.strftime('%Y-%m-%d %H:%M:%S'))] = (open_price, high_price)    
                    pricesDispoInDatesNyse[date[1]] = [prices_dict]
                else:
                    prices_dict = {}
                    for symbol, time_value_it, open_price, high_price in cur.fetchall():
                        prices_dict[(symbol, time_value_it.strftime('%Y-%m-%d %H:%M:%S'))] = (open_price, high_price)    
                    pricesDispoInDatesLarge[date[1]] = [prices_dict]    
    
    cur.close()
    conn.close()
    
    ########
    
    # Esecuzione degli agenti con le varie strategie
    
    agent2.agent2_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent2.agent2_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent2.agent2_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    
    agent3.agent3_markCapDayInitial.main(datesToTrade1,  dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent3.agent3_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent3.agent3_selectRandom.main(datesToTrade1,  dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    
    agent4.agent4_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent4.agent4_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent4.agent4_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    
    agent5_variationNumberTitle.agent5_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent5_variationNumberTitle.agent5_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent5_variationNumberTitle.agent5_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    
    agent7_larger_time_window.agent7_markCapDayInitial.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent7_larger_time_window.agent7_markCapDayPurchase.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    agent7_larger_time_window.agent7_selectRandom.main(datesToTrade1, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge)
    

    #device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    #print(f"Using device: {device}")

    # Esempio: Allocazione di dati su GPU
    #data = torch.tensor([1.0, 2.0, 3.0], device=device)
    #result = data * 2  # Operazione GPU
    
    
    #agent2.main_agent2_purchaseALL.main(datesToTrade1) # 23:23:27,064 6 gennaio
    #agent2.agent2_fast.main(datesToTrade1) # 11:22:45 ---> 11:45:10 (nasdaq) --> 12:10 (nyse) ---> 12:31 (large)  8 gennaio
    ###########################
    #agent3.agent3_SimulationMulMarket.main(datesToTrade1)
    #agent3.agent3_fast.main(datesToTrade1) # 12:31:00 --->  (nasdaq) -->  (nyse) --->  (large)  8 gennaio
    ###########################
    #agent4.agent4_simulation.main(datesToTrade1)
    #main4(datesToTrade1)
    ###########################
    #agent5.main(datesToTrade1)
    #agent5.agent5_fast.main(datesToTrade1)
    #main5(datesToTrade1)
    ###########################
    
    
    cur, conn = connectDB.connect_nasdaq()
    
    dizNasdaq = dict()
    # Apri il file CSV in modalità lettura
    with open(f'{current_path}/marketData/csv_files/nasdaq_symbols_sorted.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
        
        cur.execute(f"SELECT distinct(symbol) FROM nasdaq_actions;")
        sy_nasd = [s[0] for s in cur.fetchall()]

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            if col['Symbol'] in sy_nasd:
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
    with open(f'{current_path}/marketData/csv_files/nyse_symbols_sorted.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)
        
        cur.execute(f"SELECT distinct(symbol) FROM nyse_actions;")
        sy_nys = [s[0] for s in cur.fetchall()]

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            if col['Symbol'] in sy_nys:
                if col['Sector'] not in dizNyse:
                    dizNyse[col['Sector']] = [col['Symbol']]
                else:
                    dizNyse[col['Sector']].append(col['Symbol'])
                
    #print(dizNyse)
    
    for sector in dizNyse:
        print(f"{sector}: {len(dizNyse[sector])}\n")
        
    cur.close()
    conn.close()
    
    #agent6.main(datesToTrade1, dizNasdaq, dizNyse, perc=0.3)
    #agent6.agent6_fast.main(datesToTrade1, dizNasdaq, dizNyse, perc=0.3)
    #main6(datesToTrade1, dizNasdaq, dizNyse, perc=0.5)
    
    #main7(datesToTrade1)
    
    #main8(datesToTrade1)
    
    print("Fine simulazione")
    return

if __name__ == '__main__':
    main()


