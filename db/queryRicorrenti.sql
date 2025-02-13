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



-----------

-- 31 gennaio 2025:
-- select symbol, time_value_it, open_price, high_price, low_price, close_price from nasdaq_actions where symbol='AAPL' and time_value_it between '2021-12-20 00:00:00' and '2022-01-07 00:00:00';
--select * from middleprofit;

-- SELECT symbol, time_value_it, open_price, high_price, low_price, close_price  FROM nasdaq_actions  WHERE symbol = 'AAPL' AND CAST(close_price AS TEXT) LIKE '182%';

--select * from nasdaq_actions LIMIT 1000;

-- select * from middleProfit where agent='agent2';

--select symbol, time_value_it, open_price, high_price, low_price, close_price from nasdaq_actions where symbol='REGN' and time_value_it between '2019-06-17 00:00:00' and '2020-06-17 00:00:00';

--select testid, agent, roi, profitusd, var, devstand, middpurch, middsale, middtimesale, middtitlebettprof, middletiteworseprof, notes from middleProfit where agent='agent2' or agent='------';

-- select sum(profit_usd) from sale;
-- select * from sale;

-- select * from nasdaq_actions where symbol='EQIX' and time_value_it between '2011-09-20 00:00:00' and '2012-07-26 00:00:00';

-- select * from middleprofit where notes = 'TP:0.01%, nasdaq_actions, buy no randomly but one after the other' order by testid desc;
-- select * from sale;
-- select * from testing;

-- select * from middleprofit order by testid desc;

--select * from testing where id = '102';

--select distinct(symbol) from nasdaq_actions;

--select * from larg_comp_eu_actions where symbol='COLR.BR';

--select distinct(symbol) from larg_comp_eu_actions;

--select count(*) from nasdaq_actions;

--2108338
--2148609


--select testid, agent, roi, notes from middleprofit order by testid;

-- select * from middleprofit order by testid;

--delete from middleprofit where testid= 284 and agent = '------';
--  select distinct(symbol) from purchase;

-- delete from middleprofit where agent = 'agent5';
-- select * from testing;
--delete from testing where agent ='agent5';


-- select distinct(symbol) from larg_comp_eu_actions;


-- select * from nasdaq_actions limit 100;

-- select count(*) from nasdaq_actions;

-- select * from nasdaq_actions where symbol='GT' and time_value_it between '1999-06-24 00:00:00' and '2000-06-24 00:00:00' ;

-- select * from testing order by id desc;

-- select * from testing where id>=599 order by numbertest ;

-- select * from middleprofit order by testid desc;


--select * from testing, middleprofit
--where id= testid
--order by profitperc desc;

--select symbol, time_value_it, open_price, high_price, low_price, close_price 
--from nasdaq_actions 
--where symbol = 'GMGI' 
--and time_value_IT between '2016-01-01' and '2017-01-01' 
--order by time_value_it;

-- select * from larg_comp_eu_actions where time_value_IT between '2009-05-18' and '2010-05-18';

-- select * from middleprofit order by testid desc;

