# import MetaTrader5 as mt5
import sys

#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

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


from pathlib import Path

# Trova dinamicamente la cartella Trading-Agent e la aggiunge al path
current_path = Path(__file__).resolve()
while current_path.name != 'Trading-Agent':
    if current_path == current_path.parent:  # Se raggiungiamo la root senza trovare Trading-Agent
        raise RuntimeError("Errore: Impossibile trovare la cartella Trading-Agent!")
    current_path = current_path.parent

# Aggiunge la root al sys.path solo se non è già presente
if str(current_path) not in sys.path:
    sys.path.append(str(current_path))

from config import get_path_specify, market_data_path

# Ora possiamo importare `config`
get_path_specify(["db", "symbols", "workHistorical", "utils"])

# Importa i moduli personalizzati
from db import insertDataDB, connectDB
from symbols import getSymbols
import agentState
from utils import getLastIdTest, clearSomeTablesDB



# Funzione per aggiungere 2 anni a una data
def add_two_years(date):
    if isinstance(date, str):
        # Se la data è una stringa, convertila in datetime
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return date.replace(year=date.year + 2)



# Funzione principale per il trading e il caricamento
def main(datesToTrade):
    
    datesToTrade1 = [(start, dt, add_two_years(end)) for start, dt, end in datesToTrade]

    # Configurazione del logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        # Inserimento dati del login
        # insertDataDB.insertInLoginDate("Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn)

        profitsPerc = []
        profTot = []
        middleSale = []
        middlePurchase = []
        MmiddleTimeSale = []
        middletitleBetterProfit = []
        middletitleWorseProfit = []

        list_take_profit = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]

        #list_take_profit = [ 1.00]

        # datesToTrade = generateiRandomDates(cur, 100)

        # Inizio elaborazione per i diversi mercati
        market = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']
        for m in market:
            idTest = getLastIdTest(cur)
            insertDataDB.insertInMiddleProfit(idTest, "------", roi=0, devstandard=0, var=0, middleProfitUSD=0, middleSale=0, middlePurchase=0, middleTimeSale=0,  middletitleBetterProfit='----', middletitleWorseProfit=0, notes='---', cur=cur, conn=conn)
            
            if m == 'nasdaq_actions':
                # Recupero i simboli azionari del Nasdaq, in teoria dovrei lavorare con 100 simboli, ma nella funzione tradingYear_purchase_one_after_the_other vado a recupare i 100 simboli disponibili per cap descrescente.
                symbols = getSymbols.getSymbolsNasdaq(350)
            elif m == 'nyse_actions':
                symbols = getSymbols.getSymbolsNyse(350)
            elif m == 'larg_comp_eu_actions':
                symbols = getSymbols.getSymbolsLargestCompEU(350)

            for i in range(len(list_take_profit)):  # Per ogni valore di Take Profit (1%-10%)
                profitsPerc = []
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
                    # Logica principale
                    clearSomeTablesDB(cur, conn)
                    trade_date, initial_date, endDate = datesToTrade1[step]
                    profitPerc, profitUSD, nSale, nPurchase, middleTimeSale, titleBetterProfit, titleWorseProfit = tradingYear_purchase_one_after_the_other( cur, conn, symbols, trade_date, m, TK, initial_date, endDate)

                    # profitNotReinvestedPerc, profitNotReinvested, ticketSale, ticketPur, float(np.mean( # middleTimeSale)), max(titleProfit[symbol]), min(titleProfit[symbol])

                    print( f"\nProfitto per il test {idTest} con TP={TK}%, {m}, buy one after the other: {profitPerc}, rimangono {total_steps - step - 1} iterazioni\n")

                    profitPerc = round(profitPerc, 4)
                    insertDataDB.insertInTesting(idTest, "agent7", step, initial_date=initial_date, end_date=endDate, profitPerc=profitPerc, profitUSD=profitUSD, market=m, nPurchase=nPurchase, nSale=nSale, middleTimeSaleSecond=middleTimeSale,
                                                 middleTimeSaleDay=(middleTimeSale / 86400), titleBetterProfit=titleBetterProfit, titleWorseProfit=titleWorseProfit, notes=f"TAKE PROFIT = {TK}% ", cur=cur, conn=conn)

                    profTot.append(profitUSD)
                    profitsPerc.append(profitPerc)
                    middleSale.append(nSale)
                    middlePurchase.append(nPurchase)
                    MmiddleTimeSale.append(middleTimeSale)
                    middletitleBetterProfit.append(titleBetterProfit)
                    middletitleWorseProfit.append(titleWorseProfit)

                # Calcolo delle statistiche
                mean_profit_perc = round(float(np.mean(profitsPerc)), 4)
                std_deviation = round(float(np.std(profitsPerc)), 4)
                varianza = round(float(np.var(profitsPerc)), 4)
                mean_profit_usd = round(float(np.mean(profTot)), 4)
                mean_sale = round(float(np.mean(middleSale)), 4)
                mean_purchase = round(float(np.mean(middlePurchase)), 4)
                mean_time_sale = round(float(np.mean(MmiddleTimeSale)), 4)

                dizBetterTitle = {}
                for title in middletitleBetterProfit:
                    if title != '':
                        if title in dizBetterTitle:
                            dizBetterTitle[title] += 1
                        else:
                            dizBetterTitle[title] = 1

                dizWorseTitle = {}
                for title in middletitleWorseProfit:
                    if title != '':
                        if title in dizWorseTitle:
                            dizWorseTitle[title] += 1
                        else:
                            dizWorseTitle[title] = 1

                mean_titleBetterProfit = max(dizBetterTitle, key=dizBetterTitle.get)
                mean_titleWorseProfit = max(dizWorseTitle, key=dizWorseTitle.get)

                # logging.info(f"Profitto medio: {mean_profit}, Deviazione standard: {std_deviation}")

                notes = f"TP:{TK}%, {m}, buy no randomly but one after the other in a larger time window and gets 100 symbols by market capitalization order by date for which i purchase." 
                insertDataDB.insertInMiddleProfit(idTest, "agent7", roi=mean_profit_perc, devstandard=std_deviation, var=varianza, middleProfitUSD=mean_profit_usd, middleSale=mean_sale, middlePurchase=mean_purchase,
                                                  middleTimeSale=(mean_time_sale / 86400), middletitleBetterProfit=mean_titleBetterProfit, middletitleWorseProfit=mean_titleWorseProfit, notes=notes, cur=cur, conn=conn)

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
        cur.close()
        conn.close()
        #logging.shutdown()


