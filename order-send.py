import MetaTrader5 as mt5
from datetime import datetime
import login_mt5, closeConnectionMt5, variableLocal


symbol = "NFLX"
single_budget = 20 # budget per singolo acquisto
number_of_trades = 10 # numero acquisti



def send_order(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can't call order_check()")
        mt5.shutdown()
        quit()
    
    # Ottieni il prezzo di acquisto (ask)
    price = symbol_info.ask

    # Ottieni il volume minimo e il passo di volume
    min_volume = symbol_info.volume_min
    volume_step = symbol_info.volume_step

    print("Prezzo di acquisto:", price)
    print("Volume minimo:", min_volume)
    print("Passo di volume:", volume_step)

    for _ in range(number_of_trades):
        # Calcola il volume per il budget singolo
        volume = single_budget / price
        
        # Arrotonda il volume al passo di volume più vicino
        volume = max(min_volume, round(volume / volume_step) * volume_step)
        
        place_order(symbol=symbol, volume=volume, price=price)


def place_order(symbol, volume, price):
    # Creazione dell'ordine
    order = {
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

    # Invia ordine
    result = mt5.order_send(order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Ordine non eseguito, retcode={}".format(result.retcode))
        # Visualizza i dettagli dell'errore
        print("  retcode: ", result.retcode)
        print("  comment: ", result.comment)
    else:
        print("Ordine eseguito, ", result)
        # Visualizza i dettagli dell'ordine
        print("  Order: ", result.order)
        print("  Volume: ", result.volume)


if __name__ == '__main__':
    login_mt5.login_metaTrader5(variableLocal.account, variableLocal.password, variableLocal.server)
    
    send_order(symbol)
    
    closeConnectionMt5.closeConnection()