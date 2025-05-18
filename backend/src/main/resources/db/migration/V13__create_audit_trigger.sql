CREATE OR REPLACE FUNCTION person_audit_trig_fn() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO person_audit(person_id, first_name, last_name, operation)
        VALUES(NEW.id, NEW.first_name, NEW.last_name, 'INSERT');
RETURN NEW;
ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO person_audit(person_id, first_name, last_name, operation)
        VALUES(OLD.id, OLD.first_name, OLD.last_name, 'UPDATE');
RETURN NEW;
ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO person_audit(person_id, first_name, last_name, operation)
        VALUES(OLD.id, OLD.first_name, OLD.last_name, 'DELETE');
RETURN OLD;
END IF;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS person_audit_trig ON person;
CREATE TRIGGER person_audit_trig
    AFTER INSERT OR UPDATE OR DELETE ON person
    FOR EACH ROW EXECUTE FUNCTION person_audit_trig_fn();
