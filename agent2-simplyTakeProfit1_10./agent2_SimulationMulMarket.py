# import MetaTrader5 as mt5
import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent1')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent2')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/agent3')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

import agentState
from db import insertDataDB, connectDB
from symbols import getSector, getSymbols
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


def main():
    # configurazione del logging
    logging.basicConfig( level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s" )
    
    #logging.disable(logging.CRITICAL)
            
    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate("Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn )
        
        profTot = []
        
        datesToTrade = generate100RandomDates(cur)
        
        market = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']
        ##market = ['larg_comp_eu_actions']
        for m in market:
            if m == 'nasdaq_actions':
                symbols = getSymbols.getSymbolsNasda100()
            elif m == 'nyse_actions':
                symbols = getSymbols.getSymbolsNyse100()
            elif m == 'larg_comp_eu_actions':
                symbols = getSymbols.getSymbolsLargestCompEU100()
            
            # Ciclo per la variazione dei 10 valori per il TAKE PROFIT: rivendita con profitto del 1% - 10%
            for i in range(1, 2):
                #TK = i/100
                TK = 0.9
                
                #datesToTrade = generate100RandomDates(cur, m)
                
                # get last idTest
                idTest = getLastIdTest(cur)
            
                # Ciclo principale
                for i in range(10):
                    clearSomeTablesDB(cur, conn)
                    
                    #trade_date, initial_date, endDate = getRandomDate(cur, m)
                    #trade_date = '2008-11-25 00:00:00'   |   initial_date = '2008-11-25 00:00:00'   |   endDate = '2009-11-25 00:00:00' --> per test specifici
                    trade_date, initial_date, endDate = datesToTrade[i]
                    
                    # trading per 1 anno
                    profitto1Y = tradingYear(cur, conn, symbols, trade_date, m, TK, initial_date, endDate)
                    
                    profitto1Y = round(profitto1Y, 4)
                    
                    # Inserimento dei dati relativi al profitto dell'agente nel database
                    insertDataDB.insertInTesting(idTest, "agent2", i, initial_date=initial_date, end_date=endDate, profit=profitto1Y, market=m, notes=f"TAKE PROFIT = {TK}% ",  cur=cur, conn=conn)
                    
                    profTot.append(profitto1Y)
                    
                    print(f"\n{i}:  {profitto1Y}\n\n")
                    
                    # Metti in pausa il programma per il tempo specificato
                    #time_module.sleep(600)
                
                # Calcolo del profitto medio relativo a tutte le iterazioni
                profittoMedio = sum(profTot) / len(profTot)
                logging.info(f"Profitto medio: {profittoMedio}\n")
                
                insertDataDB.insertInMiddleProfit(idTest, "agent2", profittoMedio, cur=cur, conn=conn)
            
                # end for
                
            # end for

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
    
        cur.close()
        conn.close()
        logging.shutdown()
        return




def tradingYear(cur, conn, symbols, trade_date, market, TP, initial_date, endDate):    
    # Inizializzazione ad ogni iterazione
    budget = budgetInvestimenti = initial_budget = 1000
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = equity = margin = ticketPur = ticketSale =budgetMantenimento = 0
 
    # Inserimento dei dati iniziali dell'agente nel database
    insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                
    stateAgent = agentState.AgentState.SALE
            
    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    cur.execute(f"SELECT distinct(symbol) FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
    resSymbolDisp = cur.fetchall()
    #symbolDisp = [sy[0] for sy in resSymbolDisp if sy[0] in symbols]
    symbolDisp = [sy[0] for sy in resSymbolDisp]
    
    # Il ciclo principale esegue le operazioni di trading per 1 anno
    while True:

            ######################## inizio SALE
            if stateAgent == agentState.AgentState.SALE:
                #logging.info(f"Agent entrato nello stato Sale\n")

                # Recupera i ticker relativi agli acquisti già venduti nel db.
                cur.execute("SELECT ticket_pur FROM sale")
                sales = {int(sale[0]) for sale in cur.fetchall()}     #logging.info(f"I ticket delle vendite già effettuate sono: {sales}\n")

                # Recupera tutti valori delle colonne degli acquisti nel db.
                cur.execute("SELECT * FROM purchase order by now;")
                purchasesDB = cur.fetchall()
                
                # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                for pur in purchasesDB:
                    datePur, ticketP, volume, symbol, price_open = pur[0], pur[2], pur[3], pur[4], pur[5]
                    
                    # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                    if int(ticketP) in sales:
                        continue
                    
                    # Recupero del prezzo più alto relativo alla giornata di trading del simbolo azionario
                    cur.execute( f"SELECT high_price FROM {market} WHERE symbol = '{symbol}' AND time_value_it='{trade_date}';" )    
                    result = cur.fetchone()

                    if not result:
                        #logging.info(f"Simbolo {symbol} non presente alla data: {trade_date}")
                        continue

                    # Memorizzo il risultato relativo al prezzo più alto della giornata di trading
                    price_current = result[0]

                    # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                    if price_current > price_open:   #logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n" )
                        
                        # Calcolo del profitto:
                        profit = price_current - price_open
                        perc_profit = profit / price_open

                        # Rivendita con l'1 % di profitto
                        if perc_profit > TP:

                            # aggiorno il budget
                            budgetInvestimenti = budgetInvestimenti + ( price_open * volume )

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            profit_10Perc = (profit * 10) / 100
                            profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + ( profit_10Perc * volume )
                            budgetMantenimento = budgetMantenimento + ( profit_90Perc * volume )

                            ticketSale += 1
                            
                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                            #datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database                            
                            insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn)
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                            profitTotalUSD += profit * volume
                            profitTotalPerc = (profitTotalUSD/initial_budget)*100
                            
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                            profitNotReinvested = budgetMantenimento
                            profitNotReinvestedPerc = (profitNotReinvested/initial_budget)*100
                            
                            # Aggiornamento dello stato dell'agent nel database
                            insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                            
                            #logging.info( f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current}, prezzo di acquisto: {price_open}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

                price_open = -1
                price_current = -1
                
                # Una volta controllati tutti i simboli azionari si passa allo stato di compravendita.
                stateAgent = agentState.AgentState.PURCHASE  #logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")

            ######################## fine SALE

            
            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:   #logging.info(f"Agent entrato nello stato Purchase\n")
                
                # Acquisto di azioni in modo casuale dal pool di titoli azionari finché c'è budget
                while budgetInvestimenti > 0:        

                    # Scelgo un'azione random dal pool di titoli azionari
                    chosen_symbol = symbolDisp[random.randint(0, len(symbolDisp) - 1)]
                    
                    # Recupero del prezzo di apertura del simbolo azionario scelto nella giornata attuale di trading
                    cur.execute(f"SELECT open_price FROM {market} WHERE time_value_it = '{trade_date}' AND symbol='{chosen_symbol}';")
                    price = cur.fetchone() # Recupera i dati come lista di tuple
                    
                    if price == None: #logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                        continue
    
                    price = price[0]
                    
                    if price == 0: # Se il prezzo è = 0, allora non si può acquistare
                        continue                    
                    
                    # Verifica se il simbolo è in un settore accettato e se è presente tra tutti i settori nek database:
                    #if chosen_symbol in sectorSymbols and sectorSymbols[chosen_symbol] in sectors:
                        
                    # Calcolo volume e aggiornamento budget
                    #volumeAcq = float(math.floor(10 / price))
                    volumeAcq = float(10 / price)
                    if volumeAcq == 0:
                        continue
                    ticketPur += 1
                    dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento nel database
                    insertDataDB.insertInPurchase(trade_date, ticketPur, volumeAcq, chosen_symbol, price, cur, conn)
                    budgetInvestimenti -= (price * volumeAcq)

                    # Aggiornamento stato
                    insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                            
                        # Logging dell'acquisto
                        #if logging.getLogger().isEnabledFor(logging.INFO):
                            #logging.info(f"Acquistata azione {chosen_symbol} in data: {trade_date}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")
                
                    #else:
                    #    if logging.getLogger().isEnabledFor(logging.INFO):
                    #        logging.info(f"Settore di appartenenza per {chosen_symbol} non valido o non trovato.")

                # Dopo lo stato di acquisto il programma entra nello stato di attesa
                stateAgent = agentState.AgentState.SALE_IMMEDIATE  #logging.info(f"Cambio di stato da PURCHASE a SALE IMMEDIATE\n\n")

            ######################## fine PURCHASE
            
            
            ######################## inizio SALE_IMMEDIATE
            
            if stateAgent == agentState.AgentState.SALE_IMMEDIATE: #logging.info(f"Cambio di stato da WAIT a SALE_IMMEDIATE\n\n")
                # Recupera i ticker relativi agli acquisti già venduti nel db.
                cur.execute("SELECT ticket_pur FROM sale")
                sales = {int(sale[0]) for sale in cur.fetchall()}  #logging.info(f"I ticket delle vendite già effettuate sono: {sales}\n")

                # Recupera tutti valori delle colonne degli acquisti nel db.
                cur.execute("SELECT * FROM purchase order by now;")
                purchasesDB = cur.fetchall()
                
                # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                for pur in purchasesDB:
                    datePur, ticketP, volume, symbol, price_open = pur[0], pur[2], pur[3], pur[4], pur[5]
                    
                    # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                    if int(ticketP) in sales:
                        continue
                    
                    # Recupero del prezzo più alto relativo alla giornata di trading del simbolo azionario
                    cur.execute( f"SELECT high_price FROM {market} WHERE symbol = '{symbol}' AND time_value_it='{trade_date}';" )    
                    result = cur.fetchone()

                    if not result:
                        #logging.info(f"Simbolo {symbol} non presente alla data: {trade_date}")
                        continue

                    # Memorizzo il risultato relativo al prezzo più alto della giornata di trading
                    price_current = result[0]

                    # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                    if price_current > price_open:  #logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n" )

                        # Calcolo del profitto:
                        profit = price_current - price_open
                        perc_profit = profit / price_open

                        # Rivendita con l'1 % di profitto
                        if perc_profit > TP:

                            # aggiorno il budget
                            budgetInvestimenti = budgetInvestimenti + ( price_open * volume )

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            profit_10Perc = (profit * 10) / 100
                            profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + ( profit_10Perc * volume )
                            budgetMantenimento = budgetMantenimento + ( profit_90Perc * volume )

                            ticketSale += 1
                            
                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                            #datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database                            
                            insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn)
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                            profitTotalUSD += profit * volume
                            profitTotalPerc = (profitTotalUSD/initial_budget)*100
                            
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                            profitNotReinvested = budgetMantenimento
                            profitNotReinvestedPerc = (profitNotReinvested/initial_budget)*100
                            
                            
                            # Aggiornamento dello stato dell'agent nel database
                            insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                            
                            #logging.info( f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current}, prezzo di acquisto: {price_open}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

                price_open = -1
                price_current = -1
                                
                stateAgent = agentState.AgentState.WAIT  #logging.info(f"Cambio di stato da SALE IMMEDIATE a WAIT\n\n")
            
            ########################



            ######################## inizio WAIT
            if stateAgent == agentState.AgentState.WAIT:  #logging.info(f"Agent entrato nello stato Wait\n")
                
                # Aggiornamento dello stato dell'agent nel database
                insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                cur.execute( f"SELECT distinct time_value_it FROM {market} WHERE time_value_it > '{trade_date}' ORDER BY time_value_it LIMIT 1;")

                trade_dateN = cur.fetchone()
                
                trade_date = trade_dateN[0]                    
                trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

                if trade_date >= endDate:

                    # Recupera i ticker relativi agli acquisti già venduti nel db.
                    cur.execute("SELECT ticket_pur FROM sale")
                    sales = {int(sale[0]) for sale in cur.fetchall()}
                    
                    # Recupera tutti valori delle colonne degli acquisti nel db.
                    cur.execute("SELECT * FROM purchase order by now;")
                    purchasesDB = cur.fetchall()
                    
                    # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                    for pur in purchasesDB:
                        datePur, ticketP, volume, symbol, price_open = pur[0], pur[2], pur[3], pur[4], pur[5]
                        
                        # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                        if int(ticketP) in sales:
                            continue
                        
                        # Recupero del prezzo più alto relativo alla giornata di trading del simbolo azionario
                        cur.execute(f"SELECT high_price FROM {market} WHERE symbol = '{symbol}' AND time_value_it='{trade_date}';")
                        result = cur.fetchone()
                        
                        if result:
                            # Memorizzo il risultato relativo al prezzo più alto della giornata di trading
                            price_current = result[0]    
                            
                            if price_current > price_open:   
                                # Calcolo del profitto:
                                profit = price_current - price_open
                                perc_profit = profit / price_open
                            
                                # Vendiamo per l'ultima volta e teniamo nel deposito.
                                budgetMantenimento = budgetMantenimento + (price_open * volume) + profit
                                
                                ticketSale += 1
                            
                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale( dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn )
                                    
                                # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                                profitTotalUSD += profit * volume
                                profitTotalPerc = (profitTotalUSD / initial_budget) * 100
                                    
                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                            
                            else:
                                # Non c'è profitto, vendiamo al prezzo corrente.
                                budgetMantenimento = budgetMantenimento + (price_current * volume)

                                ticketSale += 1
                                
                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, 0, 0, cur, conn )
                                                                    
                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                    break

                #logging.info(f"Cambio di stato da WAIT a SALE\n\n")
                #logging.info(f"{initial_date} --> {trade_date} --> {endDate}: profUSD: {profitTotalUSD} | profPerc:{profitTotalPerc}")
                #logging.info(f"{initial_date} --> {trade_date} --> {endDate}:   {round(profitNotReinvested, 4)} USD  |   {round(profitNotReinvestedPerc, 4)} %")
                
                stateAgent = agentState.AgentState.SALE

            ######################## fine WAIT
              
    #return profitTotalPerc
    return profitNotReinvestedPerc




