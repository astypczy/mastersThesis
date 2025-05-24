import re
import os
from collections import namedtuple, defaultdict

# Definicja metryk
Metrics = namedtuple('Metrics', [
    'loc', 'stmt_count', 'max_depth', 'cyclomatic', 'comment_ratio'
])

# Funkcje metryczne (identyczne jak dla Liquibase)
def count_loc(code):
    lines = code.splitlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('--')]
    return len(code_lines)

def count_statements(code):
    return len(re.findall(r'\b(CREATE|ALTER|DROP|INSERT|UPDATE|DELETE)\b',
                          code, flags=re.IGNORECASE))

def count_cyclomatic(code):
    branches = re.findall(r'\b(IF|ELSIF|LOOP|CASE|WHEN)\b',
                          code, flags=re.IGNORECASE)
    return 1 + len(branches)

def comment_ratio(code):
    lines = [l for l in code.splitlines() if l.strip()]
    comments = [l for l in lines if l.strip().startswith('--') or l.strip().startswith('/*')]
    return len(comments) / len(lines) if lines else 0

# Głębokość zagnieżdżeń SQL (prostym licznikiem poziomów wcięć)
def max_sql_depth(code):
    max_d = cur_d = 0
    for line in code.splitlines():
        indent = len(line) - len(line.lstrip(' '))
        level = indent // 4  # zakładamy 4 spacje = 1 poziom
        cur_d = level
        max_d = max(max_d, cur_d)
    return max_d

# Ścieżka do katalogu ze skryptami Flyway
scripts_dir = 'migration'

# Zbior wyników: ctx -> {'mig': Metrics, 'rb': Metrics}
results = defaultdict(lambda: {})

for fname in os.listdir(scripts_dir):
    path = os.path.join(scripts_dir, fname)
    if not fname.lower().endswith('.sql'):
        continue

    # Migracje: pliki V{ver}__*.sql
    m = re.match(r'[Vv](\d+)__.*\.sql$', fname)
    if m:
        ver = int(m.group(1))
        ctx = ver - 1  # V2 -> ctx=1, ..., V24->ctx=23
        kind = 'mig'
    else:
        # Rollbacki: pliki U{ver}__*.sql
        m = re.match(r'[Uu](\d+)__.*\.sql$', fname)
        if m:
            ver = int(m.group(1))
            ctx = ver - 1
            kind = 'rb'
        else:
            continue

    # Wczytaj zawartość
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # Oblicz metryki
    metrics = Metrics(
        loc          = count_loc(code),
        stmt_count   = count_statements(code),
        max_depth    = max_sql_depth(code),
        cyclomatic   = count_cyclomatic(code),
        comment_ratio= comment_ratio(code),
    )

    results[ctx][kind] = metrics

# Wyświetl wyniki
for ctx in sorted(results):
    mig = results[ctx].get('mig')
    rb  = results[ctx].get('rb')
    print(f"\n=== ctx {ctx} ===")
    if mig:
        print("Migration script:")
        print(f"  LOC          = {mig.loc}")
        print(f"  Statements   = {mig.stmt_count}")
        print(f"  MaxDepth     = {mig.max_depth}")
        print(f"  Cyclomatic   = {mig.cyclomatic}")
        print(f"  CommentRatio = {mig.comment_ratio:.2f}")
    if rb:
        print("Rollback script:")
        print(f"  LOC          = {rb.loc}")
        print(f"  Statements   = {rb.stmt_count}")
        print(f"  MaxDepth     = {rb.max_depth}")
        print(f"  Cyclomatic   = {rb.cyclomatic}")
        print(f"  CommentRatio = {rb.comment_ratio:.2f}")
