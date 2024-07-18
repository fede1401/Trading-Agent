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



def main():
    # configurazione del logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # connessione al database
    cur, conn = connectDB.connect_nasdaq()
    
    try:
        # connessione al server MetaTrader 5 e login e salvataggio nel db per lo storico dei login.
        session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)
        
        # Inserimento dei dati relativi al login nel database
        insertDataDB.insertInLoginDate(session_management.name, session_management.account, session_management.server, cur, conn)

        # ottenimento del 5% delle azioni del Nasdaq ordinate per capitalizzazione decrescente.
        pool_Actions_Nasdaq = symbolsAcceptedByTickmill.get5PercentSymbolsCapDesc()

        # Recupera lo stato dell'agente nel database:
        cur.execute("SELECT * FROM DataTrader ORDER BY date DESC LIMIT 1")
        last_state = cur.fetchone()


        if last_state:
            # Se last_state contiene un valore, viene destrutturato in variabili individuali.
            (last_date, stateAgent, initial_budget, budget, equity, margin, profitTotalUSD, profitTotalPerc, lossTotalUSD, lossTotalPerc, budgetMantenimento, budgetInvestimenti) = last_state
            logging.info(f"Ripresa stato dell'agent: {stateAgent}, Budget: {budget}, Profitto totale USD: {profitTotalUSD}, Profitto totale percentuale: {profitTotalPerc}, Perdita totale USD: {lossTotalUSD}, Perdita totale percentuale: {lossTotalPerc}, Budget Mantenimento: {budgetMantenimento}, Budget Investimenti: {budgetInvestimenti}\n")

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
            
                
        else:
            # Inizializza lo stato dell'agent se non ci sono dati precedenti
            budget = accountInfo.get_balance_account()
            equity = accountInfo.get_equity_account()
            margin = accountInfo.get_margin_account()
            initial_budget = budget
            budgetInvestimenti = budget

            budgetMantenimento = 0
            profitTotalUSD = 0
            profitTotalPerc = 0
            lossTotalUSD = 0
            lossTotalPerc = 0

            stateAgent = agentState.AgentState.INITIAL
            
            insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, lossTotalUSD, lossTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
            logging.info(f"Budget iniziale: {budget}\n")
            
            stateAgent = agentState.AgentState.SALE

        # Il ciclo principale esegue le operazioni di trading basandosi sull'orario di apertura della borsa Nasdaq (09:30 - 16:00 orario di New York), 
        # poiché durante l'orario di chiusura non possono essere effettuate operazioni di acquisto e vendita.

        # Inizializzazione della variabile contentente gli identificatori degli ordini venduti. sales = []
        
        while True:
            # Ritorna un intero corrispondente al giorno della settimana ( 0: Monday, ... , 6: Sunday )
            dayOfWeek = datetime.today().weekday() 
            
            
            # Se il giorno della settimana è sabato o domenica mettiamo in pausa il programma poiché il mercato è chiuso
            if dayOfWeek == 5 or dayOfWeek == 6:
                logging.info(f"Pausa del trading agent poiché è sabato o domenica. {dayOfWeek}\n")
                
                # Il programma si interrompe fino a lunedì
                if dayOfWeek == 5:
                    logging.info("Oggi è sabato, il programma si interrompe fino a lunedi.\n")
                    
                    # Calcola il tempo attuale
                    now = datetime.now()
                    
                    # Calcola il tempo alla mezzanotte dei 2 giorni successivo
                    next_day = now + timedelta(days=2)
                    next_midnight = datetime(year=next_day.year, month=next_day.month, day=next_day.day)
                    
                    # Calcola la durata in secondi da adesso fino alla mezzanotte
                    seconds_until_midnight = (next_midnight - now).total_seconds()
                    logging.info(f"Waiting for {seconds_until_midnight} seconds until next midnight.\n")
                    
                    # Metti in pausa il programma
                    time_module.sleep(seconds_until_midnight)


                if dayOfWeek == 6:
                    logging.info("Oggi è domenica, il programma si interrompe fino a lunedi.\n")

                    # Calcola il tempo attuale
                    now = datetime.now()
                    
                    # Calcola il tempo alla mezzanotte del giorno successivo
                    next_day = now + timedelta(days=1)
                    next_midnight = datetime(year=next_day.year, month=next_day.month, day=next_day.day)
                    
                    # Calcola la durata in secondi da adesso fino alla mezzanotte
                    seconds_until_midnight = (next_midnight - now).total_seconds()
                    logging.info(f"Waiting for {seconds_until_midnight} seconds until next midnight.\n")
                    
                    # Metti in pausa il programma
                    time_module.sleep(seconds_until_midnight)
        

            # Ottenimento dell'orario corrente di New York
            start_time_open_nas, end_time_open_nas, current_time, datetime_NY = getCurrentTimeNY()
            
            if start_time_open_nas <= current_time < end_time_open_nas:

                logging.info(f"Orario New York: {datetime_NY.hour}:{datetime_NY.minute}, adatto per il trading.\n\n")     
                time_module.sleep(1)


                ######################## inizio SALE

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
                                        budgetInvestimenti = budgetInvestimenti + price_open

                                        # per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                                        profit_10Perc = (profit*10)/100
                                        profit_90Perc = (profit*90)/100
                                        budgetInvestimenti = budgetInvestimenti + profit_10Perc
                                        budgetMantenimento = budgetMantenimento + profit_90Perc

                                        insertDataDB.insertInSale(datetime.now(), ticket_pur=ticket, ticket_sale=ticket_sale, volume=volume, symbol=act, priceSale=price_current, pricePurchase=price_open, profitUSD=profit, profitPerc=perc_profit, lossUSD=0, lossPerc=0 ,cur=cur, conn=conn)    

                                        # Aggiornamento del budget dopo la vendita con inclusi i profitti
                                        budget = accountInfo.get_balance_account() 
                                        equity = accountInfo.get_equity_account()
                                        margin = accountInfo.get_margin_account()

                                        profitTotalUSD += profit
                                        profitTotalPerc =  perc_profit

                                        insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, lossTotalUSD, lossTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                                        logging.info(f"Venduta azione {act}, profitto: {profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}\n")
                                        
                                        logging.info("---------------------------------------------------------------------------------\n\n")

                                        #sales.append(pos.ticket)

                                        #logging.info(f"Vendite: {sales}\n")


                                # Se il prezzo corrente è minore del prezzo iniziale di acquisto c'è una qualche perdita                                
                                if price_current < price_open:
                                    
                                    logging.info(f"Price current: {price_current} minore del prezzo di apertura: {price_open}\n")

                                    # Calcolo della perdita
                                    loss = price_open - price_current
                                    perc_loss = loss / price_open

                                    # Rivendita con il 2% di perdita
                                    if perc_loss >= 0.02:

                                        logging.info(f"Si può vendere {act} poiché c'è una perdita del {perc_loss}\n")

                                        #ticket_sale = info_order_send.sell_Action(act)
                                        ticket_sale = info_order_send.close_Position(act, position=pos)

                                        # aggiorno il budget
                                        budgetInvestimenti = budgetInvestimenti + price_current

                                        insertDataDB.insertInSale(datetime.now(), ticket_pur=ticket, ticket_sale=ticket_sale, volume=volume, symbol=act, priceSale=price_current, pricePurchase=price_open, profitUSD=0, profitPerc=0, lossUSD=loss, lossPerc=perc_loss, cur=cur, conn=conn)    

                                        # Aggiornamento del budget dopo la vendita con inclusi i profitti
                                        budget = accountInfo.get_balance_account() 
                                        equity = accountInfo.get_equity_account()
                                        margin = accountInfo.get_margin_account()

                                        lossTotalUSD += loss
                                        lossTotalPerc =  perc_loss

                                        insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, lossTotalUSD, lossTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                                        logging.info(f"Venduta azione {act}, perdita: {loss}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}\n")

                                        #sales.append(pos.ticket)

                                        #logging.info(f"Vendite: {sales}\n")


                    logging.info(f"Cambio di stato da SALE a PURCHASE\n\n")
                    stateAgent = agentState.AgentState.PURCHASE

                ######################## fine SALE




                ######################## inizio PURCHASE

                if stateAgent == agentState.AgentState.PURCHASE :
                    logging.info(f"Agent entrato nello stato Purchase\n")

                    # Acquisto di azioni finché c'è budget
                    while budgetInvestimenti > 0:

                        #stateAgent = agentState.AgentState.PURCHASE

                        # scelgo un'azione random dal pool
                        symbolRandom = random.randint(0, len(pool_Actions_Nasdaq)-1)

                        logging.info(f"Possiamo acquistare perché il budget dell'investimento è > 0: simbolo scelto randomicamente tra il pool delle azioni accettate dal broker TickMill è: {pool_Actions_Nasdaq[symbolRandom]}\n")

                        # compro l'azione corrispondente
                        result = info_order_send.buy_action(pool_Actions_Nasdaq[symbolRandom])

                        if result is not None:
                            logging.info(f"Acquisto completato: {result}\n")
                        else:
                            logging.error("Acquisto fallito.\n")

                        # aggiorno il budget    
                        #budgetInvestimenti = accountInfo.get_balance_account()
                        price = result.price
                        volume = result.volume
                        ticket = result.order


                        logging.info(f"Price: {price}")

                        insertDataDB.insertInPurchase(datetime.now(), ticket, volume, pool_Actions_Nasdaq[symbolRandom], price, cur, conn)

                        budgetInvestimenti = budgetInvestimenti - price

                        # Aggiornamento del budget dopo l'acquisto dell'azione
                        budget = accountInfo.get_balance_account() 
                        equity = accountInfo.get_equity_account()
                        margin = accountInfo.get_margin_account()

                        insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, lossTotalUSD, lossTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                        logging.info(f"Acquistata azione {pool_Actions_Nasdaq[symbolRandom]}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}\n")
                        logging.info("---------------------------------------------------------------------------------\n\n")

                    logging.info(f"Cambio di stato da PURCHASE a WAIT\n\n")
                    stateAgent = agentState.AgentState.WAIT


                ######################## fine PURCHASE


                ######################## inizio WAIT

                # Il programma si interrompe per 15 minuti poi riparte
                if stateAgent == agentState.AgentState.WAIT :
                    logging.info(f"Agent entrato nello stato Wait\n")

                    insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, lossTotalUSD, lossTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                    logging.info("Interruzione del programma per 15 minuti.\n")
                            
                    time_module.sleep(900)

                    logging.info(f"Cambio di stato da WAIT a SALE\n\n")
                    stateAgent = agentState.AgentState.SALE
                    
                ######################## fine WAIT


            # Se l'orario corrente della zona di New York non corrisponde all'orario di apertura della borsa del Nasdaq, allora:
            else:
                logging.info("Orario non adatto per il trading.\n")
                
                # Calcolo della pausa per l'apertura della Borsa del Nasdaq

                try:
                    specified_time = time(9, 35)  # Ad esempio, 9:35 , poiché ho notato che alcune volte il mercato apre più tardi

                    # Get the timezone object for New York
                    tz_NY = pytz.timezone('America/New_York') 

                    # Get the current time in New York
                    datetime_NY = datetime.now(tz_NY)

                    target_time = tz_NY.localize(datetime.combine(datetime_NY.date(), specified_time))
                    
                    #print(target_time)
                    #print()

                    # Se l'orario specificato è già passato per oggi, imposta l'orario per il giorno successivo
                    if target_time < datetime_NY:
                        target_time += timedelta(days=1)

                    stateAgent = agentState.AgentState.WAIT
                    insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, equity, margin ,profitTotalUSD, profitTotalPerc, lossTotalUSD, lossTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                    # Il programma si interrompe fino all'apertura della borsa del Nasdaq
                    wait(target_time)

                    stateAgent = agentState.AgentState.SALE

                except Exception as e:
                    print(f"Errore durante l'impostazione dell'orario target: {e}")


        # fine while True:


    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
    
    finally:
        session_management.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")



