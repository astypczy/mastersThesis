ALTER TABLE person ADD COLUMN IF NOT EXISTS first_name VARCHAR(100);
ALTER TABLE person ADD COLUMN IF NOT EXISTS last_name  VARCHAR(100);
UPDATE person SET first_name = split_part(new_name, ' ', 1),
                  last_name  = split_part(new_name, ' ', 2);
