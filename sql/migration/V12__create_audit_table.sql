CREATE TABLE IF NOT EXISTS person_audit (
    audit_id   BIGSERIAL PRIMARY KEY,
    person_id  BIGINT,
    first_name VARCHAR(100),
    last_name  VARCHAR(100),
    changed_at TIMESTAMP DEFAULT now(),
    operation  VARCHAR(10)
);
