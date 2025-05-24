CREATE OR REPLACE FUNCTION person_name_sync() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.new_name IS NULL THEN
            NEW.new_name := NEW.legacy_name;
        ELSIF NEW.legacy_name IS NULL THEN
            NEW.legacy_name := NEW.new_name;
END IF;
RETURN NEW;
END IF;

    IF NEW.legacy_name IS DISTINCT FROM OLD.legacy_name THEN
        NEW.new_name := NEW.legacy_name;
    ELSIF NEW.new_name IS DISTINCT FROM OLD.new_name THEN
        NEW.legacy_name := NEW.new_name;
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS person_name_sync_trigger ON person;
CREATE TRIGGER person_name_sync_trigger
    BEFORE INSERT OR UPDATE ON person
                         FOR EACH ROW EXECUTE FUNCTION person_name_sync();
