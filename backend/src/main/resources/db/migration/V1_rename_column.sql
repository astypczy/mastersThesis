-- 1. Dodajemy nową kolumnę new_name
ALTER TABLE person
    ADD COLUMN new_name TEXT;

-- 2. Kopiujemy istniejące dane z legacy_name do new_name
UPDATE person
SET new_name = legacy_name;

-- 3. Tworzymy funkcję i trigger synchronizujący obie kolumny
CREATE OR REPLACE FUNCTION person_name_sync() RETURNS trigger AS $$
BEGIN
    -- Przy INSERT: jeśli podano jedną kolumnę, ustawiamy drugą na tę samą wartość
    IF TG_OP = 'INSERT' THEN
        IF NEW.new_name IS NULL THEN
            NEW.new_name := NEW.legacy_name;
        ELSIF NEW.legacy_name IS NULL THEN
            NEW.legacy_name := NEW.new_name;
END IF;
RETURN NEW;
END IF;

    -- Przy UPDATE: jeśli zmieniła się legacy_name, przepisujemy do new_name
    IF NEW.legacy_name IS DISTINCT FROM OLD.legacy_name THEN
        NEW.new_name := NEW.legacy_name;
    -- W przeciwnym razie jeśli zmieniła się new_name, przepisujemy do legacy_name
    ELSIF NEW.new_name IS DISTINCT FROM OLD.new_name THEN
        NEW.legacy_name := NEW.new_name;
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Definiujemy trigger wywołujący powyższą funkcję
CREATE TRIGGER person_name_sync_trigger
    BEFORE INSERT OR UPDATE ON person
                         FOR EACH ROW
                         EXECUTE FUNCTION person_name_sync();

-- 4. Usuwamy starą kolumnę legacy_name
ALTER TABLE person
DROP COLUMN legacy_name;
