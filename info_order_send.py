import MetaTrader5 as mt5
from datetime import datetime
import login_mt5, closeConnectionMt5, variableLocal


def getCurrentMarketPrice(symbol):
    print(f"\n\nPrezzo di mercato corrente {s}: {mt5.symbol_info_tick(s).ask}\n\n")



def checkSymbol(symbol):
    symbol_info = mt5.symbol_info(symbol)
    
    if symbol_info is None:
        print(symbolBuy, "not found, can't call order_check()")  
        closeConnectionMt5.closeConnection()
        quit()


    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, exit",symbol)
            closeConnectionMt5.closeConnection()
            quit()


    return symbol_info


"""
Cosa Succede Quando il Prezzo Raggiunge lo Stop Loss o il Take Profit

    Stop Loss: Se il prezzo di AAPL scende fino al livello dello stop loss (stopLoss), 
    la posizione viene chiusa automaticamente da MetaTrader 5, vendendo le azioni a quel prezzo per limitare la perdita.

    Take Profit: Se il prezzo di AAPL sale fino al livello del take profit (takeProfit), 
    la posizione viene chiusa automaticamente da MetaTrader 5, vendendo le azioni a quel prezzo per bloccare il profitto.


Ogni broker ha specifiche regole e limiti riguardanti i volumi minimi e massimi che possono essere negoziati in una singola operazione. 
Ecco alcuni dettagli importanti da considerare:

    Volume Minimo: È la quantità minima di asset che è possibile negoziare in una singola operazione. 
    Se tenti di negoziare un volume inferiore a questo, l'ordine sarà rifiutato.
     Ad esempio, se il volume minimo per un'azione è 1, non puoi acquistare meno di una singola azione.

    Passo di Volume (Volume Step): È l'incremento minimo di volume con cui è possibile aumentare l'ordine.
    Ad esempio, se il passo di volume è 0.1, puoi negoziare 1.0, 1.1, 1.2, ecc., ma non 1.05.
    Ad esempio, se il volume step è 0.01, puoi aumentare il volume in incrementi di 0.01 (ad esempio, 1.01, 1.02, ecc.).
    

    Volume Massimo: È la quantità massima di asset che è possibile negoziare in una singola operazione. 
    Questo è importante per evitare di piazzare ordini troppo grandi che potrebbero essere rifiutati.
    Ad esempio, se il volume massimo per un'azione è 1000, non puoi acquistare più di 1000 azioni in una singola operazione.
"""


def buyAction_PercProfit(symbol, profit_want):
    symbol_info = checkSymbol(symbol)

    # get account currency
    account_currency=mt5.account_info().currency
    print("Account currency:",account_currency)

    # prepare the buy request structure
    price = mt5.symbol_info_tick(symbol).ask

    # calcolo dello stop loss e takeProfit:
    profit = price * profit_want

    stopLoss = price - profit
    takeProfit = price + profit

    print(f"\nprice: {price}, profit: {profit}, stopLoss: {stopLoss}, takeProfit: {takeProfit}\n\n")

    # Calcola il prezzo di take profit
    # tp = price * (1 + profit)
    # sl = price * (1 - profit)


    # Calcola il volume minimo e il passo di volume
    min_volume = symbol_info.volume_min
    volume_step = symbol_info.volume_step
    volume = min_volume


    print(f"min_volume: {min_volume}, volume_step:{volume_step}, vol: {volume}\n")


    # Creazione dell'ordine
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbolBuy,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": stopLoss,
        "tp": takeProfit,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }


    # send a trading request
    result = mt5.order_send(request)

    # check the execution result
    checkEsecutionOrder(symbol_info=symbol_info, price=price, result=result, request=request)
    return 



def checkEsecutionOrder(symbol_info, price, result, request):
    # Verifica il risultato dell'esecuzione dell'ordine
    print("1. order_send(): by {} {}\n\n".format(symbol_info, price))

    # Controlla se l'ordine è stato eseguito correttamente (result.retcode torna il risultato dell'ordine)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("2. order_send failed, retcode={}".format(result.retcode))
        
        # Mostra i dettagli del risultato dell'ordine in caso di fallimento:
            # converti il risultato in un dizionario e mostra ogni campo
        result_dict = result._asdict()
        for field in result_dict.keys():
            print("   {}={}".format(field, result_dict[field]))
            
            # Se il campo è una struttura di richiesta di trading, mostra ogni suo elemento
            if field == "request":
                traderequest_dict = result_dict[field]._asdict()
                for tradereq_field in traderequest_dict:
                    print("       traderequest: {}={}".format(tradereq_field, traderequest_dict[tradereq_field]))
        
        print("shutdown() and quit")
        # Termina la connessione e chiude il programma in caso di fallimento
        mt5.shutdown()
        quit()
        
    # Mostra il risultato dell'ordine se è stato eseguito correttamente
    print("\n\n2. order_send done, ", result)
    print("   opened position with POSITION_TICKET={}\n\n".format(result.order))

    print("3. order_check()")

    # Esegui il controllo dell'ordine e mostra il risultato
    result = mt5.order_check(request)
    print(result)

    # Converti il risultato del controllo in un dizionario e mostra ogni campo
    result_dict = result._asdict()
    for field in result_dict.keys():
        print("   {}={}".format(field, result_dict[field]))
        
        # Se il campo è una struttura di richiesta di trading, mostra ogni suo elemento
        if field == "request":
            traderequest_dict = result_dict[field]._asdict()
            for tradereq_field in traderequest_dict:
                print("       traderequest: {}={}".format(tradereq_field, traderequest_dict[tradereq_field]))
    
    return 


def checkOrdersTotal():
    # check the presence of active orders
    orders=mt5.orders_total()
    if orders>0:
        print("Total orders=",orders)
    else:
        print("Orders not found")
 


def getActiveOrders():
    # display data on active orders on GBPUSD
    orders=mt5.orders_get(symbol="AAPL")
    if orders is None:
        print("No orders on AAPL, error code={}".format(mt5.last_error()))
    else:
        print("Total orders on AAPL:",len(orders))
        # display all active orders
        for order in orders:
            print(order)
    print()



if __name__ == '__main__':
    login_mt5.login_metaTrader5(account=variableLocal.account , password=variableLocal.password, server=variableLocal.server)

    #symbol = ["AAPL", "TSLA", "INTC"]
    #for s in symbol:
    #    getCurrentMarketPrice("AAPL")


    symbolBuy = "TSLA"
    # voglio un profitto dell'1%
    profit_want = 0.01


    buyAction_PercProfit(symbolBuy, profit_want)

    checkOrdersTotal()

    getActiveOrders()

    

