# import MetaTrader5 as mt5
import sys

#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/db')
#sys.path.append('/Users/federico/Documents/Tesi informatica/programming/Trading-Agent/symbols')

import psycopg2
import logging
from datetime import datetime, time, timedelta
import time as time_module
import math
from dateutil.relativedelta import relativedelta
import pandas as pd
import traceback
import numpy as np
import time
import random
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

from config import get_path_specify, market_data_path, project_root

# Ora possiamo importare `config`
get_path_specify(["db", "symbols", "workHistorical", "utils"])

# Importa i moduli personalizzati
from db import insertDataDB, connectDB
from symbols import getSymbols
import agentState
from utils import getLastIdTest, clearSomeTablesDB


logger_agent8 = logging.getLogger('agent8')
logger_agent8.setLevel(logging.INFO)

# Evita di aggiungere più volte lo stesso handler
if not logger_agent8.handlers:
    # Crea un file handler che scrive in un file specifico
    file_handler = logging.FileHandler(f'{project_root}/logs/testAgent8.log')
    file_handler.setLevel(logging.INFO)

    # Definisci il formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Aggiungi il file handler al logger
    logger_agent8.addHandler(file_handler)

logger_agent8.propagate = False


"Simboli che presentano anomalie nei dati di mercato"
SYMB_NASD_ANOMALIE= [ 'IDEX', 'CYRX', 'QUBT', 'POCI', 'MULN', 'BTCS', 'HEPA', 'OLB', 'NITO', 'XELA', 'ABVC', 'GMGI', 
                      'CELZ', 'IMTX', 'AREC', 'MNMD', 'PRTG', 'CHRD', 'ACCD', 'SPI',  'PRTG', 'NCPL', 'BBLGW', 'COSM', 
                      'ATXG', 'SILO', 'KWE', 'TOP',  'TPST', 'NXTT', 'OCTO', 'EGRX', 'AAGR', 'MYNZ', 'IDEX', 'CSSE', 
                      'BFI', 'EFTR', 'DRUG', 'GROM', 'HPCO', 'NCNC', 'SMFL']

SYMB_NYSE_ANOMALIE = [ 'WT', 'EMP', 'IVT', 'EMP', 'AMPY', 'ARCH', 'ODV' ]

SYMB_LARGE_ANOMALIE = [ 'SNK', 'CBE', 'BST', 'BOL', 'GEA', 'NTG', 'MBK', 'MOL', 'MAN', '1913', 
                       'SBB-B', 'SES', 'DIA', 'H2O', 'EVO', 'LOCAL', 'ATO', 'FRAG', 'MYNZ' ]
    
SYMB_TOT_ANOMALIE = ['IDEX', 'CYRX', 'QUBT', 'POCI', 'MULN', 'BTCS', 'HEPA', 'OLB', 'NITO', 'XELA', 'ABVC', 'GMGI', 
                      'CELZ', 'IMTX', 'AREC', 'MNMD', 'PRTG', 'CHRD', 'ACCD', 'SPI',  'PRTG', 'NCPL', 'BBLGW', 'COSM', 
                      'ATXG', 'SILO', 'KWE', 'TOP',  'TPST', 'NXTT', 'OCTO', 'EGRX', 'AAGR', 'MYNZ', 'IDEX', 'CSSE', 
                      'BFI', 'EFTR', 'DRUG', 'GROM', 'HPCO', 'NCNC', 'SMFL', 'WT', 'EMP', 'IVT', 'EMP', 'AMPY', 'ARCH', 'ODV',
                      'SNK', 'CBE', 'BST', 'BOL', 'GEA', 'NTG', 'MBK', 'MOL', 'MAN', '1913', 
                       'SBB-B', 'SES', 'DIA', 'H2O', 'EVO', 'LOCAL', 'ATO', 'FRAG', 'MYNZ' ]

