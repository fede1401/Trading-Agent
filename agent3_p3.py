"""
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

# Definiamo come costanti le soglie di acquisto e di vendita. La soglia di acquisto viene utilizzata per sapere quando acquistare un'azione, 
# mentre la soglia di vendita viene utilizzata per sapere quando vendere un'azione.
SA = 1
SV = 2


def main(sectors):
    # configurazione del logging
    logging.basicConfig( level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s" )
    
    #logging.disable(logging.CRITICAL)

    symbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX']

    try:          
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()  
        
        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate( "Federico Ferdinandi", "federico", "TickmillEU-Demo", cur, conn )
        
        profit = []
        
        # Carica i settori e i simboli dal file CSV
        # with open("csv_files/nasdaq_symbols.csv", mode="r") as file:
        #    csv_reader = csv.DictReader(file)
        #    symbols_data = {row["Symbol"]: row["Sector"] for row in csv_reader}
            
        # Posso controllare direttamente prima se i simboli sono dei settori che prendo in input.

        for _ in range(100):
            
            date, initialDate, endDate = getRandomDate(cur)
                        
            # Inizializzazione in caso di primo utilizzo
            budget = budgetInvestimenti = initial_budget = 50000
            equity = margin = 0
            budgetMantenimento = 0
            profitTotalUSD = profitTotalPerc = 0
            ticketPuc = ticketSale = 0
                    
            stateAgent = agentState.AgentState.INITIAL
                    
            dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                    
            # Inserimento dei dati iniziali dell'agente nel database
            insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                    
            stateAgent = agentState.AgentState.PURCHASE
            
            cur.execute("DELETE FROM sale;")
            conn.commit()
            
            cur.execute("DELETE FROM purchase;")
            conn.commit()
            
            
            for symb in symbols:
                
                profit1Y = tradingOnSymb(symb, stateAgent, date, endDate, cur, conn, SV, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, ticketPuc, ticketSale)
              
            profit.append(profitTotalUSD)
            print(f"Profitto: {profit}\n\n")


    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
        

def getRandomDate(cur):
    # Seleziona un giorno casuale all'interno del range temporale che sia piu´ piccolo di 365 giorni rispetto alla data massima presente nel database
    cur.execute("SELECT MAX(time_value_it) - INTERVAL '1 year' FROM nasdaq_actions;")
    max_date = cur.fetchone()[0]
                
    #max_date = max_date - timedelta(days=365)
                
    cur.execute("SELECT time_value_it FROM nasdaq_actions WHERE time_value_it < %s ORDER BY RANDOM() LIMIT 1;", (max_date,))
    date = cur.fetchone()[0]    
    date = date.strftime('%Y-%m-%d %H:%M:%S')
                
    initialDate = date           
    # Converti la stringa in un oggetto datetime
    initialDate = datetime.strptime(initialDate, '%Y-%m-%d %H:%M:%S')

    # Aggiungi 1 anno usando relativedelta
    endDate = initialDate + relativedelta(years=1)
    # Converti endDate in una stringa formattata
    endDate = endDate.strftime('%Y-%m-%d %H:%M:%S')
    
    return date, initialDate, endDate
    



def tradingOnSymb(symbol, stateAgent, date, endDate, cur, conn, SV, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, ticketPuc, ticketSale):
    while True:
        try:
            ######################## inizio SALE
            if stateAgent == agentState.AgentState.SALE:
                logging.info(f"Agent entrato nello stato Sale\n")

                # Recupera gli acquisti nel db.
                cur.execute("SELECT price, ticket FROM purchase WHERE symbol = %s ORDER BY date desc LIMIT 1;", (symbol,))
                pPur = cur.fetchone()
                if pPur is not None:
                    pricePur = pPur[0]
                    tickP = pPur[1]
                    
                    # Recupera le vendite nel db.
                    cur.execute("SELECT ticket_pur FROM sale")
                    sales = {int(sale[0]) for sale in cur.fetchall()}
                    
                    if int(tickP) in sales:
                        continue
                    
                    
                    valMinVendita = pricePur + (pricePur * (SV/100))
                    
                    # Devo effettuare una query per trovare il giorno in cui posso vendere l'azione
                    cur.execute(f"SELECT time_value_it, close_price FROM nasdaq_actions WHERE time_value_it > '{date}' AND close_price >= {valMinVendita} AND symbol = '{symbol}'  ORDER BY time_value_it ASC LIMIT 1;")
                    res = cur.fetchone()
                    if res is not None:
                        dateS = res[0]
                        priceS = res[1]
                     
                        if dateS is not None:
                            date = dateS.strftime('%Y-%m-%d %H:%M:%S')
                            if date >= endDate:
                                break
                                
                            profit = priceS - pricePur
                            perc_profit = profit / pricePur
                            
                            budgetInvestimenti = budgetInvestimenti + ( pricePur * volume )

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            profit_10Perc = (profit * 10) / 100
                            profit_90Perc = (profit * 90) / 100
                            budgetInvestimenti = budgetInvestimenti + ( profit_10Perc * volume )
                            budgetMantenimento = budgetMantenimento + ( profit_90Perc * volume )

                            ticketSale += 1
                                        
                            dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database                            
                            insertDataDB.insertInSale(dateObject, ticketPuc, ticketSale, volume, symbol, priceS, pricePur, profit, perc_profit, cur, conn)

                            # Aggiornamento del valore dei profitti totali .
                            profitTotalUSD += profit * volume
                            profitTotalPerc = (profitTotalUSD/initial_budget)*100
                                        
                                        
                            # Aggiornamento dello stato dell'agent nel database
                            insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                stateAgent = agentState.AgentState.PURCHASE

            ######################## fine SALE

                    
            ######################## inizio PURCHASE
            if stateAgent == agentState.AgentState.PURCHASE:
                logging.info(f"Agent entrato nello stato Purchase\n")
                
                # Calcola la data finale in Python
                dateObj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                
                #date_end = dateObj + timedelta(days=365)

                # Esegui la query con le date calcolate
                cur.execute( """ """
                    SELECT na.time_value_it, na.close_price, 
                        (SELECT AVG(close_price) 
                        FROM nasdaq_actions 
                        WHERE symbol = %s 
                        AND time_value_it BETWEEN na.time_value_it - INTERVAL '50 days' AND na.time_value_it) AS avg_50d
                    FROM nasdaq_actions na
                    WHERE na.symbol = %s 
                    AND na.time_value_it BETWEEN %s AND %s
                    AND na.close_price < ((SELECT AVG(close_price) 
                                            FROM nasdaq_actions 
                                            WHERE symbol = %s 
                                            AND time_value_it BETWEEN na.time_value_it - INTERVAL '50 days' AND na.time_value_it) * (1 - %s))
                    ORDER BY na.time_value_it ASC
                    LIMIT 1;
                """ """, (symbol, symbol, date, endDate, symbol, (SA/100)))
                                        
                # HAVING na.close_price < avg_50d * (1 - %s)
                
                result = cur.fetchone()
                print(result)
                
                if result:
                    # Se troviamo un prezzo valido, procediamo con l'acquisto
                    date = result[0]
                    prezzo_acquisto = result[1]
                    
                    # Calcolo del volume
                    volume = float(math.floor(1000 / prezzo_acquisto))
                    ticketPuc += 1
                    #dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento nel database
                    insertDataDB.insertInPurchase(date, ticketPuc, volume, symbol, prezzo_acquisto, cur, conn)
                    budgetInvestimenti -= (prezzo_acquisto * volume)

                    # Aggiornamento dello stato dell'agente
                    insertDataDB.insertInDataTrader(date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                    logging.info(f"Acquistata azione {symbol}, prezzo: {prezzo_acquisto}, budgetInvestimenti: {budgetInvestimenti}")
                    
                    # Cambio stato a SALE
                    stateAgent = agentState.AgentState.SALE
                else:
                    logging.info("Nessun prezzo inferiore alla soglia trovato, stato attesa")
                    stateAgent = agentState.AgentState.WAIT
                                        
                
                
                """ """cur.execute(f"SELECT close_price FROM nasdaq_actions WHERE time_value_it = '{date}' AND symbol='{symbol}';")
                price = cur.fetchone() # Recupera i dati come lista di tuple
                            
                middlePrice = getValueMiddlePrice(symbol, date, cur)
                                
                price = price[0]
                                    
                if price < middlePrice*(1-(SA/100)):
                    # Calcolo volume e aggiornamento budget
                    volume = float(math.floor(1000 / price))
                    ticketPuc += 1
                    dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                    # Inserimento nel database
                    insertDataDB.insertInPurchase(dateObject, ticketPuc, volume, symbol, price, cur, conn)
                    budgetInvestimenti -= (price * volume)

                    # Aggiornamento stato
                    insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                    # Logging dell'acquisto
                    if logging.getLogger().isEnabledFor(logging.INFO):
                                        logging.info(f"Acquistata azione {symbol}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")
                    
                    # Dopo lo stato di acquisto il programma entra nello stato di attesa
                    stateAgent = agentState.AgentState.SALE
                                    
                else:
                        if logging.getLogger().isEnabledFor(logging.INFO):
                            logging.info(f"Prezzo {price} non inferiore al prezzo medio {middlePrice*(1-(SA/100))} per {symbol} alla data {date}.")              
                                
                        else:
                            if logging.getLogger().isEnabledFor(logging.INFO):
                                logging.info(f"Settore di appartenenza per {symbol} non valido o non trovato.")
                                
                        # Dopo lo stato di acquisto il programma entra nello stato di attesa
                        stateAgent = agentState.AgentState.WAIT
        """
