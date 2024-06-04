# Ordinamento del 5% delle azioni della borsa Nasdaq per capitalizzazione decrescente (pool)
# Fino ad esaurimento budget si acquistano azioni random dal pool
# Vendesi delle azioni che sono salite del TP% = 1 rispetto al prezzo d'acquisto
# sleep di 15 minuti
 
import MetaTrader5 as mt5
from datetime import datetime
import login_mt5, closeConnectionMt5, variableLocal, downloadAndInsertDataDB, info_order_send, accountInfo
import psycopg2
import time
import random


pool_Actions_Nasdaq = ['MSFT', 'AAPL', 'NVDA', 'GOOGL', 'AMZN', 'META', 'AVGO', 'TSLA', 'COST', 'NFLX', 
                       'AMD', 'AZN', 'PEP', 'QCOM', 'TMUS', 'PDD', 'ADBE', 'CSCO', 'AMAT', 'AMGN', 'CMCSA', 
                       'ISRG', 'MU', 'INTC', 'BKNG', 'LRCX', 'VRTX']


def main():
    login_mt5.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

    budget = accountInfo.get_balance_account()
    #print(budget)


    while(1):
        # per tutte le azioni comprate rivendo quelle che sono salite del TP = 1% rispetto al prezzo di acquisto
        for act in pool_Actions_Nasdaq:
            position = mt5.positions_get(symbol=act)
            if position is not None:
                for pos in position:
                    price_open = pos['price_open']
                    price_current = pos['price_current']

                    if price_current > price_open:

                        # calcolo del profitto:
                        profit = price_current - price_open
                        perc_profit = profit / price_open

                        if perc_profit > 0.01:
                            info_order_send.sell_Action(act)
        

        # finchè ho budget compro azioni random dal pool
        while (budget>0):

            # scelgo un'azione random dal pool
            symbolRandom = random.randint(0, len(pool_Actions_Nasdaq)-1)

            # compro l'azione corrispondente
            info_order_send.buy_action(pool_Actions_Nasdaq[symbolRandom])

            # aggiorno il budget    
            budget = accountInfo.get_balance_account()

        

        # il programma si interrompe per 15 minuti poi riparte
        time.sleep(900)


    closeConnectionMt5.closeConnection()
    return





if __name__ == '__main__':
    main()

