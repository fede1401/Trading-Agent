# Ordinamento del 5% delle azioni della borsa Nasdaq per capitalizzazione decrescente (pool)
# Fino ad esaurimento budget si acquistano azioni random dal pool
# Vendesi delle azioni che sono salite del TP% = 1 rispetto al prezzo d'acquisto
# sleep di 15 minuti
 
import MetaTrader5 as mt5
from datetime import datetime
import session_management, info_order_send,symbolsAcceptedByTickmill, connectDB, accountInfo, insertDataDB, agentState
import psycopg2
import time
import random
import logging
import pytz
from datetime import datetime, time, timedelta
import time as time_module
import csv
import agent2


def main(sectors):
    # configurazione del logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        # Connessione al database
        cur, conn = connectDB.connect_nasdaq()

        # Connessione al server MetaTrader 5 e login e salvataggio nel db per lo storico dei login.
        session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)
        
        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate(session_management.name, session_management.account, session_management.server, cur, conn)

        # Ottenimento del 5% delle azioni del Nasdaq ordinate per capitalizzazione decrescente.
        pool_Actions_Nasdaq = symbolsAcceptedByTickmill.get5PercentSymbolsCapDesc()

        # Recupera l'ultimo stato dell'agent nel database:
        cur.execute("SELECT * FROM DataTrader ORDER BY date DESC LIMIT 1")
        last_state = cur.fetchone()

        # Se last_state contiene un valore, viene destrutturato in variabili individuali.
        if last_state:
            
            (last_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti) = last_state
            logging.info(f"Ripresa stato dell'agent: {stateAgent}, Budget: {budget}, Profitto totale USD: {profitTotalUSD}, Profitto totale percentuale: {profitTotalPerc}, Budget Mantenimento: {budgetMantenimento}, Budget Investimenti: {budgetInvestimenti}\n")

            if stateAgent == 'WAIT':
                stateAgent = agentState.AgentState.WAIT

            if stateAgent == 'SALE':
                stateAgent = agentState.AgentState.SALE

            if stateAgent == 'PURCHASE':
                stateAgent = agentState.AgentState.PURCHASE
            
            # In questo modo se il programma viene bloccato e rimane nello stato INITIAL può entrare nel While e vedere se ci sono azioni da vendere
            if stateAgent == 'INITIAL':
                logging.info(f"Cambio di stato da WAIT a SALE\n")
                stateAgent = agentState.AgentState.SALE

            logging.info(f"StateAgent: {stateAgent}\n")
            

        # Se last_state è vuoto, allora l'agente si trova nello stato iniziale.
        else:
            # Inizializza delle variabili se non ci sono dati precedenti
            budget = accountInfo.get_balance_account()
            equity = accountInfo.get_equity_account()
            margin = accountInfo.get_margin_account()
            initial_budget = budget
            budgetInvestimenti = budget

            budgetMantenimento = 0
            profitTotalUSD = 0
            profitTotalPerc = 0

            stateAgent = agentState.AgentState.INITIAL
            
            # Inserimento dei dati iniziali dell'agente nel database
            insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
            logging.info(f"Budget iniziale: {budget}\n")
            
            stateAgent = agentState.AgentState.SALE


        # Il ciclo principale esegue le operazioni di trading basandosi sull'orario di apertura della borsa Nasdaq (09:30 - 16:00 orario di New York), 
        # poiché durante l'orario di chiusura non possono essere effettuate operazioni di acquisto e vendita.
        
        while True:
            
                if stateAgent == agentState.AgentState.SALE :
                    logging.info(f"Agent entrato nello stato Sale\n")

                    # Recupera le vendite nel db.
                    cur.execute("SELECT ticket_pur FROM sale")
                    salesDB = cur.fetchall()

                    sales = []
                    for sal in salesDB:
                        sales.append(sal[0])

                    logging.info(f"I ticket delle vendite già effettuate sono: {sales}\n")
        

                    # Per tutte le azioni comprate rivendo quelle che sono salite del TP = 1% rispetto al prezzo di acquisto
                    for act in pool_Actions_Nasdaq:

                        # Ottenimento operazioni di trading attualmente in corso tramite simbolo azionario
                        positions = mt5.positions_get(symbol=act)
                        if positions is not None:

                            # Per ogni posizione di quell'azione:
                            for pos in positions:

                                logging.info(f"{pos}\n")
                                    
                                # Se il ticket della posizione di un'azione è presente tra i ticket venduti, allora procediamo con il prossimo ciclo.
                                if str(pos.ticket) in sales:
                                    logging.info(f"La vendita dell'azione {act} è già stata effettuata.\n")
                                    
                                    logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")
                                    stateAgent = agentState.AgentState.PURCHASE
                                    continue

                                        
                                logging.info(f"Lavoriamo con l'azione acquistata {act}\n")
                                        
                                # Ottenimento prezzo di acquisto(open), prezzo corrente, id ticket e volume di azioni acquistate
                                price_open = pos.price_open
                                price_current = pos.price_current
                                ticket = pos.ticket
                                volume = pos.volume

                                # Se il prezzo corrente è maggiore del prezzo iniziale di acquisto c'è un qualche profitto
                                if price_current > price_open:
                                    logging.info(f"Price current: {price_current} maggiore del prezzo di apertura: {price_open}\n")

                                    # Calcolo del profitto:
                                    profit = price_current - price_open
                                    perc_profit = profit / price_open

                                    # Rivendita con l'1 % di profitto
                                    if perc_profit > 0.01:
                                        
                                        logging.info(f"Si può vendere {act} poiché c'è un profitto del {perc_profit}\n")

                                        #ticket_sale = info_order_send.sell_Action(act)
                                        ticket_sale = info_order_send.close_Position(act, position=pos)

                                        # aggiorno il budget
                                        budgetInvestimenti = budgetInvestimenti + (price_open * volume)

                                        # Per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                                        profit_10Perc = (profit*10)/100
                                        profit_90Perc = (profit*90)/100
                                        budgetInvestimenti = budgetInvestimenti + (profit_10Perc * volume)
                                        budgetMantenimento = budgetMantenimento + (profit_90Perc * volume)

                                        # Inserimento dei dati relativi alla vendita del simbolo azionario nel database
                                        insertDataDB.insertInSale(datetime.now(), ticket_pur=ticket, ticket_sale=ticket_sale, volume=volume, symbol=act, priceSale=price_current, pricePurchase=price_open, profitUSD=profit, profitPerc=perc_profit, cur=cur, conn=conn)    

                                        # Aggiornamento del budget dopo la vendita con inclusi i profitti
                                        budget = accountInfo.get_balance_account() 
                                        equity = accountInfo.get_equity_account()
                                        margin = accountInfo.get_margin_account()

                                        # Aggiornamento del valore dei profitti totali .
                                        profitTotalUSD += (profit * volume)
                                        profitTotalPerc =  perc_profit

                                        # Aggiornamento dello stato dell'agent nel database
                                        insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                                        logging.info(f"Venduta azione {act}, profitto: {profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}\n")
                                        
                                        logging.info("---------------------------------------------------------------------------------\n\n")


                    # Una volta controllati tutti i simboli azionari si passa allo stato di compravendita.
                    logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")
                    stateAgent = agentState.AgentState.PURCHASE

                ######################## fine SALE


                ######################## inizio PURCHASE
                if stateAgent == agentState.AgentState.PURCHASE :
                    logging.info(f"Agent entrato nello stato Purchase\n")
                    
                    # Carica il file CSV una volta e memorizza i simboli e settori in un dizionario
                    symbol_sector_map = {}
                    with open('csv_files/nasdaq_symbols.csv', mode='r') as file:
                        csv_reader = csv.DictReader(file)
                        for row in csv_reader:
                            symbol_sector_map[row['Symbol']] = row['Sector']
                            
                    # Acquisto di azioni finché c'è budget
                    while budgetInvestimenti > 0:

                        # Scelgo un'azione random dal pool
                        symbolRandom = random.randint(0, len(pool_Actions_Nasdaq) - 1)
                        chosen_symbol = pool_Actions_Nasdaq[symbolRandom]
                        logging.info(f"Possiamo acquistare perché il budget dell'investimento è > 0: simbolo scelto randomicamente è: {chosen_symbol}\n")

                        # Controllo il settore dell'azione scelta
                        sector = symbol_sector_map.get(chosen_symbol)
                        if sector and sector in sectors:
                            logging.info(f"Settore di appartenenza dell'azione scelta ({sector}) è tra quelli scelti dall'utente.\n")
                            
                            # Compro l'azione corrispondente
                            result = info_order_send.buy_actions_of_title(chosen_symbol)
                            if result is not None:
                                logging.info(f"Acquisto completato: {result}\n")
                            else:
                                logging.error("Acquisto fallito.\n")
                                continue  # Se l'acquisto fallisce, passa al prossimo simbolo

                            # Si ottengono i dati relativi all'acquisto
                            price = result.price
                            volume = result.volume
                            ticket = result.order

                            # Inserimento dei dati relativi all'acquisto nel database
                            insertDataDB.insertInPurchase(datetime.now(), ticket, volume, chosen_symbol, price, cur, conn)

                            # Aggiornamento del budget di investimento dopo l'acquisto dell'azione
                            budgetInvestimenti -= (price * volume)

                            # Aggiornamento del budget dopo l'acquisto dell'azione
                            budget = accountInfo.get_balance_account()
                            equity = accountInfo.get_equity_account()
                            margin = accountInfo.get_margin_account()

                            # Aggiornamento dello stato dell'agent nel database
                            insertDataDB.insertInDataTrader(
                                datetime.now(), stateAgent, initial_budget, budget, equity, margin,
                                profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn
                            )

                            logging.info(f"Acquistata azione {chosen_symbol}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}\n")
                            logging.info("---------------------------------------------------------------------------------\n\n")
                        else:
                            logging.info(f"Settore di appartenenza dell'azione scelta ({sector}) non è tra quelli scelti dall'utente, si passa alla prossima azione.\n")

                    logging.info(f"Cambio di stato da PURCHASE a WAIT\n\n")

                    # Dopo lo stato di acquisto il programma entra nello stato di attesa
                    stateAgent = agentState.AgentState.WAIT

                ######################## fine PURCHASE

                
                ######################## inizio WAIT

                # Il programma si interrompe per 15 minuti poi riparte
                if stateAgent == agentState.AgentState.WAIT :
                    logging.info(f"Agent entrato nello stato Wait\n")

                    # Aggiornamento dello stato dell'agent nel database
                    insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                    logging.info("Interruzione del programma per 15 minuti.\n")
                    
                    # Il programma si interrompe per 15 minuti
                    time_module.sleep(900)

                    logging.info(f"Cambio di stato da WAIT a SALE\n\n")
                    stateAgent = agentState.AgentState.SALE
                    
                ######################## fine WAIT

        # fine while True:


    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
    
    finally:
        session_management.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")





if __name__ == '__main__':
    # Connessione al database
    cur, conn = connectDB.connect_nasdaq()
    
    # Recupera i settori nel database:
    cur.execute("SELECT * FROM sector;")
    sectors = [sec[0] for sec in cur.fetchall()]  # Estrai solo il primo elemento di ogni tupla
    print(sectors)

    i = 1
    for sec in sectors:
        print(f"{i}: {sec}\n")
        i += 1

    print(f"Scegli uno o più settori su cui applicare l'agente (indicando i numeri con virgole se più di uno):\n")
    choises = input("Scrivi i numeri: ")

    choises = choises.split(',')
    choises = [int(x) for x in choises]
    print(choises)

    sectors = [sectors[i-1] for i in choises]
    print(sectors)

    main(sectors)

