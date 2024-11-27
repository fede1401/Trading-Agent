-- SELECT * FROM nasdaq_actions WHERE symbol = 'NFLX' AND EXTRACT(year FROM time_value_it) = 2018 AND EXTRACT(month FROM time_value_it) = 04;

-- SELECT * FROM nasdaq_actions WHERE symbol = 'NFLX' AND EXTRACT(year FROM time_value_it) = 2018 AND EXTRACT(month FROM time_value_it) = 04 AND EXTRACT(hour FROM time_value_it) = 18 AND EXTRACT(minute FROM time_value_it) = 30;

-- SELECT * FROM datatrader order by date desc;

-- SELECT distinct EXTRACT (year FROM time_value_it) AS y FROM nasdaq_actions ORDER BY y;

-- SELECT symbol, time_value_it, open_price, high_price, low_price, close_price, tick_volume FROM nasdaq_actions WHERE symbol='NVDA' AND time_value_it BETWEEN '1999-03-11 22:00:00' AND '2000-03-11 22:00:00';


-- SELECT distinct(symbol), (extract(year from time_value_it)) FROM nasdaq_actions order by extract(year from time_value_it);

-- select count(distinct(symbol)), extract(year from time_value_it) from nasdaq_actions group by extract(year from time_value_it) order by extract(year from time_value_it) ;
-- per mostrare il numero di simboli per anno

-- SELECT symbol, time_value_it, open_price, high_price FROM nasdaq_actions 
-- WHERE symbol = 'MSFT' AND time_value_it BETWEEN '2008-11-25' AND '2008-12-29';

-- SELECT * FROM nasdaq_actions WHERE time_value_it BETWEEN '2008-11-25' AND '2009-11-25';

-- SELECT * FROM testing where id = '4' order by profit desc;
-- SELECT * FROM testing order by initial_date;
-- SELECT * FROM testing order by profit desc;
-- SELECT * FROM testing;
-- SELECT * FROM testing where id = '7' order by profit; 
-- DELETE FROM testing where id = '0' ;
-- DELETE FROM testing;
-- SELECT sum(profit)/count(*) as media FROM testing where id = '7';
-- SELECT sum(profit)/count(*) as media FROM testing;

-- SELECT * from MiddleProfit order by testid;

-- SELECT MIN(time_value_it) + INTERVAL '42 year 6 month 31 day' FROM nasdaq_actions; -- 2015-01-01 00:00:00
-- SELECT MIN(time_value_it) + INTERVAL '25 year 11 month 8 day' FROM nasdaq_actions; -- 1998-05-09 00:00:00
-- SELECT MIN(time_value_it) + INTERVAL '47 year 6 month 31 day' FROM nasdaq_actions; -- 2020-01-01 00:00:00
-- SELECT MIN(time_value_it) + INTERVAL '23 year 11 month 8 day' FROM nasdaq_actions; -- 1996-05-09 00:00:00

-- SELECT distinct(symbol) FROM nasdaq_actions WHERE time_value_it BETWEEN '1995-01-01' AND  '1995-12-01';

-- SELECT max(time_value_it) FROM nasdaq_actions;

-- SELECT * FROM sale order by profit_perc desc;

-- SELECT distinct(symbol) FROM nasdaq_actions; 

-- SELECT * FROM nasdaq_actions where symbol = 'ABNB' order by time_value_it;


-- SELECT symbol, time_value_it, open_price, high_price 
-- FROM nasdaq_actions 
-- WHERE symbol= 'MASI' AND time_value_it BETWEEN '2023-10-03' AND '2023-12-03'; 

-- select datepur, datesal, (datesal - datepur) AS diff_days , ticket_pur, ticket_sale, symbol, pricepurchase, pricesale from sale where datesal <> datepur and datepur <> datesal + INTERVAL '1 day' order by datepur;
-- per controllare nelle vendite, quanto dopo è stata venduta l'azione.

-- select distinct(symbol) from sale where datesal <> datepur and datepur <> datesal + INTERVAL '1 day';

-- select datepur, datesal, (datesal - datepur) AS diff_days , ticket_pur, ticket_sale, symbol, pricepurchase, pricesale from sale 
-- where datesal <> datepur and datepur <> datesal + INTERVAL '1 day' order by diff_days desc;


-- select * from purchase;

