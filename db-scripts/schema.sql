
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
