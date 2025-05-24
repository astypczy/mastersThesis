DROP TRIGGER IF EXISTS person_name_sync_v2_trigger ON person;
CREATE TRIGGER person_name_sync_v2_trigger
    BEFORE INSERT OR UPDATE ON person
                         FOR EACH ROW EXECUTE FUNCTION person_name_sync_v2();
