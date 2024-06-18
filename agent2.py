# Ordinamento del 5% delle azioni della borsa Nasdaq per capitalizzazione decrescente (pool)
# Fino ad esaurimento budget si acquistano azioni random dal pool
# Vendesi delle azioni che sono salite del TP% = 1 rispetto al prezzo d'acquisto
# sleep di 15 minuti
 
import MetaTrader5 as mt5
from datetime import datetime
import login, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send,symbolsAcceptedByTickmill, connectDB, accountInfo, insertDataDB
import psycopg2
import time
import random
import logging


pool_Actions_Nasdaq = symbolsAcceptedByTickmill.get5PercentSymbolsCapDesc()


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    curr, conn = connectDB.connect_nasdaq()
    
    try:
        login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)
        
        budget = accountInfo.get_balance_account()
        initial_budget = budget
        budgetInvestimenti = budget
        budgetMantenimento = 0
        logging.info(f"Budget iniziale: {budget}")

        profitTotalUSD = 0
        profitTotalPerc = 0

        insertDataDB.insertInDataTrader(datetime.now(), budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti)        

        while True:
            # per tutte le azioni comprate rivendo quelle che sono salite del TP = 1% rispetto al prezzo di acquisto
            for act in pool_Actions_Nasdaq:
                positions = mt5.positions_get(symbol=act)
                if positions is not None:
                    for pos in positions:
                        price_open = pos['price_open']
                        price_current = pos['price_current']

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

                                insertDataDB.insertInSale(datetime.now(), symbol=act, priceSale=price_current, pricePurchase=price_open, profitUSD=profit, profitPerc=perc_profit )

                                budget = accountInfo.get_balance_account() ## guadagno che comprende i profitti

                                profitTotalUSD += profit
                                profitTotalPerc =  perc_profit

                                insertDataDB.insertInDataTrader(datetime.now(), budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti)        


                                logging.info(f"Venduta azione {act}, profitto: {profit}, budgetInvestimenti: {budgetInvestimenti}, budgetMantenimento: {budgetMantenimento}")


            # Acquisto di azioni finché c'è budget
            while budgetInvestimenti > 0:
                # scelgo un'azione random dal pool
                symbolRandom = random.randint(0, len(pool_Actions_Nasdaq)-1)

                # compro l'azione corrispondente
                info_order_send.buy_action(pool_Actions_Nasdaq[symbolRandom])

                # aggiorno il budget    
                #budgetInvestimenti = accountInfo.get_balance_account()
                price = mt5.symbol_info_tick(symbolRandom).ask

                insertDataDB.insertInPurchase(datetime.now(), pool_Actions_Nasdaq[symbolRandom], price)

                budgetInvestimenti = budgetInvestimenti - price
                
                budget = accountInfo.get_balance_account() 

                insertDataDB.insertInDataTrader(datetime.now(), budget, profitTotalUSD, profitTotalPerc, budgetMantenimento, budgetInvestimenti)

                logging.info(f"Acquistata azione {pool_Actions_Nasdaq[symbolRandom]}, prezzo: {price}, budgetInvestimenti: {budgetInvestimenti}")


            # il programma si interrompe per 15 minuti poi riparte
            logging.info("Interruzione per 15 minuti.")
            time.sleep(900)

    except Exception as e:
        logging.critical(f"Errore non gestito: {e}")
    
    finally:
        closeConnectionMt5.closeConnection()
        logging.info("Connessione chiusa e fine del trading agent.")





if __name__ == '__main__':
    main()

