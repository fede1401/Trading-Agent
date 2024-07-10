
-- database already exists

\c :dbname 


CREATE TABLE IF NOT EXISTS nasdaq_actions (
    symbol VARCHAR (50) NOT NULL,
    time_frame VARCHAR (50) NOT NULL,
    time_value TIMESTAMP NOT NULL,		      -- time of reading YYYY-MM-DD hh-mm-ss
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    tick_volume BIGINT,
    spread INTEGER, 
    real_volume BIGINT,
    PRIMARY KEY(symbol, time_value, time_frame)
);


CREATE TABLE IF NOT EXISTS  Purchase (
    date TIMESTAMP NOT NULL,
    ticket VARCHAR(100) NOT NULL,
    volume INTEGER NOT NULL,
    symbol VARCHAR (10) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(date, symbol)
);


CREATE TABLE IF NOT EXISTS  Sale (
    date TIMESTAMP NOT NULL,
    ticket VARCHAR(100) NOT NULL,
    volume INTEGER NOT NULL,
    symbol VARCHAR (10) NOT NULL,
    priceSale DOUBLE PRECISION NOT NULL,
    pricePurchase  DOUBLE PRECISION NOT NULL,
    profitUSD DOUBLE PRECISION NOT NULL,
    profitPerc  DOUBLE PRECISION NOT NULL,
    --time_for_profit  DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(date, symbol)
);


CREATE TYPE stateAgent AS ENUM ('INITIAL', 'PURCHASE', 'SALE', 'WAIT');



CREATE TABLE IF NOT EXISTS  DataTrader (
    date TIMESTAMP NOT NULL,
    stAgent stateAgent,
    initialBalance DOUBLE PRECISION NOT NULL,
    balance DOUBLE PRECISION NOT NULL,
    profitUSD DOUBLE PRECISION NOT NULL,
    profitPerc DOUBLE PRECISION NOT NULL,
    deposit DOUBLE PRECISION NOT NULL,     -- per il valore dei guadagni di mantenimento
    credit  DOUBLE PRECISION NOT NULL,  -- per il valore dei soldi da investire
    PRIMARY KEY(date) 
);
