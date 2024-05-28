import MetaTrader5 as mt5
from datetime import datetime


# Specificare il simbolo dell'azione (ad esempio, 'AAPL' per Apple)
#symbol = "AAPL"

# Specificare il timeframe (ad esempio, mt5.TIMEFRAME_D1 per dati giornalieri)
#timeframe = mt5.TIMEFRAME_D1

# Specificare l'intervallo di tempo
#start_date = datetime(2024, 5, 20)
#end_date = datetime.now()

############ Ottenimento dati e scrittura su file esterno ###################
def downloadData(symbol, timeframe, start_date, end_date, file ):
    # Ottenere i dati storici
    rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)

    with open('data.txt', 'a') as file1:
        file1.write(f"\n\n{symbol}: \n\n{datetime.now()}\n")

    # Controllare se abbiamo ottenuto i dati
    if rates is None:
        print("No data retrieved")
    else:
        count = 0
        for rate in rates:
            print(rate)
            count += 1
            with open(file, 'a') as file1:
                file1.write(f"{count }: {str(rate)}")
                file1.write('\n')

    return True