"""
Agente che sfrutta la strategia del TSL: trailing stop loss.
Questa strategia si basa sulla vendita di un titolo azionario quando il suo prezzo scende sotto una certa soglia.
L'obiettivo è ottenere un profitto, tenendo salva una percentuale di profitto che il titolo ha già guadagnato.

La strategia si basa su 2 parametri fondamentali:
- alpha: indica la soglia per cui attivare la strategia del TSL. Se il profitto del titolo azionario supera alpha, allora si attiva la strategia del TSL.
- beta: indica la percentuale per cui il prezzo del titolo azionario deve scendere rispetto al prezzo massimo raggiunto dopo l'attivazione della strategia del TSL per la vendita.


Esempio:
Supponiamo di acquistare un titolo ad un prezzo di 100 USD.
Inizialmente aspettiamo che il titolo sali di una certa soglia alpha, ad esempio 15%.
Quindi, quando il prezzo raggiunge un prezzo di 115 USD si attiva la strategia.

Ci salviamo e teniamo da parte:
- il prezzo attuale per cui è partita la strategia: x(0)
e calcoliamo:
- la soglia y(0) = (1-beta) * x(0) : ad esempio se beta = 0,05 allora y(0) = 0,95 * 115 = 109,25 USD   

A questo punto ogni giorno di trading si calcola la soglia y:
y ( t + 1 ) = max( y(t), y(t) + ( x(t + 1) - x(t) ) ) ---> dove y(t) rappresenta il valore di y al giorno t e x(t) il valore di x al giorno t (prezzo al giorno t).
Nel calcolo, se il risultato cresce, signifca che il prezzo del titolo azionario sta salendo, quindi la soglia y cresce. Altrimente se il risultato è negativo, significa che il prezzo del titolo azionario sta scendendo, 
quindi la soglia y rimane invariata.

Se il prezzo corrente, cioè il prezzo al giorno t, scende sotto la soglia y, allora si vende il titolo azionario. 
In questo caso si salva una parte di profitti. Ad esempio, se il prezzo corrente è 108 USD e la soglia y è 109,25 USD, allora si vende il titolo azionario e si salva una parte di profitto.

Esempio:
- acquisto titolo a 100 USD
- alpha = 0,15
- beta = 0,05
- prezzo raggiunge 115 USD
- attivazione strategia TSL
- y = 109,25 USD
- x = 115 USD

- prezzo sale a 125 USD
- y = max(109,25, 109,25 + (125 - 115)) = max(109,25, 109,25 + 10) = 109,25 + 10 = 119,25
- x = 125 USD
- prezzo 125 USD > y = 119,25 USD, quindi non si vende il titolo azionario


- prezzo scende a 108 USD
- y = max(119,25, 119,25 + (108 - 125)) = max(119,25, 102,25) = 119,25
- x = 108 USD
- prezzo scende sotto y, quindi si vende il titolo azionario e si salva una parte di profitto


Infine, comprendiamo che:
- alpha deve essere abbastanza alto per garantire un profitto soddisfacente.

Se beta viene impostato ad un valore alto come 0,2, allora :
    - il prezzo del titolo azionario deve scendere del 20% rispetto al prezzo massimo raggiunto dopo l'attivazione della strategia del TSL per la vendita.
    Quindi, y iniziale sarebbe stato = (1 - 0,2) * 115 = 92 USD e il prezzo del titolo azionario deve scendere sotto 92 USD per vendere il titolo azionario, 
    quindi non è molto conveniente perchè si rischia di perdere troppo.
    
Se beta viene impostato ad un valore basso come 0,025, allora:
    - il prezzo del titolo azionario deve scendere del 2,5% rispetto al prezzo massimo raggiunto dopo l'attivazione della strategia del TSL per la vendita.
    Quindi, y iniziale sarebbe stato = (1 - 0,025) * 115 = 112,125 USD e il prezzo del titolo azionario deve scendere sotto 112,125 USD per vendere il titolo azionario,
    quindi è molto conveniente perchè si rischia di perdere poco.

"""


