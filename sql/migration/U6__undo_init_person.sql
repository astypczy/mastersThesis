ALTER TABLE person
    ADD COLUMN legacy_name VARCHAR(100);

UPDATE person
SET legacy_name = name;
