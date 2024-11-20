import yfinance as yf

# Scarica un esempio di dati per il NYSE
nyse_data = yf.Ticker("^NYA")  # Indice NYSE Composite


print(nyse_data.info)