"""            

            ######################## fine PURCHASE


            ######################## inizio WAIT
            if stateAgent == agentState.AgentState.WAIT:
                    logging.info(f"Agent entrato nello stato Wait\n")
                        
                    dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                    # Aggiornamento dello stato dell'agent nel database
                    insertDataDB.insertInDataTrader(dateObject, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                    cur.execute( f"SELECT time_value_it FROM nasdaq_actions WHERE time_value_it > '{date}' ORDER BY time_value_it ASC LIMIT 1;" )
                    date = cur.fetchone()[0]
                    date = date.strftime('%Y-%m-%d %H:%M:%S')

                    if date >= endDate:
                        break

                    logging.info(f"Cambio di stato da WAIT a SALE\n\n")
                    stateAgent = agentState.AgentState.SALE

            ######################## fine WAIT
                    
        except Exception as e:
            logging.critical(f"Errore non gestito: {e}")
            logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

        finally:
            logging.info("Connessione chiusa e fine del trading agent.")
            
"""

import connectDB, insertDataDB, agentState
import psycopg2
import time
import random
import logging
import pytz
from datetime import datetime, timedelta
import math
from dateutil.relativedelta import relativedelta
import traceback
import pandas as pd
import csv


# Definiamo come costanti le soglie di acquisto e di vendita. 
BUY_THRESHOLD = 1
SELL_THRESHOLD = 2


