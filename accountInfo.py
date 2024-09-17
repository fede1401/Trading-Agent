import MetaTrader5 as mt5
from datetime import datetime
import session_management, info_order_send
import psycopg2
import time
import random


def get_account_info():

    # Ottieni informazioni sul conto
    account_info = mt5.account_info()

    if account_info is not None:
        print(f"Balance: {account_info.balance}")
        print(f"Equity: {account_info.equity}")
        print(f"Margin: {account_info.margin}")
        print(f"Free Margin: {account_info.margin_free}")
        print(f"Margin Level: {account_info.margin_level}%")
    else:
        print("Failed to get account information")
    
    return account_info


def get_balance_account():

    # Ottenimento informazioni sul conto 
    account_info = mt5.account_info()
    balance = account_info.balance
    print(f"Balance: {balance}")

    return balance


def get_equity_account():

    # Ottenimento informazioni sul conto 
    account_info = mt5.account_info()
    equity = account_info.equity
    print(f"Equity: {equity}")

    return equity


def get_margin_account():

    # Ottenimento informazioni sul conto 
    account_info = mt5.account_info()
    margin = account_info.margin
    print(f"Margin: {margin}")

    return margin



if __name__ == '__main__':
    session_management.login_metaTrader5(account=session_management.account, password=session_management.password, server=session_management.server)
    #get_account_info()
    #get_balance_account()
    get_account_info()
    #main()

