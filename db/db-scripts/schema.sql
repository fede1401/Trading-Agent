
-- database already exists

\c :dbname 


CREATE TABLE IF NOT EXISTS loginDate(
    date TIMESTAMP NOT NULL,
    nameSurname VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL,
    serverr VARCHAR(50) NOT NULL,
    PRIMARY KEY(date, username)
);


CREATE TABLE IF NOT EXISTS nasdaq_actions (
    symbol VARCHAR (50) NOT NULL,
    time_frame VARCHAR (50) NOT NULL,
    time_value_IT TIMESTAMP NOT NULL,		      -- time of reading YYYY-MM-DD hh-mm-ss
    time_value_NY TIMESTAMP NOT NULL,              -- time of reading YYYY-MM-DD hh-mm-ss
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    tick_volume BIGINT,
    spread INTEGER, 
    real_volume BIGINT,
    PRIMARY KEY(symbol, time_value_IT, time_value_NY, time_frame)
);


CREATE TABLE IF NOT EXISTS nyse_actions (
    symbol VARCHAR (50) NOT NULL,
    time_frame VARCHAR (50) NOT NULL,
    time_value_IT TIMESTAMP NOT NULL,		      -- time of reading YYYY-MM-DD hh-mm-ss
    time_value_NY TIMESTAMP NOT NULL,              -- time of reading YYYY-MM-DD hh-mm-ss
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    tick_volume BIGINT,
    spread INTEGER, 
    real_volume BIGINT,
    PRIMARY KEY(symbol, time_value_IT, time_value_NY, time_frame)
);

CREATE TABLE IF NOT EXISTS larg_comp_eu_actions (
    symbol VARCHAR (50) NOT NULL,
    time_frame VARCHAR (50) NOT NULL,
    time_value_IT TIMESTAMP NOT NULL,		      -- time of reading YYYY-MM-DD hh-mm-ss
    time_value_NY TIMESTAMP NOT NULL,              -- time of reading YYYY-MM-DD hh-mm-ss
    open_price DOUBLE PRECISION,
    high_price DOUBLE PRECISION,
    low_price DOUBLE PRECISION,
    close_price DOUBLE PRECISION,
    tick_volume BIGINT,
    spread INTEGER, 
    real_volume BIGINT,
    PRIMARY KEY(symbol, time_value_IT, time_value_NY, time_frame)
);


CREATE TABLE IF NOT EXISTS  Purchase (
    datePur TIMESTAMP NOT NULL,
    now TIMESTAMP NOT NULL,
    ticket VARCHAR(100) NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    symbol VARCHAR (10) NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(datePur, now, symbol)
);


CREATE TABLE IF NOT EXISTS  Sale (
    dateSal TIMESTAMP NOT NULL,
    datePur TIMESTAMP NOT NULL,
    now TIMESTAMP NOT NULL,
    ticket_pur VARCHAR(100) NOT NULL,
    ticket_sale VARCHAR(100) NOT NULL,
    volume DOUBLE PRECISION NOT NULL,
    symbol VARCHAR (10) NOT NULL,
    priceSale DOUBLE PRECISION NOT NULL,
    pricePurchase  DOUBLE PRECISION NOT NULL,
    profit_USD DOUBLE PRECISION NOT NULL,
    profit_Perc  DOUBLE PRECISION NOT NULL,
    PRIMARY KEY(dateSal, now, symbol)
);


CREATE TYPE stateAgent AS ENUM ('INITIAL', 'PURCHASE', 'SALE', 'WAIT', 'SALE_IMMEDIATE');



CREATE TABLE IF NOT EXISTS  DataTrader (
    date TIMESTAMP NOT NULL,
    now TIMESTAMP NOT NULL,
    stAgent stateAgent,
    initialBalance DOUBLE PRECISION NOT NULL,
    balance DOUBLE PRECISION NOT NULL,
    equity DOUBLE PRECISION NOT NULL,      -- balance che include profitti e perdite delle posizioni aperte
    margin DOUBLE PRECISION NOT NULL,      -- denaro "bloccato" nel conto come garanzia per l'apertura di una posizione 
    profitUSD DOUBLE PRECISION NOT NULL,
    profitPerc DOUBLE PRECISION NOT NULL,
    deposit DOUBLE PRECISION NOT NULL,     -- per il valore dei guadagni di mantenimento
    credit  DOUBLE PRECISION NOT NULL     -- per il valore dei soldi da investire (freee Margin in mt5.)
);


CREATE TABLE IF NOT EXISTS SectorNasdaq (
    nome VARCHAR (50) NOT NULL,
    PRIMARY KEY(nome)
);

CREATE TABLE IF NOT EXISTS SectorNyse (
    nome VARCHAR (50) NOT NULL,
    PRIMARY KEY(nome)
);


CREATE TABLE IF NOT EXISTS Testing (
    id INTEGER NOT NULL,
    agent VARCHAR (50) NOT NULL,
    numberTest INTEGER,
    initial_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    profitPerc DOUBLE PRECISION NOT NULL,
    profitUSD DOUBLE PRECISION NOT NULL,
    market VARCHAR (50) NOT NULL,
    nPurchase INTEGER NOT NULL,
    nSale INTEGER NOT NULL,
    middleTimeSaleSecond DOUBLE PRECISION NOT NULL,
    middleTimeSaleDay DOUBLE PRECISION NOT NULL,
    titleBetterProfit VARCHAR (50) NOT NULL,
    titleWorseProfit VARCHAR (50) NOT NULL,
    notes VARCHAR (1000)
);



CREATE TABLE IF NOT EXISTS MiddleProfit (
    testId INTEGER NOT NULL,
    agent VARCHAR (50) NOT NULL,
    roi DOUBLE PRECISION NOT NULL,
    devstand DOUBLE PRECISION NOT NULL,
    var DOUBLE PRECISION NOT NULL,
    profitUSD DOUBLE PRECISION NOT NULL,
    middSale DOUBLE PRECISION NOT NULL,
    middPurch DOUBLE PRECISION NOT NULL,
    middTimeSale DOUBLE PRECISION NOT NULL,
    middtitleBettProf VARCHAR (50) NOT NULL,
    middletiteWorseProf VARCHAR (50) NOT NULL,
    notes VARCHAR (1000)
    -- FOREIGN KEY (testId) REFERENCES Testing(id)
);