# Funzione principale per il trading e il caricamento
def main(datesToTrade, dizMarkCap, symbolsDispoInDatesNasd, symbolsDispoInDatesNyse, symbolsDispoInDatesLarge, pricesDispoInDatesNasd, pricesDispoInDatesNyse, pricesDispoInDatesLarge, totaledates):
    # Configurazione del logging
    #logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    #logging.basicConfig(filename=f'{project_root}/logs/testAgent8.log', level=logging.INFO,  format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        logger_agent8.info(f"Start agent8_selectRandom: {datetime.now()} \n")
        
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

        #list_take_profit = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]  #list_take_profit = [ 0.50 ]
        alpha_parameters = [0.05, 0.1, 0.15, 0.2]
        beta_parameters = [0.025, 0.05, 0.1, 0.15, 0.2]

        # Inizio elaborazione per i diversi mercati
        market = ['nasdaq_actions', 'nyse_actions', 'larg_comp_eu_actions']  #market = ['larg_comp_eu_actions']
        
        for m in market:
            logger_agent8.info(f"\n\nWork with market {m} : {datetime.now()}")
            idTest = getLastIdTest(cur)
            insertDataDB.insertInMiddleProfit(idTest, "------", roi=0, devstandard=0, var=0, middleProfitUSD=0, middleSale=0, middlePurchase=0, middleTimeSale=0,  middletitleBetterProfit='----', middletitleWorseProfit=0, notes='---', cur=cur, conn=conn)
            
            if m == 'nasdaq_actions':
                # Recupero i simboli azionari del Nasdaq, in teoria dovrei lavorare con 100 simboli, ma nella funzione tradingYear_purchase_one_after_the_other vado a recupare i 100 simboli disponibili per cap descrescente.
                symbols = getSymbols.getAllSymbolsNasdaq()
                symbolsDispoInDates = symbolsDispoInDatesNasd
                pricesDispoInDates = pricesDispoInDatesNasd
            elif m == 'nyse_actions':
                symbols = getSymbols.getAllSymbolsNyse()
                symbolsDispoInDates = symbolsDispoInDatesNyse
                pricesDispoInDates = pricesDispoInDatesNyse
            elif m == 'larg_comp_eu_actions':
                symbols = getSymbols.getAllSymbolsLargestCompEU()
                symbolsDispoInDates = symbolsDispoInDatesLarge
                pricesDispoInDates = pricesDispoInDatesLarge

            for alpha in alpha_parameters:
                for beta in beta_parameters:
                    profitsPerc = []
                    profTot = []
                    middleSale = []
                    middlePurchase = []
                    MmiddleTimeSale = []
                    middletitleBetterProfit = []
                    middletitleWorseProfit = []

                    #TK = list_take_profit[i]
                    #logging.info(f"Start simulation with {TK} agent2_markCapDayInitial : {datetime.now()}")
                    idTest = getLastIdTest(cur) 

                    total_steps = len(datesToTrade)  # 
                    for step in range(total_steps):
                        # Logica principale
                        clearSomeTablesDB(cur, conn)
                        trade_date, initial_date, endDate = datesToTrade[step]
                        logger_agent8.info(f"Start test with ALPHA:{alpha} and BETA:{beta}, agent8 in initial date {initial_date} : {datetime.now()}")
                        profitPerc, profitUSD, nSale, nPurchase, middleTimeSale, titleBetterProfit, titleWorseProfit = tradingYear_purchase_one_after_the_other( cur, conn, symbols, trade_date, m, alpha, beta, initial_date, endDate, dizMarkCap, symbolsDispoInDates, pricesDispoInDates, totaledates[m])

                        # profitNotReinvestedPerc, profitNotReinvested, ticketSale, ticketPur, float(np.mean( # middleTimeSale)), max(titleProfit[symbol]), min(titleProfit[symbol])
                        print( f"\nProfitto per il test {idTest} con ALPHA:{alpha} and BETA:{beta}, {m}, buy one after the other: {profitPerc}, rimangono {total_steps - step - 1} iterazioni\n")

                        profitPerc = round(profitPerc, 4)
                        insertDataDB.insertInTesting(idTest, "agent8", step, initial_date=initial_date, end_date=endDate, profitPerc=profitPerc, profitUSD=profitUSD, market=m, nPurchase=nPurchase, nSale=nSale, middleTimeSaleSecond=middleTimeSale,
                                                    middleTimeSaleDay=(middleTimeSale / 86400), titleBetterProfit=titleBetterProfit, titleWorseProfit=titleWorseProfit, notes=f"ALPHA:{alpha} and BETA:{beta}", cur=cur, conn=conn)

                        profTot.append(profitUSD)
                        profitsPerc.append(profitPerc)
                        middleSale.append(nSale)
                        middlePurchase.append(nPurchase)
                        MmiddleTimeSale.append(middleTimeSale)
                        middletitleBetterProfit.append(titleBetterProfit)
                        middletitleWorseProfit.append(titleWorseProfit)
                        logger_agent8.info(f"End test with ALPHA:{alpha} and BETA:{beta} agent8 select Random in initial date {initial_date} : {datetime.now()}\n\n")

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
                            if (title in dizBetterTitle):
                                dizBetterTitle[title] += 1
                            else:
                                dizBetterTitle[title] = 1

                    dizWorseTitle = {}
                    for title in middletitleWorseProfit:
                        if title != '':
                            if (title in dizWorseTitle):
                                dizWorseTitle[title] += 1
                            else:
                                dizWorseTitle[title] = 1

                    mean_titleBetterProfit = max(dizBetterTitle, key=dizBetterTitle.get)
                    mean_titleWorseProfit = max(dizWorseTitle, key=dizWorseTitle.get)

                    # logging.info(f"Profitto medio: {mean_profit}, Deviazione standard: {std_deviation}")
                    logger_agent8.info(f"End simulation with ALPHA:{alpha} and BETA:{beta} agent8 : {datetime.now()} \n\n\n\n")

                    notes = f"ALPHA:{alpha} and BETA:{beta}, {m}, agent8 that purchase and sale with TK and select symbol with select random of titles."
                    insertDataDB.insertInMiddleProfit(idTest, "agent8", roi=mean_profit_perc, devstandard=std_deviation, var=varianza, middleProfitUSD=mean_profit_usd, middleSale=mean_sale, middlePurchase=mean_purchase,
                                                    middleTimeSale=(mean_time_sale / 86400), middletitleBetterProfit=mean_titleBetterProfit, middletitleWorseProfit=mean_titleWorseProfit, notes=notes, cur=cur, conn=conn)

    except Exception as e:
        logger_agent8.critical(f"Errore non gestito: {e}")
        logger_agent8.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logger_agent8.info("Connessione chiusa e fine del trading agent.")
        cur.close()
        conn.close()
        #logging.shutdown()

################################################################################


# Recupero dei 100 simboli azionari a random disponibili per le date di trading scelte.
def getSymbolsDispoible(cur, symbols, market, initial_date, endDate, symbolsDispoInDates):
    try:
        # Recupero dei simboli azionari disponibili per le date di trading scelte in "symbolDisp"
        #cur.execute(f"SELECT distinct(symbol) FROM {market} WHERE time_value_it BETWEEN '{initial_date}' AND '{endDate}';")
        #symbolDisp = [sy[0] for sy in cur.fetchall()]
        
        valid_symbols = [s for s in symbolsDispoInDates[initial_date] if s not in SYMB_TOT_ANOMALIE]

        # Poi fai il sample dalla lista già filtrata:
        symbSelect100 = random.sample(valid_symbols, 100)
        
        # si seleziona randomicamente tra i simboli disponibili per le date di trading scelte, 100 simboli azionari:
        #symbSelect100 = random.sample(symbolsDispoInDates[initial_date], 100)
                
    except Exception as e:
        logger_agent8.critical(f"Errore non gestito: {e}")
        logger_agent8.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
    finally:
        return symbSelect100


