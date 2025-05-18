UPDATE person SET new_name = first_name || ' ' || last_name;
ALTER TABLE person DROP COLUMN IF EXISTS first_name;
ALTER TABLE person DROP COLUMN IF EXISTS last_name;
