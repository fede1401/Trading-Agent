import MetaTrader5 as mt5
from datetime import datetime
import session_management
import logging
import math

# Ottiene il prezzo di mercato corrente per un simbolo specificato.
def getCurrentMarketPrice(symbol):
    current_market_price = mt5.symbol_info_tick(symbol).ask
    print(f"\n\nPrezzo di mercato corrente {symbol}: {current_market_price}\n\n")
    
    return current_market_price


# Controlla la disponibilità di un simbolo nel Market Watch di MetaTrader 5 e lo aggiunge se non è visibile.
def checkSymbol(symbol):
    # Ottiene i dati di uno specifico simbolo azionario
    symbol_info = mt5.symbol_info(symbol)
    
    # Se i dati di un simbolo azionario sono nulli esci dal programma
    if symbol_info is None:
        print(symbol, "not found, can't call order_check()")  
        session_management.closeConnection()
        quit()


    # Se il simbolo non è visibile nel Market Watch, lo aggiunge
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        
        # Prova ad aggiungere il simbolo al Market Watch
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, exit",symbol)
            session_management.closeConnection()
            quit()

    return symbol_info


# Esegue un'azione di acquisto per il simbolo specificato.
def buy_action(symbol):
    # Ottiene i dati di uno specifico simbolo azionario
    symbol_info = checkSymbol(symbol)

    # Ottiene la valuta dell'account
    account_currency=mt5.account_info().currency
    print("Account currency:",account_currency)

    # Ottiene il prezzo attuale di acquisto del simbolo
    tick_info = mt5.symbol_info_tick(symbol)

    # Se non è possibile ottenere le informazioni di tick, esci dal programma
    if tick_info is None:
        logging.error(f"Errore nel recupero delle informazioni di tick per {symbol}.")
        return None
    
    price = tick_info.ask

    # Calcola il volume minimo e il passo di volume
    min_volume = symbol_info.volume_min
    volume_step = symbol_info.volume_step
    volume = min_volume

    print(f"min_volume: {min_volume}, volume_step:{volume_step}, vol: {volume}\n")

    # Creazione dell'ordine
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Invia la richiesta di trading
    result = mt5.order_send(request)

    logging.info(f"Result: {result}")

    # Controlla il risultato dell'esecuzione dell'ordine    
    checkEsecutionOrder(symbol_info=symbol_info, price=price, result=result, request=request)
    return result


# Esegue un acquisto di un certo numero di azioni di un titolo azionario.
def buy_actions_of_title(symbol):
    # Ottiene i dati di uno specifico simbolo azionario
    symbol_info = checkSymbol(symbol)

    # Ottiene la valuta dell'account
    account_currency=mt5.account_info().currency
    print("Account currency:",account_currency)

    # Ottiene il prezzo attuale di acquisto del simbolo
    tick_info = mt5.symbol_info_tick(symbol)

    # Se non è possibile ottenere le informazioni di tick, esci dal programma
    if tick_info is None:
        logging.error(f"Errore nel recupero delle informazioni di tick per {symbol}.")
        return None
    
    price = tick_info.ask
    
    if price > 1000:
        return None

    # Calcola il volume minimo e il passo di volume
    min_volume = symbol_info.volume_min
    volume_step = symbol_info.volume_step
    
    volume = float(math.floor(1000 / price))
    logging.info(f"\n volume:{volume}\n")
    #if volume > volume_step:
    #    volume = volume_step

    print(f"min_volume: {min_volume}, volume_step:{volume_step}, vol: {volume}\n")

    # Creazione dell'ordine
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Invia la richiesta di trading
    result = mt5.order_send(request)

    logging.info(f"Result: {result}")

    # Controlla il risultato dell'esecuzione dell'ordine    
    checkEsecutionOrder(symbol_info=symbol_info, price=price, result=result, request=request)
    return result