def main(sectors):
    # configurazione del logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    symbols = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX']

    try:          
        # Connessione al database
        cursor, connection = connectDB.connect_nasdaq()  
        
        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate("Federico Ferdinandi", "federico", "TickmillEU-Demo", cursor, connection)
        
        total_profits = []
        
        for _ in range(100):
            trade_date, initial_date, end_date = getRandomDate(cursor)
                        
            # Inizializzazione in caso di primo utilizzo
            initial_budget = 50000
            investment_budget = initial_budget
            total_equity = 0
            total_margin = 0
            maintenance_budget = 0
            total_profit_usd = 0
            total_profit_percentage = 0
            purchase_ticket_count = 0
            sale_ticket_count = 0
                    
            agent_state = agentState.AgentState.INITIAL
                    
            date_object = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
                    
            # Inserimento dei dati iniziali dell'agente nel database
            insertDataDB.insertInDataTrader(date_object, agent_state, initial_budget, investment_budget, total_equity, total_margin, total_profit_usd, total_profit_percentage, maintenance_budget, investment_budget, cursor, connection)
                    
            agent_state = agentState.AgentState.PURCHASE
            
            cursor.execute("DELETE FROM sale;")
            connection.commit()
            
            cursor.execute("DELETE FROM purchase;")
            connection.commit()
            
            cursor.execute("DELETE FROM logindate;")
            connection.commit()
            
            cursor.execute("DELETE FROM datatrader;")
            connection.commit()
            
            
            for symbol in symbols:
                # Esegui la funzione di trading per il simbolo corrente
                tradingOnSymbol(symbol, agent_state, trade_date, end_date, cursor, connection, SELL_THRESHOLD, initial_budget, investment_budget, total_equity, total_margin, total_profit_usd, total_profit_percentage, maintenance_budget, purchase_ticket_count, sale_ticket_count)
              
            total_profits.append(total_profit_usd)
            print(f"Profitto totale: {total_profits}\n\n")

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
        logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")

    finally:
        logging.info("Connessione chiusa e fine del trading agent.")
        

