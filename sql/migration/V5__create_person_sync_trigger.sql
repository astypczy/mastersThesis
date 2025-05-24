DROP TRIGGER IF EXISTS person_name_sync_trigger ON person;
CREATE TRIGGER person_name_sync_trigger
    BEFORE INSERT OR UPDATE ON person
                         FOR EACH ROW
                         EXECUTE FUNCTION person_name_sync();