# Esegue un'azione di acquisto con specificazione di stop loss e take profit.
def buyAction_PercProfit(symbol, profit_loss_rate):
    symbol_info = checkSymbol(symbol)

    # Ottieni la valuta dell'account
    account_currency=mt5.account_info().currency
    print("Account currency:",account_currency)

    # Ottieni il prezzo di acquisto corrente del simbolo
    price = mt5.symbol_info_tick(symbol).ask

    # calcolo dello stop loss e takeProfit:
    profit = price * profit_loss_rate

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
        "symbol": symbol,
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


# Chiude una posizione aperta per un simbolo specificato.
def close_Position(symbol, position):    
    # Verifica se la posizione è vuota
    if position is None or len(position) == 0:
        print(f"No positions found for {symbol}")
        return
    
    # Assumiamo che ci sia solo una posizione aperta per il simbolo
    position_ticket = position.ticket
    position_type = position.type
    volume = position.volume

    # Ottieni il prezzo corrente per il simbolo
    price = mt5.symbol_info_tick(symbol).bid if position_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask

    # Creazione dell'ordine opposto per chiudere la posizione
    order_type = mt5.ORDER_TYPE_SELL if position_type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "position": position_ticket,
        "price": price,
        "deviation": 10,
        "magic": 234000,
        "comment": "python script close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Invia la richiesta di trading
    result = mt5.order_send(request)

    # Verifica il risultato dell'esecuzione dell'ordine
    checkEsecutionOrder(symbol_info=symbol, price=price, result=result, request=request)
    return result.order


# Esegue un'azione di vendita per un simbolo specificato.
def sell_Action(symbol):
    symbol_info = checkSymbol(symbol)

    # get account currency
    account_currency=mt5.account_info().currency
    print("Account currency:",account_currency)

    # ottenuto prezzo di acquisto corrente del seguente simbolo
    price = mt5.symbol_info_tick(symbol).ask

    # Calcola il volume minimo e il passo di volume
    min_volume = symbol_info.volume_min
    volume_step = symbol_info.volume_step
    volume = min_volume

    print(f"min_volume: {min_volume}, volume_step:{volume_step}, vol: {volume}\n")

    # Creazione dell'ordine
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
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
    return result.order



def checkEsecutionOrder(symbol_info, price, result, request):
    # Verifica il risultato dell'esecuzione dell'ordine
    print("\n1. order_send(): by {} {}\n\n".format(symbol_info, price))

    # Controlla se l'ordine è stato eseguito correttamente (result.retcode torna il risultato dell'ordine)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order send failed, retcode={result.retcode}")
        
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
    print("2. order_send done, ", result)
    print("   opened position with POSITION_TICKET={}\n".format(result.order))

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


# Verifica la presenza di ordini attivi nell'account.
def checkOrdersTotal():
    # Verifica la presenza di ordini attivi
    orders=mt5.orders_total()
    if orders > 0:
        print("Total orders=",orders)
    else:
        print("Orders not found")
 

# Ottiene e visualizza gli ordini attivi per un simbolo specifico (es. AAPL).
def getActiveOrders():
    # Ottiene e visualizza dati sugli ordini attivi su AAPL
    orders=mt5.orders_get(symbol="AAPL")
    if orders is None:
        print("No orders on AAPL, error code={}".format(mt5.last_error()))
    else:
        print("Total orders on AAPL:",len(orders))
        # Visualizza tutti gli ordini attivi
        for order in orders:
            print(order)
    print()



if __name__ == '__main__':
    session_management.login_metaTrader5(account=session_management.account , password=session_management.password, server=session_management.server)

    #symbol = ["AAPL", "TSLA", "INTC"]
    #for s in symbol:
    #    getCurrentMarketPrice("AAPL")


    symbolBuy = "INTC"
    # voglio un profitto dell'1%
    profit_loss_rate = 0.01


    buyAction_PercProfit(symbolBuy, profit_loss_rate)

    checkOrdersTotal()

    getActiveOrders()

    

