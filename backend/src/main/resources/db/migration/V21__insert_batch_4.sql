INSERT INTO big_table (col1)
SELECT md5(random()::text)
FROM generate_series(1,20000);