################################################################################

# Recupero dei prezzi dei simboli azionari per le date di trading scelte
def getPrices(cur, market, initial_date, endDate, pricesDispoInDates):
    return (pricesDispoInDates[initial_date])[0]
    


################################################################################


def tradingYear_purchase_one_after_the_other(cur, conn, symbols, trade_date, market, alpha, beta, initial_date, endDate, dizMarkCap, symbolsDispoInDates, pricesDispoInDates, totaledates):
    # Inizializzazione a ogni iterazione
    budgetInvestimenti = initial_budget = 1000 # budget = 
    profitTotalUSD = profitTotalPerc = profitNotReinvested = profitNotReinvestedPerc = ticketPur = ticketSale = budgetMantenimento = nSaleProfit = 0 # equity = margin = 0 
    i = 0  # utilizzata per la scelta del titolo azionario da acquistare
    middleTimeSale = []
    titleProfit = {}
    sales = set()
    purchases = {}
    salesDict = {}

    # Inserimento dei dati iniziali dell'agente nel database ---> insertDataDB.insertInDataTrader(trade_date, agentState.AgentState.INITIAL, initial_budget, 1000, 0, 0, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

    stateAgent = agentState.AgentState.SALE

    # Recupero dei simboli azionari disponibili per le date di trading scelte. 
    symbolDisp1 = getSymbolsDispoible(cur, symbols, market, initial_date, endDate, symbolsDispoInDates)
    logger_agent8.info(f"Test with this symbols : {symbolDisp1}")


    # Ottimizzazione 4: Recupera TUTTI i prezzi dei simboli disponibili per il periodo in una sola query
    prices_dict = (pricesDispoInDates[initial_date])[0]

    # Recupero delle date di trading per l'anno corrente
    datesTrade = totaledates[initial_date.strftime('%Y-%m-%d %H:%M:%S')]

    i_for_date = 0

    # Il ciclo principale esegue le operazioni di trading per 1 anno
    while True:

        ######################## inizio SALE
        if stateAgent == agentState.AgentState.SALE or stateAgent == agentState.AgentState.SALE_IMMEDIATE:    # logging.info(f"Agent entrato nello stato Sale\n")

            # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
            for k,v in purchases.items():
            #for pur in purchases:
                ticketP = k
                datePur, volume, symbol, price_purch, tsl, y_i, x_i = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
                
                # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                if ticketP in sales:
                    continue

                price_data = prices_dict.get((symbol, trade_date))   # open | high price
                if price_data:
                    open_price_from_dict, price_current = price_data

                    if price_current == None:
                        continue
                    
                    if tsl:
                        # 2) Se TSL è attiva, aggiorno la soglia y_tsl e vedo se devo vendere.
                        # logging.info(f"Analizzo il simbolo {symbol} per la data {datePur} con prezzo corrente {price_current} e prezzo di acquisto {price_purch}")
                        y_tsl = max( y_i, (y_i + (price_current - x_i) ) )
                        
                        x_anchor = price_current
                        purchases[ticketP] = (datePur, volume, symbol, price_purch, tsl, y_tsl, x_anchor)
                        
                        if price_current <= y_tsl:
                            # Calcolo del profitto:
                            profit = price_current - price_purch
                            perc_profit = profit / price_purch
                            
                            # aggiorno il budget
                            budgetInvestimenti = budgetInvestimenti + (price_purch * volume)

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            #profit_10Perc = (profit * 10) / 100
                            #profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + (((profit * 10) / 100) * volume)
                            budgetMantenimento = budgetMantenimento + (((profit * 90) / 100) * volume)

                            ticketSale += 1
                            nSaleProfit += 1

                            dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                            insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol, price_current, price_purch, profit, perc_profit, cur, conn)

                            # Calcolo del tempo medio di vendita: cioè il tempo che intercorre tra l'acquisto e la vendita di un titolo azionario
                            middleTimeSale.append((dateObject - datePur).total_seconds())

                            sales.add(ticketP)

                            # Salvataggio del profitto per il titolo azionario creato per ottenere a fine test i titoli azionari con il profitto medio migliore e peggiore 
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
                            
                            salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_purch, profit, perc_profit)

                            # Aggiornamento dello stato dell'agent nel database
                            # insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                            # logging.info( f"Venduta azione {symbol} in data:{trade_date} comprata in data:{datePur}, prezzo attuale:{price_current}, prezzo di acquisto: {price_purch}, con profitto di: {profit} = {perc_profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")
                                                
                    else:
                        # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                        if price_current > price_purch:  # logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_purch}\n" )

                            # Calcolo del profitto:
                            profit = price_current - price_purch
                            perc_profit = profit / price_purch

                            # Se la percentuale di profitto supera il valore alpha, si attiva la TSL: trailing stop loss
                            if perc_profit > alpha:
                                
                                # Attivazione TSL
                                # calcolo soglia di attivazione TSL
                                x_initial = price_purch
                                y_initial = (1-beta) * price_current
                                
                                tsl = True
                                purchases[ticketP] = (datePur, volume, symbol, price_purch, tsl, y_initial, x_initial)
                                                            
            price_purch = -1
            price_current = -1

            if stateAgent == agentState.AgentState.SALE:
                stateAgent = agentState.AgentState.PURCHASE  # logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")

            if stateAgent == agentState.AgentState.SALE_IMMEDIATE:
                stateAgent = agentState.AgentState.WAIT  # logging.info(f"Cambio di stato da SALE IMMEDIATE a WAIT\n\n")

        ######################## fine SALE



        ######################## inizio PURCHASE
        if stateAgent == agentState.AgentState.PURCHASE:  # logging.info(f"Agent entrato nello stato Purchase\n")
            giro = 0
            #random.shuffle(symbolDisp1)

            numb_purch = 0
            #i = 0
            # Acquisto di azioni in modo iterativo dal pool di titoli azionari finché c'è budget
            while budgetInvestimenti > 0:

                # Se sono stati visti tutti i titoli azionari e non c'è nulla da acquistare allora si esce dal ciclo
                if giro == len(symbolDisp1):
                    if numb_purch == 0:
                        break
                
                # Se sono stati visti tutti i titoli azionari e c'è qualcosa da acquistare allora si ricomincia a vedere i titoli azionario dal primo
                if i == len(symbolDisp1):   
                    i = 0

                # Scelta del simbolo azionario da acquistare tra quelli disponibili
                chosen_symbol = symbolDisp1[i]

                # incremento variabili per il ciclo
                i += 1
                giro += 1

                # Recupero del prezzo di apertura e  del simbolo azionario scelto
                price_data = prices_dict.get((chosen_symbol, trade_date))   # price_data = [open , high price]
                if price_data == None:
                    continue

                if price_data:
                    price, _ = price_data  # price = price_data[0] : corrisponde al prezzo di apertura del simbolo azionario scelto

                    if price == None:  # logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                        continue

                    if price == 0:  # Se il prezzo è = 0, allora non si può acquistare
                        continue

                        # Verifica se il simbolo è in un settore accettato e se è presente tra tutti i settori nek database: ---> if chosen_symbol in sectorSymbols and sectorSymbols[chosen_symbol] in sectors:

                    # Calcolo volume e aggiornamento budget
                    volumeAcq = float(10 / price)  # volumeAcq = float(math.floor(10 / price))
                    if volumeAcq == 0:
                        continue
                    ticketPur += 1
                    dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento nel database
                    insertDataDB.insertInPurchase(trade_date, ticketPur, volumeAcq, chosen_symbol, price, cur, conn)
                    numb_purch += 1
                    budgetInvestimenti -= (price * volumeAcq)
                    
                    tsl = False
                    y_initial = 0
                    x_initial = 0
                    
                    purchases[ticketPur] = [dateObject, volumeAcq, chosen_symbol, price, tsl, y_initial, x_initial]

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



        ######################## inizio WAIT
        if stateAgent == agentState.AgentState.WAIT:  # logging.info(f"Agent entrato nello stato Wait\n")

            # Aggiornamento dello stato dell'agent nel database
            # insertDataDB.insertInDataTrader(trade_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

            i_for_date += 1
            if i_for_date < len(datesTrade):
                trade_date = datesTrade[i_for_date]
                #trade_date = str(trade_date[0])
                trade_date = trade_date.strftime('%Y-%m-%d %H:%M:%S')

            if i_for_date >= len(datesTrade):

                # Recupera tutti valori delle colonne degli acquisti nel db.
                #cur.execute("SELECT * FROM purchase order by now;")
                #purchasesDB = cur.fetchall()

                # Memorizzo le informazioni relative agli acquisti nelle variabili seguenti:
                for k,v in purchases.items():
                #for pur in purchases:
                    ticketP = k
                    datePur, volume, symbol, price_purch, tsl, y_initial, x_initial = v[0], v[1], v[2], v[3], v[4], v[5], v[6]

                    # Se il ticket di acquisto del simbolo: symbol è già stato venduto, allora non dobbiamo analizzarlo e si passa al prossimo acquisto.
                    if ticketP in sales:
                        continue

                    price_data = prices_dict.get((symbol, trade_date))
                    if price_data:
                        open_price_from_dict, price_current = price_data

                        if price_current == None:
                            continue

                        if price_current > price_purch:
                                # Calcolo del profitto:
                                profit = price_current - price_purch
                                perc_profit = profit / price_purch

                                # Vendiamo per l'ultima volta e teniamo nel deposito.
                                budgetMantenimento = budgetMantenimento + (price_purch * volume) + (profit * volume)

                                ticketSale += 1

                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol,
                                                          price_current, price_purch, profit, perc_profit, cur, conn)

                                sales.add(ticketP)

                                # Aggiornamento del valore dei profitti totali (comprensivi di anche i dollari che reinvesto)
                                profitTotalUSD += profit * volume
                                profitTotalPerc = (profitTotalUSD / initial_budget) * 100

                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                                
                                salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_purch, profit, perc_profit)

                        else:
                                # Non c'è profitto, vendiamo al prezzo corrente.
                                budgetMantenimento = budgetMantenimento + (price_current * volume)

                                ticketSale += 1

                                dateObject = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                                # datePur = datetime.strptime(datePur, '%Y-%m-%d %H:%M:%S')

                                # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                insertDataDB.insertInSale(dateObject, datePur, ticketP, ticketSale, volume, symbol,
                                                          price_current, price_purch, 0, 0, cur, conn)

                                sales.add(ticketP)

                                # Aggiornamento del valore dei profitti totali (comprensivi dei dollari che non reinvesto)
                                profitNotReinvested = budgetMantenimento
                                profitNotReinvestedPerc = (profitNotReinvested / initial_budget) * 100
                                
                                salesDict[ticketSale] = (dateObject, datePur, ticketP, volume, symbol, price_current, price_purch, profit, perc_profit)
                break

            # logging.info(f"Cambio di stato da WAIT a SALE\n\n")
            # logging.info(f"{initial_date} --> {trade_date} --> {endDate}: profUSD: {profitTotalUSD} | profPerc:{profitTotalPerc}")
            #logging.info(
            #    f"{initial_date} --> {trade_date} --> {endDate}:   {round(profitNotReinvested, 4)} USD  |   {round((((profitNotReinvested - initial_budget) / initial_budget ) * 100), 4)} %")

            stateAgent = agentState.AgentState.SALE

        ######################## fine WAIT

    purForLog = ''     
    for k, v in titleProfit.items():
        #titleProfit[k] = round
        purForLog += f'{k}: {len(v)}, '
    logger_agent8.info(f"Numero acquisti: {len(purchases)}, acquisti: {purForLog}")
    
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
        
    profitNotReinvestedPerc = ((profitNotReinvested - initial_budget) / initial_budget ) * 100

    logger_agent8.info(f"Profitto in percentuale : {profitNotReinvestedPerc} %")
    
    if profitNotReinvestedPerc > 250:
        for tick, infoS in salesDict.items():
            logger_agent8.info(f"{tick}: date sale: {infoS[1]}, data purchase: {infoS[0]}, ticketAcq: {infoS[2]}, volume: {infoS[3]}, simbolo: {infoS[4]}, prezzo corrente di vendita: {infoS[5]}, prezzo acquisto: {infoS[6]}, profitto: {infoS[7]}, profitto percentuale: {infoS[8]}")

    if middleTimeSale == []:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, 0, maxT, minT

    else:
        return profitNotReinvestedPerc, profitNotReinvested, nSaleProfit, ticketPur, float(
            np.mean(middleTimeSale)), maxT, minT


