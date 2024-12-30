# import MetaTrader5 as mt5
import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

import agentState
from db import insertDataDB, connectDB
from symbols import getSector, getSymbols
from utils import generateiRandomDates, getLastIdTest, clearSomeTablesDB, getSymbols50PercSect
import psycopg2
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
import numpy as np
import time


# In questo agente andiamo ad investire sul 50% dei titoli a maggiore capitalizzazione per ogni settore del mercato corrispondente.


# Funzione principale per il trading e il caricamento
def main(datesToTrade, dizNasdaq, dizNyse, perc):
    # Configurazione del logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        # Inserimento dati del login
        #insertDataDB.insertInLoginDate("Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn)
        
        roi = []
        profTot = []
        middleSale = []
        middlePurchase= []
        MmiddleTimeSale = []
        middletitleBetterProfit = []
        middletitleWorseProfit = []
        
        list_take_profit = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

        #list_take_profit = [1.00]
        #datesToTrade = generateiRandomDates(cur, 100)

        # Inizio elaborazione per i diversi mercati
        market = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']
        for m in market:
            if m == 'nasdaq_actions':
                symbols = getSymbols50PercSect(dizNasdaq, perc)
            elif m == 'nyse_actions':
                symbols = getSymbols50PercSect(dizNyse, perc)
            elif m == 'larg_comp_eu_actions':
                symbols = getSymbols.getSymbolsLargestCompEU(100)
            
            for i in range(len(list_take_profit)):  # Per ogni valore di Take Profit (1%-10%)
                roi = []
                profTot = []
                middleSale = []
                middlePurchase= []
                MmiddleTimeSale = []
                middletitleBetterProfit = []
                middletitleWorseProfit = []
                
                
                TK = list_take_profit[i]
                idTest = getLastIdTest(cur)
                                
                total_steps = 100   # Numero di iterazioni principali
                for step in range(total_steps):
                    # Logica principale
                    clearSomeTablesDB(cur, conn)
                    trade_date, initial_date, endDate = datesToTrade[step]
                    profitPerc, profitUSD, nSale, nPurchase, middleTimeSale, titleBetterProfit, titleWorseProfit = tradingYear_purchase_one_after_the_other(cur, conn, symbols, trade_date, m, TK, initial_date, endDate)
                    
                    # profitNotReinvestedPerc, profitNotReinvested, ticketSale, ticketPur, float(np.mean(middleTimeSale)), max(titleProfit[symbol]), min(titleProfit[symbol])
                    
                    print(f"\nProfitto per il test {idTest} con TP={TK}%, {m}, buy one after the other: {profitPerc}, rimangono {total_steps - step -1} iterazioni\n")
                    
                    profitPerc = round(profitPerc, 4)
                    insertDataDB.insertInTesting( idTest, "agent6", step, initial_date=initial_date, end_date=endDate, profitPerc=profitPerc, profitUSD =profitUSD,
                                                 market=m, nPurchase=nPurchase, nSale=nSale, middleTimeSaleSecond=middleTimeSale, middleTimeSaleDay=(middleTimeSale/86400),
                                                 titleBetterProfit=titleBetterProfit, titleWorseProfit=titleWorseProfit, notes=f"TAKE PROFIT = {TK}% ", cur=cur, conn=conn)
                    
                    profTot.append(profitUSD)
                    roi.append(profitPerc)
                    middleSale.append(nSale)
                    middlePurchase.append(nPurchase)
                    MmiddleTimeSale.append(middleTimeSale)
                    middletitleBetterProfit.append(titleBetterProfit)
                    middletitleWorseProfit.append(titleWorseProfit)
                

                # Calcolo delle statistiche
                mean_profit_perc = round(float(np.mean(roi)), 4)
                std_deviation = round(float(np.std(roi)), 4)
                varianza = round(float(np.var(roi)), 4)
                mean_profit_usd = round(float(np.mean(profTot)), 4)
                mean_sale = round(float(np.mean(middleSale)), 4)
                mean_purchase = round(float(np.mean(middlePurchase)), 4)
                mean_time_sale = round(float(np.mean(MmiddleTimeSale)), 4)
                
                dizBetterTitle = {}
                for title in middletitleBetterProfit:
                    if title in dizBetterTitle:
                        dizBetterTitle[title] += 1
                    else:
                        dizBetterTitle[title] = 1
                    
                dizWorseTitle = {}
                for title in middletitleWorseProfit:
                    if title in dizWorseTitle:
                        dizWorseTitle[title] += 1
                    else:
                        dizWorseTitle[title] = 1
                        
                mean_titleBetterProfit = max(dizBetterTitle, key=dizBetterTitle.get)
                mean_titleWorseProfit = max(dizWorseTitle, key=dizWorseTitle.get)
                
                #logging.info(f"Profitto medio: {mean_profit}, Deviazione standard: {std_deviation}")

                notes = f"TP:{TK}%, {m}, buy no randomly but one after the other with 50% of the symbols with better cap of the sector."
                insertDataDB.insertInMiddleProfit(idTest, "agent6", roi=mean_profit_perc, devstandard = std_deviation, var= varianza, middleProfitUSD =mean_profit_usd,
                                                  middleSale = mean_sale, middlePurchase = mean_purchase, middleTimeSale = (mean_time_sale/86400), middletitleBetterProfit = mean_titleBetterProfit,
                                                    middletitleWorseProfit = mean_titleWorseProfit, notes=notes, cur=cur, conn=conn)

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
        cur.close()
        conn.close()
        logging.shutdown()






