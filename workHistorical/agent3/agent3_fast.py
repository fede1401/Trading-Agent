# import MetaTrader5 as mt5
import sys
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')
sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/workHistorical')


import agentState
from db import insertDataDB, connectDB
from utils import generateiRandomDates, getLastIdTest, clearSomeTablesDB, getValueMiddlePrice
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
import numpy as np


def main(datesToTrade):
    # configurazione del logging
    logging.basicConfig( level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s" )
    
    #logging.disable(logging.CRITICAL)
            
    try:
        cur, conn = connectDB.connect_nasdaq()                                                                  # connessione al database           
       
        #insertDataDB.insertInLoginDate("Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn )        # inserimento dei dati relativi al login nel database
        
        roi = []
        profTot = []
        middleSale = []
        middlePurchase= []
        MmiddleTimeSale = []
        middletitleBetterProfit = []
        middletitleWorseProfit = []                                                                                            # lista che conterrà i profitti relativi a tutte le iterazioni
        
        #datesToTrade = generateiRandomDates(cur, 100)                                                            # generazione di 100 date casuali per il trading

        list_take_profit = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

        market = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions'] 
        #market = ['larg_comp_eu_actions']
        
        # mercati su cui effettuare trading
        for m in market:
            idTest = getLastIdTest(cur)
            insertDataDB.insertInMiddleProfit(idTest, "------", roi=0, devstandard=0, var=0, middleProfitUSD=0,
                                              middleSale=0, middlePurchase=0, middleTimeSale=0,
                                              middletitleBetterProfit='----',
                                              middletitleWorseProfit=0, notes='---', cur=cur, conn=conn)
            if m == 'nasdaq_actions':
                # Recupero i simboli azionari del Nasdaq, in teoria dovrei lavorare con 100 simboli, ma nella
                # funzione tradingYear_purchase_one_after_the_other vado a recuperare i 100 simboli disponibili per cap
                # descrescente.
                symbols = getSymbols.getSymbolsNasdaq(350)
            elif m == 'nyse_actions':
                symbols = getSymbols.getSymbolsNyse(350)
            elif m == 'larg_comp_eu_actions':
                symbols = getSymbols.getSymbolsLargestCompEU(350)

            for i in range(len(list_take_profit)):  # Per ogni valore di Take Profit (1%-10%)
                roi = []
                profTot = []
                middleSale = []
                middlePurchase = []
                MmiddleTimeSale = []
                middletitleBetterProfit = []
                middletitleWorseProfit = []

                TK = list_take_profit[i]
                idTest = getLastIdTest(cur)

                total_steps = 100  # Numero di iterazioni principali
                for step in range(total_steps):

                    clearSomeTablesDB(cur, conn)
                    trade_date, initial_date, endDate = datesToTrade[step]
                    profitPerc, profitUSD, nSale, nPurchase, middleTimeSale, titleBetterProfit, titleWorseProfit = tradingYear(cur, conn, symbols, trade_date, m, TK, initial_date, endDate)

                        # profitNotReinvestedPerc, profitNotReinvested, ticketSale, ticketPur, float(np.mean(middleTimeSale)), max(titleProfit[symbol]), min(titleProfit[symbol])

                    print(f"\nProfitto per il test {idTest} con TP={TK}%, {m}, buy one after the other: {profitPerc}, rimangono {total_steps - step -1} iterazioni\n")

                    profitPerc = round(profitPerc, 4)
                    insertDataDB.insertInTesting(idTest, "agent3", i, initial_date=initial_date, end_date=endDate,
                                                 profitPerc=profitPerc, profitUSD=profitUSD,
                                                 market=m, nPurchase=nPurchase, nSale=nSale,
                                                 middleTimeSaleSecond=middleTimeSale,
                                                 middleTimeSaleDay=(middleTimeSale / 86400),
                                                 titleBetterProfit=titleBetterProfit, titleWorseProfit=titleWorseProfit,
                                                 notes=f"TAKE PROFIT = {TK}% ", cur=cur, conn=conn)

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

                notes = f"TP:{TK}%, {m}, buy no randomly but one after the other and buy only if the price is lower than the middle price"
                insertDataDB.insertInMiddleProfit(idTest, "agent3", roi=mean_profit_perc, devstandard=std_deviation,
                                                  var=varianza, middleProfitUSD =mean_profit_usd,
                                                  middleSale = mean_sale, middlePurchase=mean_purchase,
                                                  middleTimeSale = (mean_time_sale/86400), middletitleBetterProfit=mean_titleBetterProfit,
                                                  middletitleWorseProfit=mean_titleWorseProfit, notes=notes, cur=cur, conn=conn)

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
        cur.close()
        conn.close()
        logging.shutdown()


def getSymbolsDispoible(cur, symbols, market, initial_date, endDate):
    try:
        # Recupero dei simboli azionari disponibili per le date di trading scelte. 
        cur.execute(f"SELECT distinct(symbol) FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
        # symbolDisp = [sy[0] for sy in resSymbolDisp if sy[0] in symbols]
        symbolDisp = []
        for sy in cur.fetchall():
            if sy[0] in symbols:
                if len(symbolDisp) < 100:
                    if sy[0] in symbols[:100]:
                        symbolDisp.append(sy[0])
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return symbolDisp



def getPrices(cur, market, initial_date, endDate):
    try:
        cur.execute( f"SELECT symbol, time_value_it, open_price, high_price FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
        
        # Crea un dizionario per l'accesso rapido ai prezzi
        prices_dict = {}
        for symbol, time_value_it, open_price, high_price in cur.fetchall():
            prices_dict[(symbol, time_value_it.strftime('%Y-%m-%d %H:%M:%S'))] = (open_price, high_price)
    
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return prices_dict



def tradingYear(cur, conn, symbols, trade_date, market, TP, initial_date, endDate):
    
    # Inizializzazione a ogni iterazione
    budget = budgetInvestimenti = initial_budget = 1000
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = equity = margin = ticketPur = ticketSale = budgetMantenimento = nSaleProfit = 0
    i = 0   # utilizzata per la scelta del titolo azionario da acquistare
    middleTimeSale = []
    titleProfit = {}
    sales = set()
    purchases = set()

    # Inserimento dei dati iniziali dell'agente nel database --> insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento,budgetInvestimenti, cur, conn)
                
    stateAgent = agentState.AgentState.SALE
            
    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    symbolDisp = getSymbolsDispoible(cur, symbols, market, initial_date, endDate)
    symbolDisp1 = symbolDisp.copy()
    # logging.info(f"Simboli azionari disponibili per il trading: {symbolDisp}\n")

    # Ottimizzazione 4: Recupera TUTTI i prezzi dei simboli disponibili per il periodo in una sola query
    prices_dict = getPrices(cur, market, initial_date, endDate)

    # Ottengo tutte le date per l'iterazione:
    cur.execute(
        f"SELECT distinct time_value_it FROM {market} WHERE time_value_it > '{initial_date}' and time_value_it < '{endDate}' order by time_value_it;")
    datesTrade = cur.fetchall()

    i_for_date = 0
    
    
    # Il ciclo principale esegue le operazioni di trading per 1 anno
    while True:

            ######################## inizio SALE
            if stateAgent == agentState.AgentState.SALE or stateAgent == agentState.AgentState.SALE_IMMEDIATE: #logging.info(f"Agent entrato nello stato Sale\n")
                
                # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                for pur in purchases:
                    datePur, ticketP, volume, symbol, price_open = pur[0], pur[1], pur[2], pur[3], pur[4]
                    
                    # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                    if ticketP in sales:
                        continue

                    price_data = prices_dict.get((symbol, trade_date))
                    if price_data:
                        open_price_from_dict, price_current = price_data

                        if price_current == None:
                            continue

                        # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                        if price_current > price_open:   #logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n" )

                            # Calcolo del profitto:
                            profit = price_current - price_open
                            perc_profit = profit / price_open

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

                                sales.add(ticketP)

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

                                #logging.info( f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current},
                                # prezzo di acquisto: {price_open}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

                price_open = -1
                price_current = -1
                
                if stateAgent == agentState.AgentState.SALE:
                    stateAgent = agentState.AgentState.PURCHASE  # logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")

                if stateAgent == agentState.AgentState.SALE_IMMEDIATE:
                    stateAgent = agentState.AgentState.WAIT  # logging.info(f"Cambio di stato da SALE IMMEDIATE a WAIT\n\n")

            ######################## fine SALE

            
            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:   #logging.info(f"Agent entrato nello stato Purchase\n")
                
                j = 0      # indice utilizzato per passare alla giornata successiva se non si riesce a comprare nulla.
                numb_purch = 0
                i = 0

                # Acquisto di azioni in modo iterativo dal pool di titoli azionari finché c'è budget
                while budgetInvestimenti > 0:

                    if j == len(symbolDisp1):
                        break
                       
                    # Se sono stati visti tutti i titoli azionari e c'è ancora budget per acquistare si ricomincia da capo
                    if i == len(symbolDisp1):
                        if numb_purch == 0:
                            break
                        else:
                            i = 0

                    chosen_symbol = symbolDisp1[i]  #chosen_symbol = symbolDisp[random.randint(0, len(symbolDisp) - 1)]
                    
                    i += 1

                    price_data = prices_dict.get((chosen_symbol, trade_date))
                    if price_data:
                        price, _ = price_data

                        if price == None:  #logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                            j += 1
                            continue

                        #price = price[0]
                        if price == 0:  # Se il prezzo è = 0, allora non si può acquistare
                            j += 1
                            continue

                        # Verifica se il simbolo è in un settore accettato e se è presente tra tutti i settori nek database:
                        #if chosen_symbol in sectorSymbols and sectorSymbols[chosen_symbol] in sectors:

                        middlePrice = getValueMiddlePrice(chosen_symbol, market, trade_date, cur)

                        if price < middlePrice:

                            # Calcolo volume e aggiornamento budget
                            volumeAcq = float(10 / price)
                            if volumeAcq == 0:
                                continue
                            ticketPur += 1
                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento nel database
                            insertDataDB.insertInPurchase(trade_date, ticketPur, volumeAcq, chosen_symbol, price, cur, conn)
                            budgetInvestimenti -= (price * volumeAcq)
                            
                            purchases.add((dateObject, ticketPur, volumeAcq, chosen_symbol, price))

                            # Aggiornamento stato
                            #insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                                # Logging dell'acquisto
                                #if logging.getLogger().isEnabledFor(logging.INFO):
                                    #logging.info(f"Acquistata azione {chosen_symbol} in data: {trade_date}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")
                        else:
                            j += 1

                            continue

                        #else:
                        #    if logging.getLogger().isEnabledFor(logging.INFO):
                        #        logging.info(f"Settore di appartenenza per {chosen_symbol} non valido o non trovato.")


                # Dopo lo stato di acquisto il programma entra nello stato di attesa
                stateAgent = agentState.AgentState.SALE_IMMEDIATE

            ######################## fine PURCHASE

            ######################## inizio WAIT
            if stateAgent == agentState.AgentState.WAIT:  #logging.info(f"Agent entrato nello stato Wait\n")
                
                # Aggiornamento dello stato dell'agent nel database
                #insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                i_for_date += 1
                if i_for_date < len(datesTrade):
                    trade_date = datesTrade[i_for_date]
                    trade_date = str(trade_date[0])

                #if trade_date >= endDate:
                if i_for_date >= len(datesTrade):
                    # Recupera i ticker relativi agli acquisti già venduti nel db.
                    #cur.execute("SELECT ticket_pur FROM sale")
                    #sales = {int(sale[0]) for sale in cur.fetchall()}
  
                    # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                    for pur in purchases:
                        datePur, ticketP, volume, symbol, price_open = pur[0], pur[1], pur[2], pur[3], pur[4]
                        
                        # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                        if ticketP in sales:
                            continue
                        
                        # Recupero del prezzo più alto relativo alla giornata di trading del simbolo azionario
                        #cur.execute(f"SELECT high_price FROM {market} WHERE symbol = '{symbol}' AND time_value_it='{trade_date}';")
                        #result = cur.fetchone()

                        price_data = prices_dict.get((symbol, trade_date))
                        if price_data:
                            open_price_from_dict, price_current = price_data

                            if price_current == None:
                                continue
                        
                        #if result:
                            # Memorizzo il risultato relativo al prezzo più alto della giornata di trading
                        #    price_current = result[0]
                            
                            if price_current > price_open:   
                                # Calcolo del profitto:
                                profit = price_current - price_open
                                perc_profit = profit / price_open
                            
                                # Vendiamo per l'ultima volta e teniamo nel deposito.
                                budgetMantenimento = budgetMantenimento + (price_open * volume) + (profit * volume)
                                
                                ticketSale += 1
                            
                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale( dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn )

                                sales.add(ticketP)

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

                                sales.add(ticketP)

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

    if middleTimeSale == []:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, 0, maxT, minT

    else:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, float(
            np.mean(middleTimeSale)), maxT, minT




if __name__ == "__main__":
    #sectorSymbols, sectors = getSector.getSectorSymbols()

    #i = 1
    #for sec in sectors:
        #print(f"{i}: {sec}\n")
    #    i += 1

    #print( f"Scegli uno o più settori su cui applicare l'agente (indicando i numeri con virgole se più di uno):\n" )
    #choises = input("Scrivi i numeri: ")

    #choises = choises.split(",")
    #choises = [int(x) for x in choises]
    #print(choises)
    #choises = [1,2,3,4,5,6,7,8,9,10,11]

    #sectors = [sectors[i - 1] for i in choises]

    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    #datesToTrade = generateiRandomDates(cur, 100)
    
    cur.close()
    conn.close()

    #main(datesToTrade)


