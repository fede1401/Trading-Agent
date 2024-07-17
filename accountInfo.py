import MetaTrader5 as mt5
from datetime import datetime
import login, closeConnectionMt5, variableLocal, info_order_send
import psycopg2
import time
import random


def get_account_info():
    login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

    account_info_dict = mt5.account_info()._asdict()
    for prop in account_info_dict:
        print(f"{prop}: {account_info_dict[prop]}")
    print()

    return account_info_dict


def get_balance_account():
    login.login_metaTrader5(account=variableLocal.account, password=variableLocal.password, server=variableLocal.server)

    account_info_dict = mt5.account_info()._asdict()
    for prop in account_info_dict:
        if prop == 'balance':
            balance = account_info_dict[prop]
            print(f"{prop}: {balance}")

    return balance
         


if __name__ == '__main__':
    #get_account_info()
    get_balance_account()
    #main()

