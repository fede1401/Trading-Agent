# Ordinamento del 5% delle azioni della borsa Nasdaq per capitalizzazione decrescente (pool)
# Fino ad esaurimento budget si acquistano azioni random dal pool
# Vendesi delle azioni che sono salite del TP% = 1 rispetto al prezzo d'acquisto
# sleep di 15 minuti

# import MetaTrader5 as mt5
#import db.connectDB as connectDB, db.insertDataDB as insertDataDB, agentState
import psycopg2
import time
import random
import logging
import pytz
from datetime import datetime, time, timedelta
import time as time_module
import csv
import math
from dateutil.relativedelta import relativedelta
import pandas as pd
import traceback

import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent1')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent2')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent3')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

from db import insertDataDB, connectDB as connectDB
import agentState


def getRandomDate(cursor):
    # Seleziona un giorno casuale all'interno del range temporale che sia più piccolo di 365 giorni rispetto alla data massima presente nel database
    cursor.execute("SELECT MAX(time_value_it) - INTERVAL '1 year 2 month 1 days' FROM nasdaq_actions;")
    max_date = cursor.fetchone()[0]
                
    cursor.execute("SELECT time_value_it FROM nasdaq_actions WHERE time_value_it < %s ORDER BY RANDOM() LIMIT 1;", (max_date,))
    trade_date = cursor.fetchone()[0]    
    trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')
                
    # Converti la stringa in un oggetto datetime
    initial_date = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

    # Aggiungi 1 anno usando relativedelta
    end_date = initial_date + relativedelta(years=1)
    # Converti end_date in una stringa formattata
    end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    return trade_date, initial_date, end_date


