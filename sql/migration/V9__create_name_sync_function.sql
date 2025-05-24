CREATE OR REPLACE FUNCTION person_name_sync_v2() RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        IF NEW.new_name IS NOT NULL THEN
            NEW.first_name := split_part(NEW.new_name, ' ', 1);
            NEW.last_name  := NULLIF(split_part(NEW.new_name, ' ', 2), '');
END IF;
RETURN NEW;
END IF;

    IF TG_OP = 'UPDATE' AND NEW.new_name IS DISTINCT FROM OLD.new_name THEN
        NEW.first_name := split_part(NEW.new_name, ' ', 1);
        NEW.last_name  := NULLIF(split_part(NEW.new_name, ' ', 2), '');
END IF;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;
