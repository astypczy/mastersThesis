DO $$
BEGIN
FOR i IN 1..50 LOOP
    EXECUTE format(
      'UPDATE big_table SET col%s = ''UPDATED_'' || id WHERE col%s IS NULL;',
      i, i
    );
END LOOP;
END;
$$;