def getRandomDate(cursor):
    # Seleziona un giorno casuale all'interno del range temporale che sia più piccolo di 365 giorni rispetto alla data massima presente nel database
    #cursor.execute("SELECT MAX(time_value_it) - INTERVAL '1 year 2 month 1 days' FROM nasdaq_actions;")
    #max_date = cursor.fetchone()[0]
    max_date = datetime(2023, 11, 1, 0, 0, 0)
    
    # Determina la data minima (ad esempio, la data più antica nella tabella)
    #cursor.execute("SELECT MIN(time_value_it) + INTERVAL '23 year 11 month 8 day' FROM nasdaq_actions;")
    #min_date = cursor.fetchone()[0]
    min_date =  datetime(1999, 1, 1, 0, 0, 0)
                
    # Seleziona una data casuale all'interno dell'intervallo
    #cursor.execute("SELECT time_value_it FROM nasdaq_actions WHERE time_value_it BETWEEN %s AND %s ORDER BY RANDOM() LIMIT 1;", (min_date, max_date))
    #trade_date = cursor.fetchone()[0]
    #trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')
                
    # Calcola una data casuale tra min_date e max_date
    while True:
        random_days = random.randint(0, (max_date - min_date).days)
        random_date = min_date + timedelta(days=random_days)
        
        # Verifica se la data casuale esiste nel database
        cursor.execute(f"SELECT time_value_it FROM nyse_actions WHERE time_value_it = '{random_date}';")
        result = cursor.fetchone()
        
        if result:  # Data trovata nel database
            # Verifica se la data casuale esiste nel database
            cursor.execute(f"SELECT time_value_it FROM larg_comp_eu_actions WHERE time_value_it = '{random_date}';")
            result1 = cursor.fetchone()
            
            if result1:
                # Verifica se la data casuale esiste nel database
                cursor.execute(f"SELECT time_value_it FROM nasdaq_actions WHERE time_value_it = '{random_date}';")
                result2 = cursor.fetchone()
                
                if result2:
                    trade_date = result[0]
                    
                    trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')
            
                    # Converti la stringa in un oggetto datetime
                    initial_date = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Aggiungi 1 anno usando relativedelta
                    end_date = initial_date + relativedelta(years=1)
                    # Converti end_date in una stringa formattata
                    end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
                    
                    return trade_date, initial_date, end_date
                
                else:  # Data non trovata nel database
                    continue
            
            else:  # Data non trovata nel database
                continue
        else:  # Data non trovata nel database
            continue
    

