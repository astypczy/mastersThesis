INSERT INTO big_table (col1, col2, col3)
SELECT
    md5(random()::text),
    md5(random()::text),
    md5(random()::text)
FROM generate_series(1,20000);