def getRandomDate(cursor):
    # Seleziona un giorno casuale all'interno del range temporale che sia più piccolo di 365 giorni rispetto alla data massima presente nel database
    cursor.execute("SELECT MAX(time_value_it) - INTERVAL '1 year' FROM nasdaq_actions;")
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
    

def tradingOnSymbol(symbol, agent_state, trade_date, end_date, cursor, connection, sell_threshold, initial_budget, investment_budget, total_equity, total_margin, total_profit_usd, total_profit_percentage, maintenance_budget, purchase_ticket_count, sale_ticket_count):
    while True:
        try:
            ######################## inizio SALE
            if agent_state == agentState.AgentState.SALE:
                logging.info(f"Agent entrato nello stato Sale\n")

                # Recupera gli acquisti nel db.
                cursor.execute("SELECT price, ticket FROM purchase WHERE symbol = %s ORDER BY date DESC LIMIT 1;", (symbol,))
                purchase_record = cursor.fetchone()
                if purchase_record is not None:
                    purchase_price = purchase_record[0]
                    purchase_ticket = purchase_record[1]
                    
                    # Recupera le vendite nel db.
                    cursor.execute("SELECT ticket_pur FROM sale")
                    sales_tickets = {int(sale[0]) for sale in cursor.fetchall()}
                    
                    if int(purchase_ticket) in sales_tickets:
                        agent_state = agentState.AgentState.PURCHASE
                        continue
                    
                    minimum_sale_value = purchase_price + (purchase_price * (sell_threshold / 100))
                    
                    # Effettua una query per trovare il giorno in cui posso vendere l'azione
                    cursor.execute(f"SELECT time_value_it, close_price FROM nasdaq_actions WHERE time_value_it > '{trade_date}' AND close_price >= {minimum_sale_value} AND symbol = '{symbol}' ORDER BY time_value_it ASC LIMIT 1;")
                    sale_record = cursor.fetchone()
                    if sale_record is not None:
                        sale_date = sale_record[0]
                        trade_date = sale_date
                        sale_price = sale_record[1]
                     
                        if sale_date is not None:
                            #trade_date = sale_date.strftime('%Y-%m-%d %H:%M:%S')
                            if trade_date >= end_date:
                                break
                                
                            profit = sale_price - purchase_price
                            profit_percentage = profit / purchase_price
                            
                            investment_budget += (purchase_price * volume)

                            # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                            profit_reinvestment = (profit * 10) / 100
                            profit_maintenance = (profit * 90) / 100
                            investment_budget += (profit_reinvestment * volume)
                            maintenance_budget += (profit_maintenance * volume)

                            sale_ticket_count += 1
                                        
                            #date_object = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                            # Inserimento dei dati relativi alla vendita del simbolo azionario nel database                            
                            insertDataDB.insertInSale(trade_date, purchase_ticket, sale_ticket_count, volume, symbol, sale_price, purchase_price, profit, profit_percentage, cursor, connection)

                            # Aggiornamento del valore dei profitti totali .
                            total_profit_usd += profit * volume
                            total_profit_percentage = (total_profit_usd / initial_budget) * 100
                                        
                            # Aggiornamento dello stato dell'agente nel database
                            insertDataDB.insertInDataTrader(trade_date, agent_state, initial_budget, investment_budget, total_equity, total_margin, total_profit_usd, total_profit_percentage, maintenance_budget, investment_budget, cursor, connection)

                agent_state = agentState.AgentState.PURCHASE

            ######################## fine SALE

                    
            ######################## inizio PURCHASE
            if agent_state == agentState.AgentState.PURCHASE:
                logging.info(f"Agent entrato nello stato Purchase\n")
                
                # Calcola la data finale in Python
                #date_object = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')

                # Esegui la query con le date calcolate
                cursor.execute("""
                    SELECT na.time_value_it, na.close_price, 
                        (SELECT AVG(close_price) 
                         FROM nasdaq_actions 
                         WHERE symbol = %s 
                         AND time_value_it BETWEEN na.time_value_it - INTERVAL '50 days' AND na.time_value_it) AS avg_50d
                    FROM nasdaq_actions na
                    WHERE na.symbol = %s 
                    AND na.time_value_it BETWEEN %s AND %s
                    AND na.close_price < ((SELECT AVG(close_price) 
                                            FROM nasdaq_actions 
                                            WHERE symbol = %s 
                                            AND time_value_it BETWEEN na.time_value_it - INTERVAL '50 days' AND na.time_value_it) * (1 - %s))
                    ORDER BY na.time_value_it ASC
                    LIMIT 1;
                """, (symbol, symbol, trade_date, end_date, symbol, (BUY_THRESHOLD / 100)))
                                        
                result = cursor.fetchone()
                print(result)
                
                if result:
                    # Se troviamo un prezzo valido, procediamo con l'acquisto
                    trade_date = result[0]
                    purchase_price = result[1]
                    
                    # Calcolo del volume
                    volume = float(math.floor(1000 / purchase_price))
                    purchase_ticket_count += 1

                    # Inserimento nel database
                    insertDataDB.insertInPurchase(trade_date, purchase_ticket_count, volume, symbol, purchase_price, cursor, connection)
                    investment_budget -= (purchase_price * volume)

                    # Aggiornamento dello stato dell'agente nel database
                    total_equity = investment_budget + maintenance_budget
                    insertDataDB.insertInDataTrader(trade_date, agent_state, initial_budget, investment_budget, total_equity, total_margin, total_profit_usd, total_profit_percentage, maintenance_budget, investment_budget, cursor, connection)

                agent_state = agentState.AgentState.SALE

            ######################## fine PURCHASE
            
            
            # Calcola la data finale in Python
            #trade_date = datetime.strptime(trade_date, '%Y-%m-%d %H:%M:%S')
            #end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
            
            if trade_date >= end_date:
                break

        except Exception as e:
            logging.critical(f"Errore non gestito: {e}")
            logging.critical(f"Dettagli del traceback:\n{traceback.format_exc()}")
            break  # Esci dal ciclo in caso di errore




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


    

