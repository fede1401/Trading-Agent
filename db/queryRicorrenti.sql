-- SELECT * FROM nasdaq_actions WHERE symbol = 'NFLX' AND EXTRACT(year FROM time_value_it) = 2018 AND EXTRACT(month FROM time_value_it) = 04;

-- SELECT * FROM nasdaq_actions WHERE symbol = 'NFLX' AND EXTRACT(year FROM time_value_it) = 2018 AND EXTRACT(month FROM time_value_it) = 04 AND EXTRACT(hour FROM time_value_it) = 18 AND EXTRACT(minute FROM time_value_it) = 30;

-- SELECT * FROM datatrader order by date desc;

-- SELECT distinct EXTRACT (year FROM time_value_it) AS y FROM nasdaq_actions ORDER BY y;

-- SELECT symbol, time_value_it, open_price, high_price, low_price, close_price, tick_volume FROM nasdaq_actions WHERE symbol='NVDA' AND time_value_it BETWEEN '1999-03-11 22:00:00' AND '2000-03-11 22:00:00';


-- SELECT distinct(symbol), (extract(year from time_value_it)) FROM nasdaq_actions order by extract(year from time_value_it);

-- select count(distinct(symbol)), extract(year from time_value_it) from nasdaq_actions group by extract(year from time_value_it) order by extract(year from time_value_it) ;
-- per mostrare il numero di simboli per anno