def tradingYear_purchase_one_after_the_other(cur, conn, symbols, trade_date, market, TP, initial_date, endDate):    
    # Inizializzazione ad ogni iterazione
    budget = budgetInvestimenti = initial_budget = len(symbols) * 10
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = equity = margin = ticketPur = ticketSale = budgetMantenimento = nSaleProfit = 0
    i = 0   # utilizzata per la scelta del titolo azionario da acquistare
    middleTimeSale = []
    titleProfit = {}
 
    # Inserimento dei dati iniziali dell'agente nel database
    #insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                
    stateAgent = agentState.AgentState.SALE
            
    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    cur.execute(f"SELECT distinct(symbol) FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
    resSymbolDisp = cur.fetchall()
    #symbolDisp = [sy[0] for sy in resSymbolDisp if sy[0] in symbols]
    symbolDisp = [sy[0] for sy in resSymbolDisp if sy[0] in symbols]
    symbolDisp1 = symbolDisp.copy()
    #logging.info(f"Simboli azionari disponibili per il trading: {symbolDisp}\n")
    
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
                            nSaleProfit += 1
                            
                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                            #datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database                            
                            insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn)
                            
                            middleTimeSale.append((dateObject - datePur).total_seconds())
                            
                            if symbol in titleProfit:
                                titleProfit[symbol] += [perc_profit]
                            else:
                                titleProfit[symbol] = [perc_profit]
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                            profitTotalUSD += profit * volume
                            profitTotalPerc = (profitTotalUSD/initial_budget)*100
                            
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                            profitNotReinvested = budgetMantenimento
                            profitNotReinvestedPerc = (profitNotReinvested/initial_budget)*100
                            
                            # Aggiornamento dello stato dell'agent nel database
                            #insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                            
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
                      
                    if i == len(symbolDisp1):
                        i = 0
                    
                    # Scelgo un'azione random dal pool di titoli azionari
                    #chosen_symbol = symbolDisp[random.randint(0, len(symbolDisp) - 1)]
                    chosen_symbol = symbolDisp1[i]
                    
                    i += 1
                    
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
                    #insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                            
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
                            nSaleProfit += 1
                            
                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                            #datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database                            
                            insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn)
                            
                            middleTimeSale.append((dateObject - datePur).total_seconds())
                            
                            if symbol in titleProfit:
                                titleProfit[symbol] += [perc_profit]
                            else:
                                titleProfit[symbol] = [perc_profit]
                            
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                            profitTotalUSD += profit * volume
                            profitTotalPerc = (profitTotalUSD/initial_budget)*100
                            
                            
                            # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                            profitNotReinvested = budgetMantenimento
                            profitNotReinvestedPerc = (profitNotReinvested/initial_budget)*100
                            
                            
                            # Aggiornamento dello stato dell'agent nel database
                            #insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                            
                            #logging.info( f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current}, prezzo di acquisto: {price_open}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

                price_open = -1
                price_current = -1
                                
                stateAgent = agentState.AgentState.WAIT  #logging.info(f"Cambio di stato da SALE IMMEDIATE a WAIT\n\n")
            
            ########################



            ######################## inizio WAIT
            if stateAgent == agentState.AgentState.WAIT:  #logging.info(f"Agent entrato nello stato Wait\n")
                
                # Aggiornamento dello stato dell'agent nel database
                #insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                #cur.execute(f"SELECT distinct(symbol), now FROM purchase WHERE datepur = '{trade_date}' order by now;")
                #p = {pu[0] for pu in cur.fetchall()}
                #logging.info(f"Simboli acquistati in data: {trade_date} sono: {p}")
                
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
                logging.info(f"{initial_date} --> {trade_date} --> {endDate}:   {round(profitNotReinvested, 4)} USD  |   {round(profitNotReinvestedPerc, 4)} %")
                
                stateAgent = agentState.AgentState.SALE

            ######################## fine WAIT
              
    #return profitTotalPerc
    maxT, minT = '', ''
    maxP, minP = 0, 1000000000
    for k, v in titleProfit.items():
        titleProfit[k] = float(np.mean(v))
        if titleProfit[k] > maxP:
            maxP = titleProfit[k]
            maxT = k
        if titleProfit[k] < minP:
            minP = titleProfit[k]
            minT = k
    
    return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, float(np.mean(middleTimeSale)), maxT, minT






if __name__ == "__main__":
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    datesToTrade = generateiRandomDates(cur, 100)
    
    """cur.execute(f"SELECT * FROM SectorNasdaq;")
    sectNasd = [sy[0] for sy in cur.fetchall()]
    
    cur.execute(f"SELECT * FROM SectorNyse;")
    sectNyse = [sy[0] for sy in cur.fetchall()]
    
    print(f"Choice from Sectors Nasdaq in 1-12: {sectNasd}")

    choises = input("Write numbers and enter to continue:  ")
    choises = choises.split(",")
    choises = [int(x) for x in choises]
    sectNasdchoice = [sectNasd[i - 1] for i in choises]
    print(sectNasdchoice)
    
    print(f"\nChoice from Sectors Nyse in 13-24: {sectNyse}")
    choises = input("Write numbers and enter to continue:   ")
    choises = choises.split(",")
    choises = [int(x) for x in choises]
    sectNysechoice = [sectNyse[i - 13] for i in choises]
    print(sectNysechoice)
    """
    
    
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
    
    
    
    
    cur.close()
    conn.close()

    main(datesToTrade, dizNasdaq, dizNyse, perc=0.5)


