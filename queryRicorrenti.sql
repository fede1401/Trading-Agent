-- SELECT * FROM nasdaq_actions WHERE symbol = 'NFLX' AND EXTRACT(year FROM time_value_it) = 2018 AND EXTRACT(month FROM time_value_it) = 04;

-- SELECT * FROM nasdaq_actions WHERE symbol = 'NFLX' AND EXTRACT(year FROM time_value_it) = 2018 AND EXTRACT(month FROM time_value_it) = 04 AND EXTRACT(hour FROM time_value_it) = 18 AND EXTRACT(minute FROM time_value_it) = 30;

-- SELECT * FROM datatrader order by date desc;

-- SELECT distinct EXTRACT (year FROM time_value_it) AS y FROM nasdaq_actions ORDER BY y;