-- no-op: ANALYZE has no undo, poniższa instrukcja nic nie zmienia, ale sprawia, że plik nie jest już pusty i ScriptUtils go przepuści:
SELECT 1;