def main(sectors):
    # configurazione del logging
    logging.basicConfig( level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s" )
    
    #logging.disable(logging.CRITICAL)
    
    """symbols = ['AAL', 'AAPL', 'ABNB', 'ACAD', 'ACGL', 'ACIW', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AGIO', 'AKAM', 'ALGN', 'ALRM', 'AMAT', 'AMD', 'AMED', 
               'AMGN', 'AMKR', 'AMZN', 'APLS', 'APPS', 'ARWR', 'ATSG', 'AVGO', 'AZN', 'BCRX', 'BIDU', 'BILI', 'BKNG', 'BL', 'BLMN', 'BMBL', 'BMRN', 
               'BNTX', 'BPMC', 'BRKR', 'CAKE', 'CALM', 'CAR', 'CARG', 'CBRL', 'CDNS', 'CDW', 'CG', 'CGNX', 'CMCSA', 'CME', 'COIN', 'COLM', 'CORT', 
               'COST', 'CROX', 'CRSP', 'CRWD', 'CSCO', 'CSIQ', 'CTAS', 'CTSH', 'CYRX', 'CYTK', 'CZR', 'DASH', 'DBX', 'DDOG', 'DKNG', 'DLO', 'DLTR', 
               'DNLI', 'DOCU', 'EA', 'EBAY', 'EEFT', 'ENPH', 'ENTA', 'ENTG', 'ERII', 'ETSY', 'EVBG', 'EXAS', 'EXPE', 'EYE', 'FANG', 'FAST', 'FIVE', 
               'FLEX', 'FOLD', 'FORM', 'FOX', 'FRPT', 'FSLR', 'FTNT', 'GBDC', 'GDS', 'GH', 'GILD', 'GLNG', 'GLPI', 'GOGL', 'GOOGL', 'GPRE', 'GPRO', 
               'GTLB', 'HAIN', 'HCM', 'HCSG', 'HIBB', 'HOOD', 'HQY', 'HTHT', 'IART', 'IBKR', 'ICLR', 'ILMN', 'INCY', 'INSM', 'INTC', 'IOVA', 'IRDM', 
               'IRTC', 'IRWD', 'ISRG', 'ITRI', 'JACK', 'JD', 'KLIC', 'KRNT', 'KTOS', 'LAUR', 'LBRDK', 'LBTYA', 'LI', 'LITE', 'LIVN', 'LNT', 'LNTH', 
               'LOGI', 'LOPE', 'LPLA', 'LPSN', 'LRCX', 'LSCC', 'LYFT', 'MANH', 'MAR', 'MASI', 'MDB', 'MDLZ', 'MEDP', 'META', 'MKSI', 'MMSI', 
               'MNRO', 'MNST', 'MPWR', 'MRCY', 'MRNA', 'MSFT', 'MSTR', 'MTCH', 'MTSI', 'MU', 'MYGN', 'NAVI', 'NBIX', 'NDAQ', 'NEOG', 'NFLX', 'NMIH', 
               'NSIT', 'NTCT', 'NTES', 'NTNX', 'NTRA', 'NVCR', 'NVDA', 'NWSA', 'ODP', 'OKTA', 'OLLI', 'OMCL', 'ORLY', 'PAYX', 'PCH', 'PDD', 'PEGA', 
               'PENN', 'PEP', 'PGNY', 'PLAY', 'PLUG', 'POOL', 'POWI', 'PPC', 'PRAA', 'PRGS', 'PTC', 'PTCT', 'PTEN', 'PTON', 'PYPL', 'PZZA', 'QCOM', 
               'QDEL', 'QFIN', 'QLYS', 'RARE', 'RCM', 'REG', 'REGN', 'REYN', 'RGEN', 'RIVN', 'RMBS', 'ROIC', 'ROKU', 'RPD', 'RRR', 'RUN', 'SAGE', 
               'SAIA', 'SANM', 'SBAC', 'SBGI', 'SBLK', 'SBRA', 'SBUX', 'SEDG', 'SFM', 'SGRY', 'SHOO', 'SKYW', 'SLM', 'SMTC', 'SONO', 'SPWR', 'SRCL', 
               'SRPT', 'SSRM', 'STX', 'SWKS', 'SYNA', 'TMUS', 'TRIP', 'TRMB', 'TROW', 'TSCO', 'TSLA', 'TTEK', 'TTMI', 'TTWO', 'TXG', 'TXRH', 'UAL', 
               'UCTT', 'URBN', 'VCYT', 'VECO', 'VIAV', 'VIRT', 'VRNS', 'VRNT', 'VRSK', 'VRSN', 'VRTX', 'VSAT', 'WB', 'WDC', 'WERN', 'WING', 'WIX', 
               'WMG', 'WSC', 'WSFS', 'WWD', 'XP', 'XRAY', 'YY', 'ZD', 'ZG', 'ZI', 'ZLAB', 'ZM']
    """
    
    symbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX', 'AMD', 'AZN', 'QCOM', 'ADBE', 'PEP', 'TMUS', 'PDD', 'AMAT', 'CSCO', 
     'AMGN', 'MU', 'ISRG', 'CMCSA', 'LRCX', 'BKNG', 'INTC', 'VRTX', 'REGN', 'ADI', 'ADP', 'ABNB', 'CRWD', 'SBUX', 'MDLZ', 'CDNS', 'GILD', 'CTAS', 'CME', 
     'MAR', 'PYPL', 'ORLY', 'NTES', 'COIN', 'MRNA', 'ADSK', 'MNST', 'FTNT', 'JD', 'DASH', 'PAYX', 'MPWR', 'DDOG', 'VRSK', 'ACGL', 'EA', 'FAST', 'NDAQ', 
     'FANG', 'BIDU', 'CTSH', 'TSCO', 'CDW', 'FSLR', 'TTWO', 'EBAY', 'ICLR', 'MSTR', 'TROW', 'WDC', 'DLTR', 'STX', 'BNTX', 'LPLA', 'PTC', 'SBAC', 'ENTG', 
     'HOOD', 'DKNG', 'LI', 'ALGN', 'VRSN', 'ILMN', 'ENPH', 'SWKS', 'EXPE', 'MDB', 'UAL', 'WMG', 'BMRN', 'LOGI', 'NWSA', 'OKTA', 'FOX', 'MANH', 'CG', 'INCY', 
     'NTRA', 'NBIX', 'AKAM', 'TRMB', 'NTNX', 'POOL', 'IBKR', 'LNT', 'FLEX', 'MEDP', 'WING', 'SAIA', 'GLPI', 'SRPT', 'REG', 'TXRH', 'TTEK', 'WWD', 'ZG', 'RIVN', 
     'HTHT', 'CROX', 'INSM', 'XP', 'WIX', 'MKSI', 'LSCC', 'PPC', 'MTCH', 'SFM', 'ROKU', 'EXAS', 'MTSI', 'MASI', 'HQY', 'LBRDK', 'WSC', 'RGEN', 'ETSY', 'GTLB', 
     'NSIT', 'LBTYA', 'FIVE', 'FRPT', 'RMBS', 'REYN', 'LYFT', 'OLLI', 'LNTH', 'RRR', 'SRCL', 'XRAY', 'RCM', 'QLYS', 'PEGA', 'VRNS', 'MMSI', 'ITRI', 'ZI', 
     'FORM', 'SLM', 'GBDC', 'POWI', 'LOPE', 'URBN', 'PTEN', 'VIRT', 'CAR', 'GH', 'SANM', 'NEOG', 'SYNA', 'SBRA', 'RARE', 'LITE', 'PCH', 'SGRY', 'IRDM', 
     'SHOO', 'HCM', 'SKYW', 'QFIN', 'GLNG', 'FOLD', 'KTOS', 'IRTC', 'RUN', 'LIVN', 'BL', 'PTCT', 'PENN', 'CARG', 'VECO', 'WSFS', 'NMIH', 'GOGL', 'ZD', 'PGNY', 
     'KLIC', 'TRIP', 'QDEL', 'TXG', 'IART', 'WERN']    
        
    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate("Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn )
        
        profTot = []
        
        # Carica i settori e i simboli dal file CSV
        with open("csv_files/nasdaq_symbols.csv", mode="r") as file:
            csv_reader = csv.DictReader(file)
            symbols_data = {row["Symbol"]: row["Sector"] for row in csv_reader}
            
        # Recupera l´ultimo id del testing
        cur.execute("SELECT id FROM Testing")
        idTest = cur.fetchone()
            
        if idTest == None:
            idTest = 0
        else:
            idTest = idTest[0]
            idTest += 1

        # Ciclo principale
        for i in range(100):
            
            cur.execute("DELETE FROM sale;")
            conn.commit()
                
            cur.execute("DELETE FROM purchase;")
            conn.commit()
                
            cur.execute("DELETE FROM logindate;")
            conn.commit()
                
            cur.execute("DELETE FROM datatrader;")
            conn.commit()
            
            
            # Definiamo come costanti le soglie di acquisto e di vendita. La soglia di acquisto viene utilizzata per sapere quando acquistare un'azione, 
            # mentre la soglia di vendita viene utilizzata per sapere quando vendere un'azione.
            SA = random.randint(1,4)
            SV = random.randint(1,4)
                        
            trade_date, initial_date, endDate = getRandomDate(cur)
            #trade_date = '2018-04-06 18:30:00'
            #initial_date = '2018-04-06 18:30:00'
            #endDate = '2019-04-06 18:30:00'
            
            # Inizializzazione in caso di primo utilizzo
            budget = budgetInvestimenti = initial_budget = 10000
            equity = margin = 0
            budgetMantenimento = 0
            profitTotalUSD = profitTotalPerc = 0
            ticketPur = ticketSale = 0
                
            stateAgent = agentState.AgentState.INITIAL
            
            # Inserimento dei dati iniziali dell'agente nel database
            insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                
            #logging.info(f"Budget iniziale: {budget}\n")
            stateAgent = agentState.AgentState.SALE
            
            profitto1Y = trading1Years(symbols, stateAgent, trade_date, initial_date, endDate, budget, cur, conn, ticketPur, ticketSale, initial_budget, equity, margin, budgetInvestimenti, budgetMantenimento, profitTotalUSD, profitTotalPerc, symbols_data, SA, SV)
              
            insertDataDB.insertInTesting(idTest, "agent3", i, initial_date=initial_date, end_date=endDate, profit=profitto1Y, cur=cur, conn=conn)
            
            profTot.append(profitto1Y)
            
            print(f"\n{i}:  {profitto1Y}\n\n")
        
        # Calcolo del profitto medio.
        profittoMedio = sum(profTot) / len(profTot)
        logging.info(f"Profitto medio: {profittoMedio}\n")
        
        insertDataDB.insertInMiddleProfit(idTest, "agent3", profittoMedio, cur=cur, conn=conn)

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        #session_management.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")



def trading1Years(symbols, stateAgent, trade_date, initial_date, endDate, budget, cur, conn, ticketPur, ticketSale, initial_budget, equity, margin, budgetInvestimenti, budgetMantenimento, profitTotalUSD, profitTotalPerc, symbols_data, SA, SV):
    # Il ciclo principale esegue le operazioni di trading
    while True:

            ######################## inizio SALE
            if stateAgent == agentState.AgentState.SALE:
                #logging.info(f"Agent entrato nello stato Sale\n")

                # Recupera le vendite nel db.
                cur.execute("SELECT ticket_pur FROM sale")
                sales = {int(sale[0]) for sale in cur.fetchall()}

                #logging.info(f"I ticket delle vendite già effettuate sono: {sales}\n")

                # Recupera gli acquisti nel db.
                cur.execute("SELECT * FROM purchase;")
                purchasesDB = cur.fetchall()

                for pur in purchasesDB:
                    ticketP, volume, symbol, price_open = pur[1], pur[2], pur[3], pur[4]
                    
                    if int(ticketP) in sales:
                        continue
                    
                    cur.execute( f"SELECT high_price FROM nasdaq_actions WHERE symbol = '{symbol}' AND time_value_it='{trade_date}';" )    
                    result = cur.fetchone()

                    if not result:
                        #logging.info(f"Simbolo {symbol} non presente alla data: {trade_date}")
                        continue

                    price_current = result[0]

                    # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                    if price_current > price_open:
                        #logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n" )

                        # Calcolo del profitto:
                        profit = price_current - price_open
                        perc_profit = profit / price_open

                        # Rivendita con SV come percentuale di profitto
                        if perc_profit > (SV/100):

                            # aggiorno il budget
                            budgetInvestimenti = budgetInvestimenti + ( price_open * volume )

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            profit_10Perc = (profit * 10) / 100
                            profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + ( profit_10Perc * volume )
                            budgetMantenimento = budgetMantenimento + ( profit_90Perc * volume )

                            ticketSale += 1
                            
                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database                            
                            insertDataDB.insertInSale(dateObject, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn)

                            # Aggiornamento del valore dei profitti totali .
                            profitTotalUSD += profit * volume
                            profitTotalPerc = (profitTotalUSD/initial_budget)*100
                            
                            # Aggiornamento dello stato dell'agent nel database
                            insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                            #logging.info( f"Venduta azione {symbol}, profitto: {profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

                price_open = -1
                price_current = -1
                
                # Una volta controllati tutti i simboli azionari si passa allo stato di compravendita.
                #logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")
                stateAgent = agentState.AgentState.PURCHASE

            ######################## fine SALE

            
            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:
                #logging.info(f"Agent entrato nello stato Purchase\n")

                # Eseguire una query all'inizio per ottenere tutti i simboli e i prezzi
                #cur.execute(f"SELECT symbol, open_price FROM nasdaq_actions WHERE time_value_it = '{trade_date}';")
                #symbolsQ = cur.fetchall()  # Recupera i dati come lista di tuple

                # Converte symbolsQ in un dizionario per un accesso più veloce
                #symbolsQ_dict = {sy[0]: sy[1] for sy in symbolsQ}  # {symbol: price}

                # Acquisto di azioni finché c'è budget
                copyList = symbols.copy()
                
                while (budgetInvestimenti > 0) and (len(copyList) > 0):

                    # Scelgo un'azione random dal pool
                    symbolRandom = random.randint(0, len(copyList) - 1)
                    chosen_symbol = copyList[symbolRandom]
                    
                    cur.execute(f"SELECT high_price FROM nasdaq_actions WHERE time_value_it = '{trade_date}' AND symbol='{chosen_symbol}';")
                    price = cur.fetchone() # Recupera i dati come lista di tuple
                    
                    if price == None:
                        #logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                        copyList.remove(chosen_symbol)
                        continue
                    
                    price = price[0]
                    
                    
                    # Verifica se il simbolo è in un settore accettato e se è presente nelle query SQL
                    if chosen_symbol in symbols_data and symbols_data[chosen_symbol] in sectors:
                        #if chosen_symbol in symbolsQ_dict:
                        #    price = symbolsQ_dict[chosen_symbol]
                        
                            middlePrice = getValueMiddlePrice(chosen_symbol, trade_date, cur)
                            
                            if price < middlePrice*(1-(SA/100)):

                                # Calcolo volume e aggiornamento budget
                                volume = float(math.floor(1000 / price))
                                ticketPur += 1
                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                                # Inserimento nel database
                                insertDataDB.insertInPurchase(trade_date, ticketPur, volume, chosen_symbol, price, cur, conn)
                                budgetInvestimenti -= (price * volume)

                                # Aggiornamento stato
                                insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                                
                                copyList.remove(chosen_symbol)
                                
                                # Logging dell'acquisto
                                #if logging.getLogger().isEnabledFor(logging.INFO):
                                    #logging.info(f"Acquistata azione {chosen_symbol}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")
                            #else:
                                #if logging.getLogger().isEnabledFor(logging.INFO):
                                        #logging.info(f"Prezzo {price} non inferiore al prezzo medio {middlePrice*(1-(SA/100))} per {chosen_symbol} alla data {date}.")
                            
                            else:
                                copyList.remove(chosen_symbol)
                                #if logging.getLogger().isEnabledFor(logging.INFO):
                                    #logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                    else:
                        copyList.remove(chosen_symbol)
                        #if logging.getLogger().isEnabledFor(logging.INFO):
                            #logging.info(f"Settore di appartenenza per {chosen_symbol} non valido o non trovato.")

                    #logging.info(f"Cambio di stato da PURCHASE a WAIT\n\n")

                # Dopo lo stato di acquisto il programma entra nello stato di attesa
                stateAgent = agentState.AgentState.WAIT

            ######################## fine PURCHASE



            ######################## inizio WAIT
            if stateAgent == agentState.AgentState.WAIT:
                #logging.info(f"Agent entrato nello stato Wait\n")
                
                #dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                # Aggiornamento dello stato dell'agent nel database
                insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                #cur.execute( f"SELECT distinct time_value_it FROM nasdaq_actions WHERE time_value_it > '2020-06-26 18:45:00'AND EXTRACT(hour FROM time_value_it)='18' AND EXTRACT(minute FROM time_value_it)='45' ORDER BY time_value_it LIMIT 1;")

                forExtract = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                
                # Estrazione dell'ora e del minuto
                hour = forExtract.hour
                minute = forExtract.minute
                
                
                cur.execute( f"SELECT distinct time_value_it FROM nasdaq_actions WHERE time_value_it > '{trade_date}'AND EXTRACT(hour FROM time_value_it)={hour} AND EXTRACT(minute FROM time_value_it)={minute} ORDER BY time_value_it LIMIT 1;")


                #cur.execute( f"SELECT time_value_it FROM nasdaq_actions WHERE time_value_it > '{date}' ORDER BY time_value_it ASC LIMIT 1;" )
                #cur.execute( f"SELECT time_value_it + INTERVAL '1 day' FROM nasdaq_actions WHERE time_value_it = '{trade_date}';" )
                # Risolvere per date in cui non c'è il giorno dopo.

                trade_dateN = cur.fetchone()
                
                #if trade_dateN == None:
                #    cur.execute( f"SELECT time_value_it + INTERVAL '3 days' FROM nasdaq_actions WHERE time_value_it = '{trade_date}';" )
                #    trade_dateN = cur.fetchone()
                    
                trade_date = trade_dateN[0]                    
                trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

                if trade_date >= endDate:
                    break

                #logging.info(f"Cambio di stato da WAIT a SALE\n\n")
                logging.info(f"{initial_date} --> {trade_date} --> {endDate}: {profitTotalUSD} | {profitTotalPerc}")
                stateAgent = agentState.AgentState.SALE

            ######################## fine WAIT
    return profitTotalPerc



def getValueMiddlePrice(chosen_symbol, date, cur):
    start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - timedelta(days=50)
    cur.execute("SELECT close_price FROM nasdaq_actions WHERE symbol = %s AND time_value_it BETWEEN %s AND %s;", (chosen_symbol, start_date, date))
    prices = [row[0] for row in cur.fetchall()]
    
    if len(prices) == 0:
        return 0  # O gestisci come preferisci il caso senza dati
    
    return sum(prices) / len(prices)




def getSectorSymbols():
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    
    symbolsAccepted = ['AAL', 'AAPL', 'ABNB', 'ACAD', 'ACGL', 'ACIW', 'ADBE', 'ADI', 'ADP', 'ADSK', 'AGIO', 'AKAM', 'ALGN', 'ALRM', 'AMAT', 'AMD', 'AMED', 
               'AMGN', 'AMKR', 'AMZN', 'APLS', 'APPS', 'ARWR', 'ATSG', 'AVGO', 'AZN', 'BCRX', 'BIDU', 'BILI', 'BKNG', 'BL', 'BLMN', 'BMBL', 'BMRN', 
               'BNTX', 'BPMC', 'BRKR', 'CAKE', 'CALM', 'CAR', 'CARG', 'CBRL', 'CDNS', 'CDW', 'CG', 'CGNX', 'CMCSA', 'CME', 'COIN', 'COLM', 'CORT', 
               'COST', 'CROX', 'CRSP', 'CRWD', 'CSCO', 'CSIQ', 'CTAS', 'CTSH', 'CYRX', 'CYTK', 'CZR', 'DASH', 'DBX', 'DDOG', 'DKNG', 'DLO', 'DLTR', 
               'DNLI', 'DOCU', 'EA', 'EBAY', 'EEFT', 'ENPH', 'ENTA', 'ENTG', 'ERII', 'ETSY', 'EVBG', 'EXAS', 'EXPE', 'EYE', 'FANG', 'FAST', 'FIVE', 
               'FLEX', 'FOLD', 'FORM', 'FOX', 'FRPT', 'FSLR', 'FTNT', 'GBDC', 'GDS', 'GH', 'GILD', 'GLNG', 'GLPI', 'GOGL', 'GOOGL', 'GPRE', 'GPRO', 
               'GTLB', 'HAIN', 'HCM', 'HCSG', 'HIBB', 'HOOD', 'HQY', 'HTHT', 'IART', 'IBKR', 'ICLR', 'ILMN', 'INCY', 'INSM', 'INTC', 'IOVA', 'IRDM', 
               'IRTC', 'IRWD', 'ISRG', 'ITRI', 'JACK', 'JD', 'KLIC', 'KRNT', 'KTOS', 'LAUR', 'LBRDK', 'LBTYA', 'LI', 'LITE', 'LIVN', 'LNT', 'LNTH', 
               'LOGI', 'LOPE', 'LPLA', 'LPSN', 'LRCX', 'LSCC', 'LYFT', 'MANH', 'MAR', 'MASI', 'MDB', 'MDLZ', 'MEDP', 'MEOH', 'META', 'MKSI', 'MMSI', 
               'MNRO', 'MNST', 'MPWR', 'MRCY', 'MRNA', 'MSFT', 'MSTR', 'MTCH', 'MTSI', 'MU', 'MYGN', 'NAVI', 'NBIX', 'NDAQ', 'NEOG', 'NFLX', 'NMIH', 
               'NSIT', 'NTCT', 'NTES', 'NTNX', 'NTRA', 'NVCR', 'NVDA', 'NWSA', 'ODP', 'OKTA', 'OLLI', 'OMCL', 'ORLY', 'PAYX', 'PCH', 'PDD', 'PEGA', 
               'PENN', 'PEP', 'PGNY', 'PLAY', 'PLUG', 'POOL', 'POWI', 'PPC', 'PRAA', 'PRGS', 'PTC', 'PTCT', 'PTEN', 'PTON', 'PYPL', 'PZZA', 'QCOM', 
               'QDEL', 'QFIN', 'QLYS', 'RARE', 'RCM', 'REG', 'REGN', 'REYN', 'RGEN', 'RIVN', 'RMBS', 'ROIC', 'ROKU', 'RPD', 'RRR', 'RUN', 'SAGE', 
               'SAIA', 'SANM', 'SBAC', 'SBGI', 'SBLK', 'SBRA', 'SBUX', 'SEDG', 'SFM', 'SGRY', 'SHOO', 'SKYW', 'SLM', 'SMTC', 'SONO', 'SPWR', 'SRCL', 
               'SRPT', 'SSRM', 'STX', 'SWKS', 'SYNA', 'TMUS', 'TRIP', 'TRMB', 'TROW', 'TSCO', 'TSLA', 'TTEK', 'TTMI', 'TTWO', 'TXG', 'TXRH', 'UAL', 
               'UCTT', 'URBN', 'VCYT', 'VECO', 'VIAV', 'VIRT', 'VRNS', 'VRNT', 'VRSK', 'VRSN', 'VRTX', 'VSAT', 'WB', 'WDC', 'WERN', 'WING', 'WIX', 
               'WMG', 'WSC', 'WSFS', 'WWD', 'XP', 'XRAY', 'YY', 'ZD', 'ZG', 'ZI', 'ZLAB', 'ZM']

    # Dizionario per memorizzare i simboli e il settore di appartenenza
    diz = dict()

    # Leggi il file CSV in un DataFrame
    df = pd.read_csv('csv_files/nasdaq_symbols.csv')

    # Apri il file CSV in modalità lettura
    with open('csv_files/nasdaq_symbols.csv', mode='r') as file:
        # Crea un lettore CSV con DictReader
        csv_reader = csv.DictReader(file)

        # Aggiungi i simboli accettati e il settore di appartenenza al dizionario
        for col in csv_reader:
            if col['Symbol'] in symbolsAccepted:
                diz[col['Symbol']] = col['Sector']

    # Ottieni le chiavi del dizionario (i simboli)
    key_diz = list(diz.keys())

    print(diz.keys())

    settoriDupl = diz.values()
    settori = []
    for sett in settoriDupl:
        if sett not in settori:
            if sett != '':
                settori.append(sett)
                insertDataDB.insertInSector(str(sett), cur, conn)
    print(settori)

    print(len(key_diz))
    
    cur.close()
    conn.close()

    # Ritorna il dizionario con i simboli e il settore di appartenenza
    return diz





if __name__ == "__main__":
    
    getSectorSymbols()
    
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()

    # Recupera i settori nel database:
    cur.execute("SELECT * FROM sector;")
    sectors = [ sec[0] for sec in cur.fetchall() ]  # Estrai solo il primo elemento di ogni tupla
    #print(sectors)
    
    cur.close()
    conn.close()

    i = 1
    for sec in sectors:
        #print(f"{i}: {sec}\n")
        i += 1

    #print( f"Scegli uno o più settori su cui applicare l'agente (indicando i numeri con virgole se più di uno):\n" )
    #choises = input("Scrivi i numeri: ")

    #choises = choises.split(",")
    #choises = [int(x) for x in choises]
    #print(choises)
    choises = [1,2,3,4,5,6,7,8,9,10,11]

    sectors = [sectors[i - 1] for i in choises]
    print(sectors)
    
    #date = '2023-09-08 15:30:00'

    main(sectors)


