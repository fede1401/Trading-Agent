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




def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    cur, conn = connectDB.connect_nasdaq()
    
    try:
        login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

        pool_Actions_Nasdaq = symbolsAcceptedByTickmill.get5PercentSymbolsCapDesc()
        
        budget = accountInfo.get_balance_account()
        initial_budget = budget
        budgetInvestimenti = budget
        budgetMantenimento = 0

        logging.info(f"Budget iniziale: {budget}")

        profitTotalUSD = 0
        profitTotalPerc = 0

        stateAgent = agentState.AgentState.WAIT

        insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget, budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)        

        while True:

            stateAgent = agentState.AgentState.SALE

            # per tutte le azioni comprate rivendo quelle che sono salite del TP = 1% rispetto al prezzo di acquisto
            for act in pool_Actions_Nasdaq:
                positions = mt5.positions_get(symbol=act)
                if positions is not None:
                    for pos in positions:
                        print(pos)
                        #price_open = pos['price_open']
                        #price_current = pos['price_current']
                        price_open = pos.price_open
                        price_current = pos.price_current
                        ticket = pos.ticket
                        volume = pos.volume

                        if price_current > price_open:

                            # calcolo del profitto:
                            profit = price_current - price_open
                            perc_profit = profit / price_open

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

                                budget = accountInfo.get_balance_account() ## guadagno che comprende i profitti

                                profitTotalUSD += profit
                                profitTotalPerc =  perc_profit

                                insertDataDB.insertInDataTrader(datetime.now(), stateAgent ,initial_budget,  budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn) 


                                logging.info(f"Venduta azione {act}, profitto: {profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")


            # Acquisto di azioni finché c'è budget
            while budgetInvestimenti > 0:

                stateAgent = agentState.AgentState.PURCHASE

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
                
                budget = accountInfo.get_balance_account() 

                insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget,  budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)

                logging.info(f"Acquistata azione {pool_Actions_Nasdaq[symbolRandom]}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")


            # il programma si interrompe per 15 minuti poi riparte
            stateAgent = agentState.AgentState.WAIT

            logging.info("Interruzione per 15 minuti.")
            time.sleep(900)

            insertDataDB.insertInDataTrader(datetime.now(), stateAgent, initial_budget,  budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti, cur, conn)


    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
    
    finally:
        closeConnectionMt5.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")





if __name__ == '__main__':
    main()