def getValueMiddlePrice(chosen_symbol, date, cur):
    start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S') - timedelta(days=50)
    cur.execute("SELECT close_price FROM nasdaq_actions WHERE symbol = %s AND time_value_it BETWEEN %s AND %s;", (chosen_symbol, start_date, date))
    prices = [row[0] for row in cur.fetchall()]
    
    if len(prices) == 0:
        return 0  # O gestisci come preferisci il caso senza dati
    
    return sum(prices) / len(prices)






if __name__ == "__main__":
    
    getSectorSymbols()
    
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()

    # Recupera i settori nel database:
    cur.execute("SELECT * FROM sector;")
    sectors = [ sec[0] for sec in cur.fetchall() ]  # Estrai solo il primo elemento di ogni tupla
    print(sectors)
    
    cur.close()
    conn.close()

    i = 1
    for sec in sectors:
        print(f"{i}: {sec}\n")
        i += 1

    print( f"Scegli uno o più settori su cui applicare l'agente (indicando i numeri con virgole se più di uno):\n" )
    """choises = input("Scrivi i numeri: ")

    choises = choises.split(",")
    choises = [int(x) for x in choises]
    print(choises)"""
    choises = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,11]

    sectors = [sectors[i - 1] for i in choises]
    print(sectors)
    
    date = '2023-09-08 15:30:00'

    main(sectors)