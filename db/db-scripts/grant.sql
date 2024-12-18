
-- connettersi al database dbname

\c :dbname postgres

-- user already exists
GRANT ALL PRIVILEGES ON DATABASE :dbname to :username ;


ALTER TABLE nasdaq_actions OWNER TO :username ;
ALTER TABLE nyse_actions OWNER TO :username ;
ALTER TABLE larg_comp_eu_actions OWNER TO :username
ALTER TABLE Purchase OWNER TO :username;
ALTER TABLE Sale OWNER TO :username;
ALTER TABLE DataTrader OWNER TO :username;
ALTER TABLE loginDate OWNER TO :username;
ALTER TABLE Testing OWNER TO :username;
ALTER TABLE Sector OWNER TO :username;


GRANT ALL ON SCHEMA public TO :username ;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO :username ;