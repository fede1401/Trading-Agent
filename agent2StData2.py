import connectDB, insertDataDB, agentState
import psycopg2
import logging
import random
import csv
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import traceback


def main(sectors, start_date):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    symbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX', 'AMD', 'AZN', 'QCOM', 'ADBE']
    start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
    end_date = start_date + relativedelta(years=1)

    try:
        cur, conn = connectDB.connect_nasdaq()

        insertDataDB.insertInLoginDate("Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn)

        # Recupera lo stato precedente dell'agente
        cur.execute("SELECT * FROM DataTrader ORDER BY date DESC LIMIT 1")
        last_state = cur.fetchone()

        if last_state:
            last_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti = last_state
            logging.info(f"Ripresa stato dell'agent: {stateAgent}, Budget: {budget}, Profitto totale USD: {profitTotalUSD}")

            stateAgent = agentState.AgentState[stateAgent] if stateAgent in agentState.AgentState.__members__ else agentState.AgentState.WAIT

            # Carica gli ultimi ticket di acquisto e vendita
            cur.execute("SELECT MAX(ticket) FROM purchase")
            ticketPuc = cur.fetchone()[0] or 0
            cur.execute("SELECT MAX(ticket_sale) FROM sale")
            ticketSale = cur.fetchone()[0] or 0
        else:
            # Inizializzazione in caso di primo utilizzo
            budget = budgetInvestimenti = initial_budget = 50000
            equity = margin = profitTotalUSD = profitTotalPerc = budgetMantenimento = 0
            ticketPuc = ticketSale = 0
            stateAgent = agentState.AgentState.INITIAL

            insertDataDB.insertInDataTrader(start_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
            logging.info(f"Budget iniziale: {budget}")
            stateAgent = agentState.AgentState.SALE

        while True:
            ######################## inizio SALE
            if stateAgent == agentState.AgentState.SALE:
                logging.info("Agent entrato nello stato Sale")
                
                # Recupera le vendite già effettuate
                cur.execute("SELECT ticket_pur FROM sale")
                sales = {int(sale[0]) for sale in cur.fetchall()}

                # Recupera gli acquisti dal DB
                cur.execute("SELECT * FROM purchase")
                purchasesDB = cur.fetchall()

                for pur in purchasesDB:
                    ticketP, volume, symbol, price_open = pur[1], pur[2], pur[3], pur[4]
                    
                    if ticketP in sales:
                        continue

                    cur.execute(f"SELECT open_price FROM nasdaq_actions WHERE symbol = %s AND time_value_it = %s", (symbol, start_date))
                    result = cur.fetchone()

                    if not result:
                        logging.info(f"Simbolo {symbol} non presente alla data: {start_date}")
                        continue

                    price_current = result[0]

                    if price_current > price_open:
                        profit = (price_current - price_open) * volume
                        perc_profit = profit / (price_open * volume)

                        if perc_profit > 0.01:
                            budgetInvestimenti += (price_open + profit * 0.10) * volume
                            budgetMantenimento += profit * 0.90 * volume

                            ticketSale += 1
                            insertDataDB.insertInSale(start_date, ticketP, ticketSale, volume, symbol, price_current, price_open, profit, perc_profit, cur, conn)
                            profitTotalUSD += profit
                            profitTotalPerc = perc_profit

                            insertDataDB.insertInDataTrader(start_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                            logging.info(f"Venduta azione {symbol} con profitto di {profit} USD")

                stateAgent = agentState.AgentState.PURCHASE
            ######################## fine SALE

            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:
                logging.info("Agent entrato nello stato Purchase")

                while budgetInvestimenti > 0:
                    while True:
                        symbolRandom = random.choice(symbols)

                        cur.execute(f"SELECT symbol, open_price FROM nasdaq_actions WHERE symbol = %s AND time_value_it = %s", (symbolRandom, start_date))
                        result = cur.fetchone()
                        if result:
                            price = result[1]
                            break

                    volume = math.floor(1000 / price)
                    ticketPuc += 1
                    insertDataDB.insertInPurchase(start_date, ticketPuc, volume, symbolRandom, price, cur, conn)

                    budgetInvestimenti -= price * volume
                    insertDataDB.insertInDataTrader(start_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                    logging.info(f"Acquistata azione {symbolRandom}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")

                stateAgent = agentState.AgentState.WAIT
            ######################## fine PURCHASE
            
            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:
                logging.info(f"Agent entrato nello stato Purchase\n")

                # Carica i settori e i simboli dal file CSV
                with open("csv_files/nasdaq_symbols.csv", mode="r") as file:
                    csv_reader = csv.DictReader(file)
                    symbols_data = {row["Symbol"]: row["Sector"] for row in csv_reader}

                # Eseguire una query all'inizio per ottenere tutti i simboli e i prezzi
                cur.execute(f"SELECT symbol, open_price FROM nasdaq_actions WHERE time_value_it = '{date}';")
                symbolsQ = {sy[0]: sy[1] for sy in cur.fetchall()}

                # Acquisto di azioni finché c'è budget
                while budgetInvestimenti > 0:

                    # Scelgo un'azione random dal pool
                    symbolRandom = random.randint(0, len(symbols) - 1)
                    chosen_symbol = symbols[symbolRandom]

                    # Verifica se il simbolo è in un settore accettato e se è presente nelle query SQL
                    if chosen_symbol in symbols_data and symbols_data[chosen_symbol] in sectors:
                        if chosen_symbol in symbolsQ:
                            price = symbolsQ[chosen_symbol]

                            # Calcolo volume e aggiornamento budget
                            volume = float(math.floor(1000 / price))
                            ticketPuc += 1
                            dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento nel database
                            insertDataDB.insertInPurchase(dateObject, ticketPuc, volume, symbolRandom, price, cur, conn)
                            budgetInvestimenti -= (price * volume)

                            # Aggiornamento stato
                            insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                            # Logging dell'acquisto
                            if logging.getLogger().isEnabledFor(logging.INFO):
                                logging.info(f"Acquistata azione {chosen_symbol}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")
                        else:
                            if logging.getLogger().isEnabledFor(logging.INFO):
                                logging.info(f"Simbolo {chosen_symbol} non trovato nella data specificata.")
                    else:
                        if logging.getLogger().isEnabledFor(logging.INFO):
                            logging.info(f"Settore di appartenenza per {chosen_symbol} non valido o non trovato.")

                logging.info(f"Cambio di stato da PURCHASE a WAIT\n\n")

                # Dopo lo stato di acquisto il programma entra nello stato di attesa
                stateAgent = agentState.AgentState.WAIT

            ######################## fine PURCHASE

            ######################## inizio WAIT
            if stateAgent == agentState.AgentState.WAIT:
                logging.info("Agent entrato nello stato Wait")
                insertDataDB.insertInDataTrader(start_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                cur.execute(f"SELECT time_value_it FROM nasdaq_actions WHERE time_value_it > %s ORDER BY time_value_it ASC LIMIT 1", (start_date,))
                next_date = cur.fetchone()
                if not next_date or next_date[0] >= end_date:
                    break

                start_date = next_date[0]
                stateAgent = agentState.AgentState.SALE
            ######################## fine WAIT

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        cur.close()
        conn.close()
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