def generate100RandomDates(cursor):
    # Genera 100 date casuali all'interno del range temporale che sia più piccolo di 365 giorni rispetto alla data massima presente nel database
    result = []
    for _ in range(100):
        trade_date, initial_date, end_date = getRandomDate(cursor)
        result.append((trade_date, initial_date, end_date))
    return result


def getLastIdTest(cur):
    # Recupera l'ultimo id del testing
    cur.execute("SELECT id FROM Testing ORDER BY id desc;")
    idTest = cur.fetchone()
            
    if idTest == None:
        idTest = 0
    else:
        idTest = idTest[0]
        idTest += 1
    return idTest


def clearSomeTablesDB(cur, conn):
    cur.execute("DELETE FROM sale;")
    conn.commit()
                
    cur.execute("DELETE FROM purchase;")
    conn.commit()
                
    cur.execute("DELETE FROM logindate;")
    conn.commit()
                
    cur.execute("DELETE FROM datatrader;")
    conn.commit()
    

if __name__ == "__main__":

    main()



"""

def tradingYear(cur, conn, symbols, trade_date, market, TK, initial_date, endDate):    
    # Inizializzazione ad ogni iterazione
    budget = budgetInvestimenti = initial_budget = 1000
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = equity = margin = budgetMantenimento = ticketPur = ticketSale = 0
    
    with open("purchase_agent2.txt", "a") as f:
    #    f.write("Iterazione %s:\n" % str(i))
            
    #with open("sale_agent2.txt", "a") as f:
    #    f.write("Iterazione %s:\n" % str(i))

                
    # Inserimento dei dati iniziali dell'agente nel database          
    #insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                         
    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    cur.execute(f"SELECT distinct(symbol) FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
    symbolDisp = [sy[0] for sy in cur.fetchall()]
    
    stateAgent = agentState.AgentState.SALE
    
    # Il ciclo principale esegue le operazioni di trading per 1 anno
    while True:
        if stateAgent == agentState.AgentState.SALE:
            stateAgent = handle_sale_state( cur, conn, trade_date, market, TK, initial_budget, budgetInvestimenti, budgetMantenimento, profitTotalUSD, ticketSale, stateAgent, budget, equity, margin)
        
        elif stateAgent == agentState.AgentState.PURCHASE:
            stateAgent = handle_purchase_state( cur, conn, trade_date, market, symbolDisp, initial_budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, ticketPur, stateAgent, budget, equity, margin)
        
        elif stateAgent == agentState.AgentState.SALE_IMMEDIATE:
            stateAgent = handle_sale_immediate_state( cur, conn, trade_date, market, TK, initial_budget, budgetInvestimenti, budgetMantenimento, profitTotalUSD, ticketSale, stateAgent, budget, equity, margin)
        
        elif stateAgent == agentState.AgentState.WAIT:
            trade_date, stateAgent = handle_wait_state( cur, conn, initial_date, trade_date, endDate, market, stateAgent, initial_budget, budget, equity, margin, budgetInvestimenti, budgetMantenimento, profitTotalUSD, profitTotalPerc, profitNotReinvested, profitNotReinvestedPerc)

        # Terminazione del ciclo
        if trade_date >= endDate:
            # vendita di tutte le azioni rimanenti
            profitNotReinvestedPerc, profitNotReinvested = sale_all_remaining(cur, conn, trade_date, market, TK, initial_budget, budgetInvestimenti, budgetMantenimento, profitTotalUSD, ticketSale, stateAgent, budget, equity, margin)
            
            break

    # Calcolo profitto non reinvestito
    profitNotReinvestedPerc = (budgetMantenimento / initial_budget) * 100
    
    return profitNotReinvestedPerc
        

def handle_sale_state(cur, conn, trade_date, market, TK, initial_budget, budgetInvestimenti, budgetMantenimento, profitTotalUSD, ticketSale, stateAgent, budget, equity, margin):
    # Recupera i ticker relativi agli acquisti già venduti nel db.
    cur.execute("SELECT ticket_pur FROM sale")
    sales = {int(sale[0]) for sale in cur.fetchall()}
    # logging.info(f"I ticket delle vendite già effettuate sono: {sales}\n")

    # Recupera tutti valori delle colonne degli acquisti nel db.
    cur.execute("SELECT * FROM purchase order by now;")
    purchasesDB = cur.fetchall()
    
    # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
    for pur in purchasesDB:
        datePur, ticketP, volume, symbol, price_open = pur[0], pur[2], pur[3], pur[4], pur[5]
        
        # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
        if int(ticketP) in sales:
            continue
        
        # Recupero del prezzo più alto relativo alla giornata di trading del simbolo azionario
        cur.execute(f"SELECT high_price FROM {market} WHERE symbol = '{symbol}' AND time_value_it='{trade_date}';")
        result = cur.fetchone()

        if not result:
            # logging.info(f"Simbolo {symbol} non presente alla data: {trade_date}")
            continue

        # Memorizzo il risultato relativo al prezzo più alto della giornata di trading
        price_current = result[0]

        # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
        if price_current > price_open:
            # logging.info(f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n")

            # Calcolo del profitto:
            profit = price_current - price_open
            perc_profit = profit / price_open

            # Rivendita con l'1 % di profitto
            if perc_profit > TK:

                # aggiorno il budget
                budgetInvestimenti = budgetInvestimenti + (price_open * volume)

                # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                profit_10Perc = (profit * 10) / 100
                profit_90Perc = (profit * 90) / 100
                budgetInvestimenti = budgetInvestimenti + (profit_10Perc * volume)
                budgetMantenimento = budgetMantenimento + (profit_90Perc * volume)

                ticketSale += 1
                
                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                insertDataDB.insertInSale(
                    dateObject, datePur, ticketP, ticketSale, volume, symbol, 
                    price_current, price_open, profit, perc_profit, cur, conn
                )
                
                # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                profitTotalUSD += profit * volume
                profitTotalPerc = (profitTotalUSD / initial_budget) * 100
                
                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                profitNotReinvested = budgetMantenimento
                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                
                # Aggiornamento dello stato dell'agent nel database
                #insertDataDB.insertInDataTrader( dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn )
                
                # logging.info(f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, "
                #              f"prezzo attuale:{price_current}, prezzo di acquisto: {price_open}, con profitto di: "
                #              f"{profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, "
                #              f"budgetMantenimento: {budgetMantenimento}")

    price_open = -1
    price_current = -1
    
    # Una volta controllati tutti i simboli azionari si passa allo stato di compravendita.
    # logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")
    return agentState.AgentState.PURCHASE


def handle_purchase_state(cur, conn, trade_date, market, symbolDisp, initial_budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, ticketPur, stateAgent, budget, equity, margin):
    ######################## inizio PURCHASE
    while budgetInvestimenti > 0:
        # Scelgo un'azione random dal pool di titoli azionari
        chosen_symbol = symbolDisp[random.randint(0, len(symbolDisp) - 1)]
        
        # Recupero del prezzo di apertura del simbolo azionario scelto nella giornata attuale di trading
        cur.execute(f"SELECT open_price FROM {market} WHERE time_value_it = '{trade_date}' AND symbol='{chosen_symbol}';")
        price = cur.fetchone()  # Recupera i dati come lista di tuple
        
        if price is None:
            # logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
            continue
        
        price = price[0]
        # Se il prezzo è = 0, allora non si può acquistare
        if price == 0:
            continue
        
        # Verifica se il simbolo è in un settore accettato e se è presente tra tutti i settori nel database:
        # if chosen_symbol in sectorSymbols and sectorSymbols[chosen_symbol] in sectors:
        
        # Calcolo volume e aggiornamento budget
        # volumeAcq = float(math.floor(10 / price))
        volumeAcq = float(10 / price)
        if volumeAcq == 0:
            continue
        
        ticketPur += 1
        dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

        # Inserimento nel database
        insertDataDB.insertInPurchase(trade_date, ticketPur, volumeAcq, chosen_symbol, price, cur, conn)
        budgetInvestimenti -= (price * volumeAcq)

        # Aggiornamento stato
        #insertDataDB.insertInDataTrader( trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn )
        
        # Logging dell'acquisto
        # if logging.getLogger().isEnabledFor(logging.INFO):
        #     logging.info(f"Acquistata azione {chosen_symbol} in data: {trade_date}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")
    
        # else:
        #     if logging.getLogger().isEnabledFor(logging.INFO):
        #         logging.info(f"Settore di appartenenza per {chosen_symbol} non valido o non trovato.")

    # logging.info(f"Cambio di stato da PURCHASE a WAIT\n\n")

    # Dopo lo stato di acquisto il programma entra nello stato di attesa
    return agentState.AgentState.SALE_IMMEDIATE
    ######################## fine PURCHASE


def handle_sale_immediate_state(cur, conn, trade_date, market, TK, initial_budget, budgetInvestimenti, budgetMantenimento, profitTotalUSD, ticketSale, stateAgent, budget, equity, margin):
        # Recupera i ticker relativi agli acquisti già venduti nel db.
        cur.execute("SELECT ticket_pur FROM sale")
        sales = {int(sale[0]) for sale in cur.fetchall()}

        # logging.info(f"I ticket delle vendite già effettuate sono: {sales}\n")

        # Recupera tutti valori delle colonne degli acquisti nel db.
        cur.execute("SELECT * FROM purchase order by now;")
        purchasesDB = cur.fetchall()

        # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
        for pur in purchasesDB:
            datePur, ticketP, volume, symbol, price_open = pur[0], pur[2], pur[3], pur[4], pur[5]

            # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
            if int(ticketP) in sales:
                continue

            # Recupero del prezzo più alto relativo alla giornata di trading del simbolo azionario
            cur.execute(f"SELECT high_price FROM {market} WHERE symbol = '{symbol}' AND time_value_it='{trade_date}';")
            result = cur.fetchone()

            if not result:
                # logging.info(f"Simbolo {symbol} non presente alla data: {trade_date}")
                continue

            # Memorizzo il risultato relativo al prezzo più alto della giornata di trading
            price_current = result[0]

            # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
            if price_current > price_open:
                # logging.info(f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n")

                # Calcolo del profitto:
                profit = price_current - price_open
                perc_profit = profit / price_open

                # Rivendita con l'1 % di profitto
                if perc_profit > TK:
                    # Aggiorno il budget
                    budgetInvestimenti += (price_open * volume)

                    # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                    profit_10Perc = (profit * 10) / 100
                    profit_90Perc = (profit * 90) / 100
                    budgetInvestimenti += (profit_10Perc * volume)
                    budgetMantenimento += (profit_90Perc * volume)

                    ticketSale += 1

                    dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                    insertDataDB.insertInSale( dateObject, datePur, ticketP, ticketSale, volume, symbol,  price_current, price_open, profit, perc_profit, cur, conn)

                    # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                    profitTotalUSD += profit * volume
                    profitTotalPerc = (profitTotalUSD / initial_budget) * 100

                    # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                    profitNotReinvested = budgetMantenimento
                    profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100

                    # Aggiornamento dello stato dell'agent nel database
                    #insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                    # logging.info(f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current}, prezzo di acquisto: {price_open}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

        price_open = -1
        price_current = -1

        # Una volta controllati tutti i simboli azionari si passa allo stato di attesa.
        # logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")
        return  agentState.AgentState.WAIT
    ########################
         

def handle_wait_state(cur, conn, initial_date, trade_date, endDate, market, stateAgent, initial_budget, budget, equity, margin, budgetInvestimenti, budgetMantenimento, profitTotalUSD, profitTotalPerc, profitNotReinvested, profitNotReinvestedPerc):
    # Aggiornamento dello stato dell'agent nel database
        #insertDataDB.insertInDataTrader( trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn )

        # Selezione della prossima data disponibile per il trading
        cur.execute(f"SELECT DISTINCT time_value_it FROM {market} WHERE time_value_it > '{trade_date}' ORDER BY time_value_it LIMIT 1;")
        trade_dateN = cur.fetchone()

        # Aggiorna la data di trading se disponibile
        if trade_dateN:
            trade_date = trade_dateN[0].strftime('%Y-%m-%d %H:%M:%S')

        # Logging dello stato e delle performance
        logging.info(f"{initial_date} --> {trade_date} --> {endDate}: {profitNotReinvested} USD  |   {profitNotReinvestedPerc} %")
        print(f"{initial_date} --> {trade_date} --> {endDate}: {profitNotReinvested} USD  |   {profitNotReinvestedPerc} %")
        # Cambia stato a SALE
        stateAgent = agentState.AgentState.SALE


        # Ritorna la percentuale di profitto non reinvestito
        return trade_date, stateAgent



"""