if __name__ == "__main__":
    # Connessione al database
    #cur, conn = connectDB.connect_nasdaq()
    #datesToTrade = generateiRandomDates(cur, 100)
    #datesToTrade1 = [('1999-06-24 00:00:00', datetime(1999, 6, 24, 0, 0), '2000-06-24 00:00:00'), ('1999-07-16 00:00:00', datetime(1999, 7, 16, 0, 0), '2000-07-16 00:00:00'), ('1999-09-08 00:00:00', datetime(1999, 9, 8, 0, 0), '2000-09-08 00:00:00'), ('2001-08-08 00:00:00', datetime(2001, 8, 8, 0, 0), '2002-08-08 00:00:00'), ('2001-09-24 00:00:00', datetime(2001, 9, 24, 0, 0), '2002-09-24 00:00:00'), ('2001-09-24 00:00:00', datetime(2001, 9, 24, 0, 0), '2002-09-24 00:00:00'), ('2002-11-01 00:00:00', datetime(2002, 11, 1, 0, 0), '2003-11-01 00:00:00'), ('2002-11-18 00:00:00', datetime(2002, 11, 18, 0, 0), '2003-11-18 00:00:00'), ('2004-01-09 00:00:00', datetime(2004, 1, 9, 0, 0), '2005-01-09 00:00:00'), ('2004-08-18 00:00:00', datetime(2004, 8, 18, 0, 0), '2005-08-18 00:00:00'), ('2006-11-02 00:00:00', datetime(2006, 11, 2, 0, 0), '2007-11-02 00:00:00'), ('2006-11-15 00:00:00', datetime(2006, 11, 15, 0, 0), '2007-11-15 00:00:00'), ('2007-10-22 00:00:00', datetime(2007, 10, 22, 0, 0), '2008-10-22 00:00:00'), ('2008-12-05 00:00:00', datetime(2008, 12, 5, 0, 0), '2009-12-05 00:00:00'), ('2009-04-16 00:00:00', datetime(2009, 4, 16, 0, 0), '2010-04-16 00:00:00'), ('2009-10-20 00:00:00', datetime(2009, 10, 20, 0, 0), '2010-10-20 00:00:00'), ('2009-11-23 00:00:00', datetime(2009, 11, 23, 0, 0), '2010-11-23 00:00:00'), ('2010-07-16 00:00:00', datetime(2010, 7, 16, 0, 0), '2011-07-16 00:00:00'), ('2011-06-09 00:00:00', datetime(2011, 6, 9, 0, 0), '2012-06-09 00:00:00'), ('2011-07-28 00:00:00', datetime(2011, 7, 28, 0, 0), '2012-07-28 00:00:00'), ('2011-09-20 00:00:00', datetime(2011, 9, 20, 0, 0), '2012-09-20 00:00:00'), ('2012-11-19 00:00:00', datetime(2012, 11, 19, 0, 0), '2013-11-19 00:00:00'), ('2012-12-20 00:00:00', datetime(2012, 12, 20, 0, 0), '2013-12-20 00:00:00'), ('2013-03-01 00:00:00', datetime(2013, 3, 1, 0, 0), '2014-03-01 00:00:00'), ('2013-06-28 00:00:00', datetime(2013, 6, 28, 0, 0), '2014-06-28 00:00:00'), ('2013-08-12 00:00:00', datetime(2013, 8, 12, 0, 0), '2014-08-12 00:00:00'), ('2014-01-13 00:00:00', datetime(2014, 1, 13, 0, 0), '2015-01-13 00:00:00'), ('2014-01-21 00:00:00', datetime(2014, 1, 21, 0, 0), '2015-01-21 00:00:00'), ('2014-01-30 00:00:00', datetime(2014, 1, 30, 0, 0), '2015-01-30 00:00:00'), ('2015-03-04 00:00:00', datetime(2015, 3, 4, 0, 0), '2016-03-04 00:00:00'), ('2015-03-13 00:00:00', datetime(2015, 3, 13, 0, 0), '2016-03-13 00:00:00'), ('2015-03-16 00:00:00', datetime(2015, 3, 16, 0, 0), '2016-03-16 00:00:00'), ('2015-03-26 00:00:00', datetime(2015, 3, 26, 0, 0), '2016-03-26 00:00:00'), ('2015-04-28 00:00:00', datetime(2015, 4, 28, 0, 0), '2016-04-28 00:00:00'), ('2015-05-14 00:00:00', datetime(2015, 5, 14, 0, 0), '2016-05-14 00:00:00'), ('2015-09-15 00:00:00', datetime(2015, 9, 15, 0, 0), '2016-09-15 00:00:00'), ('2016-02-23 00:00:00', datetime(2016, 2, 23, 0, 0), '2017-02-23 00:00:00'), ('2016-03-18 00:00:00', datetime(2016, 3, 18, 0, 0), '2017-03-18 00:00:00'), ('2016-04-06 00:00:00', datetime(2016, 4, 6, 0, 0), '2017-04-06 00:00:00'), ('2016-10-06 00:00:00', datetime(2016, 10, 6, 0, 0), '2017-10-06 00:00:00'), ('2017-02-15 00:00:00', datetime(2017, 2, 15, 0, 0), '2018-02-15 00:00:00'), ('2017-03-15 00:00:00', datetime(2017, 3, 15, 0, 0), '2018-03-15 00:00:00'), ('2017-05-01 00:00:00', datetime(2017, 5, 1, 0, 0), '2018-05-01 00:00:00'), ('2017-08-14 00:00:00', datetime(2017, 8, 14, 0, 0), '2018-08-14 00:00:00'), ('2017-08-15 00:00:00', datetime(2017, 8, 15, 0, 0), '2018-08-15 00:00:00'), ('2017-08-16 00:00:00', datetime(2017, 8, 16, 0, 0), '2018-08-16 00:00:00'), ('2017-10-30 00:00:00', datetime(2017, 10, 30, 0, 0), '2018-10-30 00:00:00'), ('2018-02-14 00:00:00', datetime(2018, 2, 14, 0, 0), '2019-02-14 00:00:00'), ('2018-03-29 00:00:00', datetime(2018, 3, 29, 0, 0), '2019-03-29 00:00:00'), ('2018-05-14 00:00:00', datetime(2018, 5, 14, 0, 0), '2019-05-14 00:00:00'), ('2018-06-04 00:00:00', datetime(2018, 6, 4, 0, 0), '2019-06-04 00:00:00'), ('2018-08-09 00:00:00', datetime(2018, 8, 9, 0, 0), '2019-08-09 00:00:00'), ('2019-03-14 00:00:00', datetime(2019, 3, 14, 0, 0), '2020-03-14 00:00:00'), ('2019-05-03 00:00:00', datetime(2019, 5, 3, 0, 0), '2020-05-03 00:00:00'), ('2019-05-17 00:00:00', datetime(2019, 5, 17, 0, 0), '2020-05-17 00:00:00'), ('2019-06-17 00:00:00', datetime(2019, 6, 17, 0, 0), '2020-06-17 00:00:00'), ('2019-06-27 00:00:00', datetime(2019, 6, 27, 0, 0), '2020-06-27 00:00:00'), ('2020-01-10 00:00:00', datetime(2020, 1, 10, 0, 0), '2021-01-10 00:00:00'), ('2020-01-31 00:00:00', datetime(2020, 1, 31, 0, 0), '2021-01-31 00:00:00'), ('2020-03-27 00:00:00', datetime(2020, 3, 27, 0, 0), '2021-03-27 00:00:00'), ('2020-05-26 00:00:00', datetime(2020, 5, 26, 0, 0), '2021-05-26 00:00:00'), ('2020-05-27 00:00:00', datetime(2020, 5, 27, 0, 0), '2021-05-27 00:00:00'), ('2020-08-05 00:00:00', datetime(2020, 8, 5, 0, 0), '2021-08-05 00:00:00'), ('2020-08-17 00:00:00', datetime(2020, 8, 17, 0, 0), '2021-08-17 00:00:00'), ('2020-09-11 00:00:00', datetime(2020, 9, 11, 0, 0), '2021-09-11 00:00:00'), ('2020-10-21 00:00:00', datetime(2020, 10, 21, 0, 0), '2021-10-21 00:00:00'), ('2021-02-10 00:00:00', datetime(2021, 2, 10, 0, 0), '2022-02-10 00:00:00'), ('2021-03-30 00:00:00', datetime(2021, 3, 30, 0, 0), '2022-03-30 00:00:00'), ('2021-04-14 00:00:00', datetime(2021, 4, 14, 0, 0), '2022-04-14 00:00:00'), ('2021-07-08 00:00:00', datetime(2021, 7, 8, 0, 0), '2022-07-08 00:00:00'), ('2021-08-11 00:00:00', datetime(2021, 8, 11, 0, 0), '2022-08-11 00:00:00'), ('2021-08-12 00:00:00', datetime(2021, 8, 12, 0, 0), '2022-08-12 00:00:00'), ('2021-08-18 00:00:00', datetime(2021, 8, 18, 0, 0), '2022-08-18 00:00:00'), ('2021-10-28 00:00:00', datetime(2021, 10, 28, 0, 0), '2022-10-28 00:00:00'), ('2021-11-04 00:00:00', datetime(2021, 11, 4, 0, 0), '2022-11-04 00:00:00'), ('2021-11-04 00:00:00', datetime(2021, 11, 4, 0, 0), '2022-11-04 00:00:00'), ('2021-11-11 00:00:00', datetime(2021, 11, 11, 0, 0), '2022-11-11 00:00:00'), ('2021-12-28 00:00:00', datetime(2021, 12, 28, 0, 0), '2022-12-28 00:00:00'), ('2022-01-07 00:00:00', datetime(2022, 1, 7, 0, 0), '2023-01-07 00:00:00'), ('2022-02-08 00:00:00', datetime(2022, 2, 8, 0, 0), '2023-02-08 00:00:00'), ('2022-04-04 00:00:00', datetime(2022, 4, 4, 0, 0), '2023-04-04 00:00:00'), ('2022-05-10 00:00:00', datetime(2022, 5, 10, 0, 0), '2023-05-10 00:00:00'), ('2022-05-26 00:00:00', datetime(2022, 5, 26, 0, 0), '2023-05-26 00:00:00'), ('2022-06-15 00:00:00', datetime(2022, 6, 15, 0, 0), '2023-06-15 00:00:00'), ('2022-06-21 00:00:00', datetime(2022, 6, 21, 0, 0), '2023-06-21 00:00:00'), ('2022-10-17 00:00:00', datetime(2022, 10, 17, 0, 0), '2023-10-17 00:00:00'), ('2022-12-29 00:00:00', datetime(2022, 12, 29, 0, 0), '2023-12-29 00:00:00'), ('2023-01-09 00:00:00', datetime(2023, 1, 9, 0, 0), '2024-01-09 00:00:00'), ('2023-01-20 00:00:00', datetime(2023, 1, 20, 0, 0), '2024-01-20 00:00:00'), ('2023-03-03 00:00:00', datetime(2023, 3, 3, 0, 0), '2024-03-03 00:00:00'), ('2023-03-10 00:00:00', datetime(2023, 3, 10, 0, 0), '2024-03-10 00:00:00'), ('2023-03-22 00:00:00', datetime(2023, 3, 22, 0, 0), '2024-03-22 00:00:00'), ('2023-04-13 00:00:00', datetime(2023, 4, 13, 0, 0), '2024-04-13 00:00:00'), ('2023-04-20 00:00:00', datetime(2023, 4, 20, 0, 0), '2024-04-20 00:00:00'), ('2023-04-28 00:00:00', datetime(2023, 4, 28, 0, 0), '2024-04-28 00:00:00'), ('2023-05-24 00:00:00', datetime(2023, 5, 24, 0, 0), '2024-05-24 00:00:00'), ('2023-08-15 00:00:00', datetime(2023, 8, 15, 0, 0), '2024-08-15 00:00:00'), ('2023-08-24 00:00:00', datetime(2023, 8, 24, 0, 0), '2024-08-24 00:00:00'), ('2023-09-08 00:00:00', datetime(2023, 9, 8, 0, 0), '2024-09-08 00:00:00'), ('2023-10-25 00:00:00', datetime(2023, 10, 25, 0, 0), '2024-10-25 00:00:00')]


    #cur.close()
    #conn.close()
    print()

    #main(datesToTrade1)