def wait(target_time):
    try:
        # Get the timezone object for New York
        tz_NY = pytz.timezone('America/New_York') 

        # Get the current time in New York
        datetime_NY = datetime.now(tz_NY)

        sleep_duration = (target_time - datetime_NY).total_seconds()

        # print(sleep_duration)

        if sleep_duration > 0:
            logging.info(f"Il programma si interromperà fino a: {target_time}, con una pausa di {sleep_duration} secondi.")
            time_module.sleep(sleep_duration)
            print("Il programma ha ripreso l'esecuzione.")
        else:
            print("Il tempo target è già passato.")
    except Exception as e:
        print(f"Errore durante l'attesa: {e}")



def getCurrentTimeNY():
    # Get the timezone object for New York
    tz_NY = pytz.timezone('America/New_York') 

    # Get the current time in New York
    datetime_NY = datetime.now(tz_NY)

    #logging.info(f"Orario New York: {datetime_NY.hour}:{datetime_NY.minute}")

    # Orario di apertura della borsa Nasdaq a New York: 9:35 - 16:00. Ho notato che il mercato apre più tardi
    start_time_open_nas = time(9, 35)
    end_time_open_nas = time(16, 0)

    current_time = datetime_NY.time()

    return start_time_open_nas, end_time_open_nas, current_time, datetime_NY



if __name__ == '__main__':
    main()