-- select distinct(symbol) from nasdaq_actions;

-- select * from nasdaq_actions where symbol = 'AAPL' and time_value_it = '2024-11-14 00:00:00';
-- delete from nasdaq_actions where symbol = '';

--  select * from nyse_actions limit 10000;
-- delete from nyse_actions;

-- select count(*) from nyse_actions;


-- SELECT symbol, time_value_it, open_price, high_price FROM nasdaq_actions 
-- WHERE symbol = 'MSFT' AND time_value_it BETWEEN '2008-11-25' AND '2008-12-29';

-- SELECT * FROM nasdaq_actions WHERE time_value_it BETWEEN '2008-11-25' AND '2009-11-25';

-- SELECT * FROM testing where id = '4' order by profit desc;
-- SELECT * FROM testing order by initial_date;
-- SELECT * FROM testing order by profit desc;
-- SELECT * FROM testing;
-- SELECT * FROM testing where id = '7' order by profit; 
-- DELETE FROM testing where id = '0' ;
-- DELETE FROM testing;
-- SELECT sum(profit)/count(*) as media FROM testing where id = '7';
-- SELECT sum(profit)/count(*) as media FROM testing;

-- SELECT * from MiddleProfit order by testid;

-- SELECT MIN(time_value_it) + INTERVAL '42 year 6 month 31 day' FROM nasdaq_actions; -- 2015-01-01 00:00:00
-- SELECT MIN(time_value_it) + INTERVAL '25 year 11 month 8 day' FROM nasdaq_actions; -- 1998-05-09 00:00:00
-- SELECT MIN(time_value_it) + INTERVAL '47 year 6 month 31 day' FROM nasdaq_actions; -- 2020-01-01 00:00:00
-- SELECT MIN(time_value_it) + INTERVAL '23 year 11 month 8 day' FROM nasdaq_actions; -- 1996-05-09 00:00:00

-- SELECT distinct(symbol) FROM nasdaq_actions WHERE time_value_it BETWEEN '1995-01-01' AND  '1995-12-01';

-- SELECT max(time_value_it) FROM nasdaq_actions;

-- SELECT * FROM sale order by profit_perc desc;

-- SELECT distinct(symbol) FROM nasdaq_actions; 

-- SELECT * FROM nasdaq_actions where symbol = 'ABNB' order by time_value_it;


-- SELECT symbol, time_value_it, open_price, high_price 
-- FROM nasdaq_actions 
-- WHERE symbol= 'MASI' AND time_value_it BETWEEN '2023-10-03' AND '2023-12-03'; 

-- select datepur, datesal, (datesal - datepur) AS diff_days , ticket_pur, ticket_sale, symbol, pricepurchase, pricesale from sale where datesal <> datepur and datepur <> datesal + INTERVAL '1 day' order by datepur;
-- per controllare nelle vendite, quanto dopo è stata venduta l'azione.

-- select distinct(symbol) from sale where datesal <> datepur and datepur <> datesal + INTERVAL '1 day';

-- select datepur, datesal, (datesal - datepur) AS diff_days , ticket_pur, ticket_sale, symbol, pricepurchase, pricesale from sale 
-- where datesal <> datepur and datepur <> datesal + INTERVAL '1 day' order by diff_days desc;


-- select * from purchase;

-- select distinct(symbol) from nasdaq_actions;

-- select * from nasdaq_actions where symbol = 'AAPL' and time_value_it = '2024-11-14 00:00:00';
-- delete from nasdaq_actions where symbol = '';

-- select * from nyse_actions limit 10000;
-- delete from nyse_actions;

--select count(distinct(symbol)) from larg_comp_eu_actions;
-- select min(time_value_IT) from nasdaq_actions;

--select * from larg_comp_eu_actions;
-- select * from testing;
-- delete from MiddleProfit

-- delete from testing;

-- delete from testing where id = 1;
-- delete from nyse_actions;

-- SELECT sum(profit)/count(*) as media FROM testing where id = 2 and market = 'larg_comp_eu_actions';


-- SELECT symbol,open_price FROM larg_comp_eu_actions WHERE time_value_it = '1999-11-25 00:00:00';


--SELECT distinct(symbol) FROM larg_comp_eu_actions WHERE time_value_it BETWEEN '1999-11-25 00:00:00' AND '2000-11-25 00:00:00';