################################################################################

# Recupero dei simboli azionari disponibili per le date di trading scelte.
def getSymbolsDispoible(cur, market, initial_date, endDate):
    try:
        # Recupero dei simboli azionari disponibili per le date di trading scelte. 
        cur.execute(f"SELECT distinct(symbol) FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
        symbolDisp = [sy[0] for sy in cur.fetchall()]
        #symb100 = symbols[0:100]
                
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return symbolDisp
    
    
    
################################################################################

# Recupero dei simboli azionari a maggior capitalizzazione per le date di trading scelte.
def getXSymbolsOrderedByMarketCap(symbolDisp, market, trade_data, x):
    try:
        # Recupero dei simboli azionari disponibili per le date di trading scelte in "symbolDisp"
        #cur.execute(f"SELECT distinct(symbol) FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
        #symbolDisp = [sy[0] for sy in cur.fetchall()]
        
        # extract the year for which we are starting trading
        year = str(trade_data).split('-')[0]
        
        if market == 'nasdaq_actions':
            strMark = 'NASDAQ'
        elif market == 'nyse_actions':
            strMark = 'NYSE'
        elif market == 'larg_comp_eu_actions':
            strMark = 'LARG_COMP_EU'
        
        # get the top x market cap stocks
        fileMarkCap = f'{market_data_path}/csv_files/marketCap/{strMark}/topVal{year}.csv'
        with open(fileMarkCap, mode='r') as file:
            symbXSelect = []
            for row in file:
                date, symbols = row.split(',')
                if date[0:-6] == trade_data: #datetime.strftime(initial_date, '%Y-%m-%d %H:%M:%S'):
                    symbXSelect = symbols.split(';')
                    symbXSelect = symbXSelect[0:x]
                    break
                
        finalSymbXSelect = []        
        for symb in symbXSelect:
            if symb.replace(' ', '') in symbolDisp:
                finalSymbXSelect.append(symb.replace(' ', ''))
            
        
    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return finalSymbXSelect



################################################################################


# Recupero dei 100 simboli azionari disponibili per le date di trading scelte, che sono i 100 titoli azionari a maggior capitalizzazione al momento della data di inizio di trading.
def selectSymbol(market, trade_date, symbolDisp ):
        # dizionario utilizzato per selezionare i titoli a maggior capitalizzazione attuali alla data di inizio di trading per il test
        selectors = {}
        
        # lista dei simboli azionari selezionati alla fine
        symbfinal = []
        
        # recupero dell'anno per il quale si sta iniziando trading
        year = str(trade_date).split('-')[0]
        
        # ottenere i titoli a maggior capitalizzazione
        if market == 'nasdaq_actions':
            # recupero dei dati relativi alla capitalizzazione di mercato dei titoli azionari del NASDAQ
            with open(f'{market_data_path}/csv_files/marketCap/NASDAQ/{year}.csv', mode='r') as file:
                for row in file:
                    # recupero del simbolo azionario, della data e della capitalizzazione di mercato per ogni riga del file
                    symb, date, cap = row.split(',')
                    
                    # se la data è uguale alla data trading attuale allora si aggiunge la capitalizzazione di mercato del titolo azionario al dizionario selectors
                    if date[0:-6] == trade_date :
                        if symb in selectors.keys():
                            selectors[symb] += [float(cap.replace('\n', ''))]
                        else:
                            selectors[symb] = [float(cap.replace('\n', ''))]
                            
            # ordinamento del dizionario selectors in ordine alfabetico per il simbolo azionario: calcolo per controllo della correzione degli ordinamenti.            
            selectors = dict(sorted(selectors.items()))
            
            # ordinamento del dizionario selectors in ordine decrescente di capitalizzazione di mercato
            symbSelect = sorted(selectors, key=lambda x: selectors[x], reverse=True)
            
            # selezione dei primi 100 titoli azionari a maggior capitalizzazione
            symbSelect100 = symbSelect[0:100]
         
        # stesso procedimento per gli altri mercati:               
        if market == 'nyse_actions':
            with open(f'{market_data_path}/csv_files/marketCap/NYSE/{year}.csv', mode='r') as file:
                for row in file:
                    symb, date, cap = row.split(',')
                    if date[0:-6] == trade_date :
                        if symb in selectors.keys():
                            selectors[symb] += [float(cap.replace('\n', ''))]
                        else:
                            selectors[symb] = [float(cap.replace('\n', ''))]
            symbSelect = sorted(selectors, key=lambda x: selectors[x], reverse=True)
            symbSelect100 = symbSelect[0:100]
            
        if market == 'larg_comp_eu_actions':
            with open(f'{market_data_path}/csv_files/marketCap/LARG_COMP_EU/{year}.csv', mode='r') as file:
                for row in file:
                    symb, date, cap = row.split(',')
                    if date[0:-6] == trade_date :
                        if symb in selectors.keys():
                            selectors[symb] += [float(cap.replace('\n', ''))]
                        else:
                            selectors[symb] = [float(cap.replace('\n', ''))]
            symbSelect = sorted(selectors, key=lambda x: selectors[x], reverse=True)
            symbSelect100 = symbSelect[0:100]
            symbSelect100 = [sy.split('.')[0] for sy in symbSelect100]
        
        # per ogni simbolo disponibile per le date di trading scelte, se il simbolo è tra i 100 titoli azionari a maggior capitalizzazione allora si aggiunge alla lista symbifinal 
        for sy in symbSelect100:
            symbfinal = [sy for sy in symbolDisp]
        
        return symbfinal


################################################################################

# Recupero dei prezzi dei simboli azionari per le date di trading scelte
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


################################################################################

def tradingYear_purchase_one_after_the_other(cur, conn, symbols, trade_date, market, TP, initial_date, endDate):
    # Inizializzazione a ogni iterazione
    budget = budgetInvestimenti = initial_budget = 1000
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = ticketPur = ticketSale = budgetMantenimento = nSaleProfit = 0 # equity = margin = 0 
    i = 0  # utilizzata per la scelta del titolo azionario da acquistare
    middleTimeSale = []
    titleProfit = {}
    sales = set()
    purchases = set()

    # Inserimento dei dati iniziali dell'agente nel database ---> insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

    stateAgent = agentState.AgentState.SALE

    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    symbolDisp1 = getSymbolsDispoible(cur, market, initial_date, endDate)
    
    # logging.info(f"Simboli azionari disponibili per il trading: {symbolDisp}\n")

    # Ottimizzazione 4: Recupera TUTTI i prezzi dei simboli disponibili per il periodo in una sola query
    prices_dict = getPrices(cur, market, initial_date, endDate)

    # Ottengo tutte le date per l'iterazione:
    cur.execute(f"SELECT distinct time_value_it FROM {market} WHERE time_value_it > '{initial_date}' and time_value_it < '{endDate}' order by time_value_it;")
    datesTrade = cur.fetchall()

    i_for_date = 0

    # Il ciclo principale esegue le operazioni di trading per 1 anno
    while True:

        ######################## inizio SALE
        if stateAgent == agentState.AgentState.SALE or stateAgent == agentState.AgentState.SALE_IMMEDIATE:    # logging.info(f"Agent entrato nello stato Sale\n")

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
                    if price_current > price_open:  # logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n" )

                        # Calcolo del profitto:
                        profit = price_current - price_open
                        perc_profit = profit / price_open

                        # Rivendita con l'1 % di profitto
                        if perc_profit > TP:

                            # aggiorno il budget
                            budgetInvestimenti = budgetInvestimenti + (price_open * volume)

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            profit_10Perc = (profit * 10) / 100
                            profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + (profit_10Perc * volume)
                            budgetMantenimento = budgetMantenimento + (profit_90Perc * volume)

                            ticketSale += 1
                            nSaleProfit += 1

                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

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
                            profitTotalPerc = (profitTotalUSD / initial_budget) * 100

                            # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                            profitNotReinvested = budgetMantenimento
                            profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100

                            # Aggiornamento dello stato dell'agent nel database
                            # insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                            # logging.info( f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current}, prezzo di acquisto: {price_open}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")

            price_open = -1
            price_current = -1

            if stateAgent == agentState.AgentState.SALE:
                stateAgent = agentState.AgentState.PURCHASE  # logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")

            if stateAgent == agentState.AgentState.SALE_IMMEDIATE:
                stateAgent = agentState.AgentState.WAIT  # logging.info(f"Cambio di stato da SALE IMMEDIATE a WAIT\n\n")

        ######################## fine SALE

        ######################## inizio PURCHASE
        if stateAgent == agentState.AgentState.PURCHASE:  # logging.info(f"Agent entrato nello stato Purchase\n")
            
            # dato che i 100 simboli a maggior capitalizzazione vengono scelti ad ogni iterazione (data di trading), si selezionano i 100 simboli azionari (a maggior cap) disponibili per la data di trading attuale
            #symbolDispTod = selectSymbol(market, trade_date, symbolDisp1)
            symbolDispTod = getXSymbolsOrderedByMarketCap(symbolDisp1, market, trade_date, 100)
            
            numb_purch = 0
            #i = 0
            
            giro = 0
            # Acquisto di azioni in modo iterativo dal pool di titoli azionari finché c'è budget
            while budgetInvestimenti > 0:

                # Se sono stati visti tutti i titoli azionari e c'è ancora budget per acquistare si ricomincia da capo
                if giro == len(symbolDispTod):
                    if numb_purch == 0:
                        break
                
                if i == len(symbolDispTod):   
                    i = 0

                chosen_symbol = symbolDispTod[i]

                i += 1
                giro += 1

                # Recupero del prezzo di apertura del simbolo azionario scelto
                price_data = prices_dict.get((chosen_symbol, trade_date))
                if price_data == None:
                    continue

                if price_data:
                    price, _ = price_data

                    if price == None:  # logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                        continue

                    if price == 0:  # Se il prezzo è = 0, allora non si può acquistare
                        continue

                        # Verifica se il simbolo è in un settore accettato e se è presente tra tutti i settori nek database: ---> if chosen_symbol in sectorSymbols and sectorSymbols[chosen_symbol] in sectors:

                    # Calcolo volume e aggiornamento budget
                    # volumeAcq = float(math.floor(10 / price))
                    volumeAcq = float(10 / price)
                    if volumeAcq == 0:
                        continue
                    ticketPur += 1
                    dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento nel database
                    insertDataDB.insertInPurchase(trade_date, ticketPur, volumeAcq, chosen_symbol, price, cur, conn)
                    numb_purch += 1
                    budgetInvestimenti -= (price * volumeAcq)
                    
                    purchases.add((dateObject, ticketPur, volumeAcq, chosen_symbol, price))

                    # Aggiornamento stato
                    # insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                    # Logging dell'acquisto
                    # if logging.getLogger().isEnabledFor(logging.INFO):
                    # logging.info(f"Acquistata azione {chosen_symbol} in data: {trade_date}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")

                    # else:
                    #    if logging.getLogger().isEnabledFor(logging.INFO):
                    #        logging.info(f"Settore di appartenenza per {chosen_symbol} non valido o non trovato.")

            # Dopo lo stato di acquisto il programma entra nello stato di attesa
            stateAgent = agentState.AgentState.SALE_IMMEDIATE  # logging.info(f"Cambio di stato da PURCHASE a SALE IMMEDIATE\n\n")

        ######################## fine PURCHASE

        #####################

        ######################## inizio WAIT
        if stateAgent == agentState.AgentState.WAIT:  # logging.info(f"Agent entrato nello stato Wait\n")

            # Aggiornamento dello stato dell'agent nel database
            # insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

            i_for_date += 1
            if i_for_date < len(datesTrade):
                trade_date = datesTrade[i_for_date]
                trade_date = str(trade_date[0])

            if i_for_date >= len(datesTrade):

                # Recupera tutti valori delle colonne degli acquisti nel db.
                #cur.execute("SELECT * FROM purchase order by now;")
                #purchasesDB = cur.fetchall()

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
                                insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol,
                                                          price_current, price_open, profit, perc_profit, cur, conn)

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
                                insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol,
                                                          price_current, price_open, 0, 0, cur, conn)

                                sales.add(ticketP)

                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                break

            # logging.info(f"Cambio di stato da WAIT a SALE\n\n")
            # logging.info(f"{initial_date} --> {trade_date} --> {endDate}: profUSD: {profitTotalUSD} | profPerc:{profitTotalPerc}")
            logging.info(
                f"{initial_date} --> {trade_date} --> {endDate}:   {round(profitNotReinvested, 4)} USD  |   {round(profitNotReinvestedPerc, 4)} %")

            stateAgent = agentState.AgentState.SALE

        ######################## fine WAIT

    purForLog = ''     
    for k, v in titleProfit.items():
        #titleProfit[k] = round
        purForLog += f'{k}: {len(v)}, '
    logging.info(f"Numero acquisti: {len(purchases)}, acquisti: {purForLog}")
    
    # return profitTotalPerc
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
            
    profitNotReinvestedPerc = ((profitNotReinvested - initial_budget) / initial_budget )


    if middleTimeSale == []:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, 0, maxT, minT

    else:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, float(
            np.mean(middleTimeSale)), maxT, minT


if __name__ == "__main__":
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    #datesToTrade = generateiRandomDates(cur, 100)

    cur.close()
    conn.close()

    #main(datesToTrade)
