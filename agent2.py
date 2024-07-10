# Ordinamento del 5% delle azioni della borsa Nasdaq per capitalizzazione decrescente (pool)
# Fino ad esaurimento budget si acquistano azioni random dal pool
# Vendesi delle azioni che sono salite del TP% = 1 rispetto al prezzo d'acquisto
# sleep di 15 minuti
 
import MetaTrader5 as mt5
from datetime import datetime
import login, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send,symbolsAcceptedByTickmill, connectDB, accountInfo, insertDataDB, agentState
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
        # connessione al server MetaTrader 5 e login
        login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

        # ottenimento del 5% delle azioni del Nasdaq ordinate per capitalizzazione decrescente.
        pool_Actions_Nasdaq = symbolsAcceptedByTickmill.get5PercentSymbolsCapDesc()

        # Recupera lo stato dell'agente nel database:
        cur.execute("SELECT * FROM DataTrader ORDER BY date DESC LIMIT 1")
        last_state = cur.fetchone()


        if last_state:
            # Se last_state contiene un valore, viene destrutturato in variabili individuali.
            (last_date, stateAgent, initial_budget, budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti) = last_state
            logging.info(f"Ripresa stato dell'agent: {stateAgent}, Budget: {budget}, Profitto totale USD: {profitTotalUSD}, Profitto totale percentuale: {profitTotalPerc}, Budget Mantenimento: {budgetMantenimento}, Budget Investimenti: {budgetInvestimenti}")

            # In questo modo se il programma viene bloccato e rimane nello stato INITIAL può entrare nel While e vedere se ci sono azioni da vendere
            if stateAgent == 'INITIAL' :
                logging.info(f"Cambio di stato da WAIT a SALE")
                stateAgent = agentState.AgentState.SALE

        else:
            # Inizializza lo stato dell'agent se non ci sono dati precedenti
            budget = accountInfo.get_balance_account()
            initial_budget = budget
            budgetInvestimenti = budget

            budgetMantenimento = 0
            profitTotalUSD = 0
            profitTotalPerc = 0

            stateAgent = agentState.AgentState.INITIAL
            
            insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
            logging.info(f"Budget iniziale: {budget}")
            
            stateAgent = agentState.AgentState.SALE

        # Il ciclo principale esegue le operazioni di trading basandosi sull'orario di apertura della borsa Nasdaq (09:30 - 16:00 orario di New York).
        while True:

            start_time_open_nas, end_time_open_nas, current_time, datetime_NY = getCurrentTimeNY()
            
            if start_time_open_nas <= current_time < end_time_open_nas:

                logging.info(f"Orario New York: {datetime_NY.hour}:{datetime_NY.minute}\n")                        
                if stateAgent == 'SALE' :
        
                    # Per tutte le azioni comprate rivendo quelle che sono salite del TP = 1% rispetto al prezzo di acquisto
                    for act in pool_Actions_Nasdaq:

                        # Ottenimento operazioni di trading attualmente in corso tramite simbolo azionario
                        positions = mt5.positions_get(symbol=act)
                        if positions is not None:
                            for pos in positions:
                                        
                                print(pos)
                                        
                                # Ottenimento prezzo di acquisto(open), prezzo corrente, id ticket e volume di azioni acquistate
                                price_open = pos.price_open
                                price_current = pos.price_current
                                ticket = pos.ticket
                                volume = pos.volume

                                if price_current > price_open:

                                    # Calcolo del profitto:
                                    profit = price_current - price_open
                                    perc_profit = profit / price_open

                                    # Rivendita con l'1 % di profitto
                                    if perc_profit > 0.01:
                                        info_order_send.sell_Action(act)

                                        # aggiorno il budget
                                        budgetInvestimenti = budgetInvestimenti + price_open

                                        # per la strategia dell'investitore prudente soltanto il 10% del guadagno lo reinvesto
                                        profit_10Perc = (profit*10)/100
                                        profit_90Perc = (profit*90)/100
                                        budgetInvestimenti = budgetInvestimenti + profit_10Perc
                                        budgetMantenimento = budgetMantenimento + profit_90Perc

                                        insertDataDB.insertInSale(datetime.now(), ticket=ticket, volume=volume, symbol=act, priceSale=price_current, pricePurchase=price_open, profitUSD=profit, profitPerc=perc_profit, cur=cur, conn=conn)    

                                        # Aggiornamento del budget dopo la vendita con inclusi i profitti
                                        budget = accountInfo.get_balance_account() 

                                        profitTotalUSD += profit
                                        profitTotalPerc =  perc_profit

                                        insertDataDB.insertInDataTrader(datetime.now(), stateAgent ,initial_budget,  budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn) 

                                        logging.info(f"Venduta azione {act}, profitto: {profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")


                    logging.info(f"Cambio di stato da SALE a PURCHASE")
                    stateAgent = agentState.AgentState.PURCHASE


                ###### fine SALE

                if stateAgent == 'PURCHASE':

                    # Acquisto di azioni finché c'è budget
                    while budgetInvestimenti > 0:

                        #stateAgent = agentState.AgentState.PURCHASE

                        # scelgo un'azione random dal pool
                        symbolRandom = random.randint(0, len(pool_Actions_Nasdaq)-1)

                        logging.info(f"Simbolo scelto: {pool_Actions_Nasdaq[symbolRandom]}")

                        # compro l'azione corrispondente
                        result = info_order_send.buy_action(pool_Actions_Nasdaq[symbolRandom])

                        if result is not None:
                            logging.info(f"Acquisto completato al prezzo: {result}")
                        else:
                            logging.error("Acquisto fallito.")

                        # aggiorno il budget    
                        #budgetInvestimenti = accountInfo.get_balance_account()
                        price = result.price
                        volume = result.volume
                        ticket = result.order


                        logging.info(f"\nPrice: {price}")

                        insertDataDB.insertInPurchase(datetime.now(), ticket, volume, pool_Actions_Nasdaq[symbolRandom], price, cur, conn)

                        budgetInvestimenti = budgetInvestimenti - price

                        # Aggiornamento del budget dopo l'acquisto dell'azione
                        budget = accountInfo.get_balance_account() 

                        insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget,  budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                        logging.info(f"Acquistata azione {pool_Actions_Nasdaq[symbolRandom]}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")

                    logging.info(f"Cambio di stato da PURCHASE a WAIT")
                    stateAgent = agentState.AgentState.WAIT


                ###### fine PURCHASE

                # Il programma si interrompe per 15 minuti poi riparte
                if stateAgent == 'WAIT':

                    insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)
                    logging.info("Interruzione del programma per 15 minuti.")
                            
                    time_module.sleep(900)

                    logging.info(f"Cambio di stato da WAIT a SALE")
                    stateAgent = agentState.AgentState.SALE

                    
                ###### fine WAIT


            # Se l'orario corrente della zona di New York non corrisponde all'orario di apertura della borsa del Nasdaq, allora:
            else:
                logging.info("Orario non adatto per il trading.")
                
                # Calcolo della pausa per l'apertura della Borsa del Nasdaq

                try:
                    specified_time = time(9, 30)  # Ad esempio, 9:30

                    # Get the timezone object for New York
                    tz_NY = pytz.timezone('America/New_York') 

                    # Get the current time in New York
                    datetime_NY = datetime.now(tz_NY)

                    target_time = tz_NY.localize(datetime.combine(datetime_NY.date(), specified_time))
                    
                    print(target_time)
                    print()

                    # Se l'orario specificato è già passato per oggi, imposta l'orario per il giorno successivo
                    if target_time < datetime_NY:
                        target_time += timedelta(days=1)

                    stateAgent = agentState.AgentState.WAIT
                    insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                    # Il programma si interrompe fino all'apertura della borsa del Nasdaq
                    wait(target_time)

                    stateAgent = agentState.AgentState.SALE

                except Exception as e:
                    print(f"Errore durante l'impostazione dell'orario target: {e}")


        # fine while True:


    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
    
    finally:
        closeConnectionMt5.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")



def wait(target_time):
    try:
        # Get the timezone object for New York
        tz_NY = pytz.timezone('America/New_York') 

        # Get the current time in New York
        datetime_NY = datetime.now(tz_NY)

        sleep_duration = (target_time - datetime_NY).total_seconds()

        print(sleep_duration)

        if sleep_duration > 0:
            print(f"Il programma si interromperà fino a: {target_time}")
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

    logging.info(f"Orario New York: {datetime_NY.hour}:{datetime_NY.minute}")

    # Orario di apertura della borsa Nasdaq a New York: 9:30 - 16:00
    start_time_open_nas = time(9, 30)
    end_time_open_nas = time(16, 0)

    current_time = datetime_NY.time()

    return start_time_open_nas, end_time_open_nas, current_time, datetime_NY



if __name__ == '__main__':
    main()

