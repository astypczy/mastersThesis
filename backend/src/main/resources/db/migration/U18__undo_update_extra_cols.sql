DO $$
BEGIN
FOR i IN 1..50 LOOP
    EXECUTE format(
      'UPDATE big_table SET col%s = NULL;',
      i
    );
END LOOP;
END;
$$;
