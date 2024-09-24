# Ordinamento del 5% delle azioni della borsa Nasdaq per capitalizzazione decrescente (pool)
# Fino ad esaurimento budget si acquistano azioni random dal pool
# Vendesi delle azioni che sono salite del TP% = 1 rispetto al prezzo d'acquisto
# sleep di 15 minuti

# import MetaTrader5 as mt5
from datetime import datetime
import connectDB, insertDataDB, agentState
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




def main(sectors, date):
    # configurazione del logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
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
        


    # fasi
    # 1. Acquisto di azioni random dal pool fino a esaurimento budget
    # 2. Vendita delle azioni che sono salite del TP% = 1 rispetto al prezzo d'acquisto

    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate( "Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn )

        # Recupera l'ultimo stato dell'agent nel database:
        cur.execute("SELECT * FROM DataTrader ORDER BY date DESC LIMIT 1")
        last_state = cur.fetchone()

        initialDate = date
        
        # Converti la stringa in un oggetto datetime
        initialDate = datetime.strptime(initialDate, '%Y-%m-%d %H:%M:%S')

        # Aggiungi 1 anno usando relativedelta
        endDate = initialDate + relativedelta(years=1)

        # Converti endDate in una stringa formattata
        endDate = endDate.strftime('%Y-%m-%d %H:%M:%S')

        # Se last_state contiene un valore, viene destrutturato in variabili individuali.
        if last_state:
            ( last_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti ) = last_state
            
            logging.info( f"Ripresa stato dell'agent: {stateAgent}, Budget: {budget}, Profitto totale USD: {profitTotalUSD}, Profitto totale percentuale: {profitTotalPerc}, Budget Mantenimento: {budgetMantenimento}, Budget Investimenti: {budgetInvestimenti}\n" )

            if stateAgent == "WAIT":
                stateAgent = agentState.AgentState.WAIT

            if stateAgent == "SALE":
                stateAgent = agentState.AgentState.SALE

            if stateAgent == "PURCHASE":
                stateAgent = agentState.AgentState.PURCHASE

            # In questo modo se il programma viene bloccato e rimane nello stato INITIAL può entrare nel While e vedere se ci sono azioni da vendere
            if stateAgent == "INITIAL":
                logging.info(f"Cambio di stato da WAIT a SALE\n")
                stateAgent = agentState.AgentState.SALE

            logging.info(f"StateAgent: {stateAgent}\n")
            
            date = last_date
            date = date.strftime('%Y-%m-%d %H:%M:%S')
            
            cur.execute( f"SELECT ticket FROM purchase ORDER BY ticket DESC LIMIT 1;" )
            ticketPuc = int(cur.fetchone()[0])
            
            cur.execute( f"SELECT ticket_sale FROM sale ORDER BY ticket_sale DESC LIMIT 1;" )
            ticketSale = int(cur.fetchone()[0])

        # Se last_state è vuoto, allora l'agente si trova nello stato iniziale.
        else:
            # Inizializza delle variabili se non ci sono dati precedenti
            budget = 50000
            equity = 0
            margin = 0
            initial_budget = budget
            budgetInvestimenti = budget

            budgetMantenimento = 0
            profitTotalUSD = 0
            profitTotalPerc = 0
            
            ticketPuc = 0
            ticketSale = 0
            
            stateAgent = agentState.AgentState.INITIAL
            
            dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

            # Inserimento dei dati iniziali dell'agente nel database
            insertDataDB.insertInDataTrader(
                dateObject,
                stateAgent,
                initial_budget,budget, equity, margin,
                profitTotalUSD, profitTotalPerc,
                budgetMantenimento, budgetInvestimenti,
                cur, conn,
            )
            logging.info(f"Budget iniziale: {budget}\n")

            stateAgent = agentState.AgentState.SALE

        # Il ciclo principale esegue le operazioni di trading

        while True:

            ######################## inizio SALE
            if stateAgent == agentState.AgentState.SALE:
                logging.info(f"Agent entrato nello stato Sale\n")

                # Recupera le vendite nel db.
                cur.execute("SELECT ticket_pur FROM sale")
                salesDB = cur.fetchall()

                sales = []
                for sal in salesDB:
                    sales.append(sal[0])

                logging.info(f"I ticket delle vendite già effettuate sono: {sales}\n")

                # Recupera gli acquisti nel db.
                cur.execute("SELECT * FROM purchase;")
                purchasesDB = cur.fetchall()

                for pur in purchasesDB:
                    ticketP = pur[1]
                    volume = pur[2]
                    symbol = pur[3]
                    price_open = pur[4]
                    
                    cur.execute( f"SELECT open_price FROM nasdaq_actions WHERE symbol = '{symbol}' AND time_value_it='{date}';" )    
                    result = cur.fetchone()

                    if result is not None:
                        price_current = result[0]
                    
                    else:
                        logging.info(f"Simbolo {symbol} non presente nella data in input.\n")
                        continue
                    

                    # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                    if price_current > price_open:
                        logging.info( f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n" )

                        # Calcolo del profitto:
                        profit = price_current - price_open
                        perc_profit = profit / price_open

                        # Rivendita con l'1 % di profitto
                        if perc_profit > 0.01:

                            logging.info( f"Si può vendere {symbol} poiché c'è un profitto del {perc_profit}\n" )

                            # aggiorno il budget
                            budgetInvestimenti = budgetInvestimenti + ( price_open * volume )

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            profit_10Perc = (profit * 10) / 100
                            profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + ( profit_10Perc * volume )
                            budgetMantenimento = budgetMantenimento + ( profit_90Perc * volume )

                            ticketSale += 1
                            
                            dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                            insertDataDB.insertInSale(
                                dateObject,
                                ticket_pur=ticketP, ticket_sale=ticketSale,
                                volume=volume, symbol=symbol,
                                priceSale=price_current, pricePurchase=price_open,
                                profitUSD=profit, profitPerc=perc_profit,
                                cur=cur, conn=conn,
                            )

                
                            # Aggiornamento del valore dei profitti totali .
                            profitTotalUSD += profit * volume
                            profitTotalPerc = perc_profit

                            # Aggiornamento dello stato dell'agent nel database
                            insertDataDB.insertInDataTrader(
                                dateObject,
                                stateAgent,
                                initial_budget, budget, equity, margin,
                                profitTotalUSD, profitTotalPerc,
                                budgetMantenimento, budgetInvestimenti,
                                cur,  conn,
                            )

                            logging.info( f"Venduta azione {symbol}, profitto: {profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}\n")
                            logging.info( "---------------------------------------------------------------------------------\n\n" )

                price_open = -1
                price_current = -1
                
                # Una volta controllati tutti i simboli azionari si passa allo stato di compravendita.
                logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")
                stateAgent = agentState.AgentState.PURCHASE

            ######################## fine SALE

            
            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:
                logging.info(f"Agent entrato nello stato Purchase\n")

                # Acquisto di azioni finché c'è budget
                while budgetInvestimenti > 0:

                    symbInQ = False
                    while symbInQ == False:

                        # Scelgo un'azione random dal pool
                        symbolRandom = random.randint(0, len(symbols) - 1)

                        logging.info( f"Possiamo acquistare perché il budget dell'investimento è > 0: simbolo scelto randomicamente tra il pool delle azioni accettate dal broker TickMill è: {symbols[symbolRandom]}\n"  )

                        sectFind = False
                        while sectFind == False:
                            # Apri il file CSV in modalità lettura
                            with open("csv_files/nasdaq_symbols.csv", mode="r") as file:
                                # Crea un lettore CSV con DictReader
                                csv_reader = csv.DictReader(file)

                                for col in csv_reader:
                                    if ( col["Symbol"] == symbols[symbolRandom] ):
                                        #logging.info( f"Settore di appartenenza dell'azione scelta: {col['Sector']}\n" )

                                        if col["Sector"] in sectors:
                                            #logging.info( f"Settore di appartenenza dell'azione scelta è tra quelli scelti dall'utente.\n")
                                            sectFind = True
                                            break
                                        else:
                                            #logging.info( f"Settore di appartenenza dell'azione scelta non è tra quelli scelti dall'utente, si passa alla prossima azione.\n" )
                                            sectFind = False

                        cur.execute( f"SELECT symbol, open_price FROM nasdaq_actions WHERE time_value_it = '{date}';" )
                        symbolsQ = cur.fetchall()
                        
                        #symbolsName = []
                        for sy in symbolsQ:
                            if symbols[symbolRandom] == sy[0]:
                                
                                price = sy[1]
                                symbInQ = True
                                logging.info( f"Simbolo scelto è tra quelli della data in input.\n" )

                    volume = float(math.floor(1000 / price))
                    logging.info(f"\n volume:{volume}\n")

                    ticketPuc += 1
                    
                    dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento dei dati relativi all'acquisto nel database
                    insertDataDB.insertInPurchase(
                        dateObject,
                        ticketPuc,
                        volume,
                        symbols[symbolRandom],
                        price,
                        cur, conn
                    )

                    # Aggiornamento del budget di investimento dopo l'acquisto dell'azione
                    budgetInvestimenti = budgetInvestimenti - (price * volume)

                    # Aggiornamento dello stato dell'agent nel database
                    insertDataDB.insertInDataTrader(
                        dateObject,
                        stateAgent,
                        initial_budget, budget, equity, margin,
                        profitTotalUSD, profitTotalPerc,
                        budgetMantenimento, budgetInvestimenti,
                        cur, conn
                    )

                    logging.info(f"Acquistata azione {symbols[symbolRandom]}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}\n" )
                    logging.info("---------------------------------------------------------------------------------\n\n" )

                logging.info(f"Cambio di stato da PURCHASE a WAIT\n\n")

                # Dopo lo stato di acquisto il programma entro nello stato di attesa
                stateAgent = agentState.AgentState.WAIT

            ######################## fine PURCHASE



            ######################## inizio WAIT

            # Il programma si interrompe per 15 minuti poi riparte
            if stateAgent == agentState.AgentState.WAIT:
                logging.info(f"Agent entrato nello stato Wait\n")
                
                dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                # Aggiornamento dello stato dell'agent nel database
                insertDataDB.insertInDataTrader(
                    dateObject,
                    stateAgent,
                    initial_budget, budget, equity, margin,
                    profitTotalUSD, profitTotalPerc,
                    budgetMantenimento, budgetInvestimenti,
                    cur, conn
                )
                logging.info("Interruzione del programma.\n")

                # Il programma si interrompe
                cur.execute( f"SELECT time_value_it  FROM nasdaq_actions WHERE time_value_it > '{date}' ORDER BY time_value_it ASC LIMIT 1;" )
                date = cur.fetchone()[0]
                date = date.strftime('%Y-%m-%d %H:%M:%S')

                if date == endDate:
                    break

                logging.info(f"Cambio di stato da WAIT a SALE\n\n")
                stateAgent = agentState.AgentState.SALE

            ######################## fine WAIT

        # fine while True:

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        #session_management.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")



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

    # Ritorna il dizionario con i simboli e il settore di appartenenza
    return diz





if __name__ == "__main__":
    
    getSectorSymbols()
    
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()

    # Recupera i settori nel database:
    cur.execute("SELECT * FROM sector;")
    sectors = [ sec[0] for sec in cur.fetchall() ]  # Estrai solo il primo elemento di ogni tupla
    print(sectors)

    i = 1
    for sec in sectors:
        print(f"{i}: {sec}\n")
        i += 1

    print( f"Scegli uno o più settori su cui applicare l'agente (indicando i numeri con virgole se più di uno):\n" )
    choises = input("Scrivi i numeri: ")

    choises = choises.split(",")
    choises = [int(x) for x in choises]
    print(choises)

    sectors = [sectors[i - 1] for i in choises]
    print(sectors)
    
    date = '2023-09-08 15:30:00'

    main(sectors, date)


