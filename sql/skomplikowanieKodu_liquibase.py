import re
import xml.etree.ElementTree as ET
from collections import namedtuple
import csv

# Definicja metryk
Metrics = namedtuple('Metrics', [
    'loc', 'stmt_count', 'max_depth', 'cyclomatic', 'comment_ratio'
])

# Parsowanie XML
tree = ET.parse('db.changelog-master.xml')
ns = {'lb': 'http://www.liquibase.org/xml/ns/dbchangelog'}
root = tree.getroot()

def get_sql_text(cs):
    """Zwróć wszystkie teksty SQL wewnątrz <sql> i CDATA."""
    parts = []
    for sql in cs.findall('.//lb:sql', ns):
        text = ''.join(sql.itertext())
        parts.append(text.strip())
    return '\n'.join(parts)

def count_loc(code):
    """LOC: niepuste, niekomentarzowe linie."""
    lines = code.splitlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('--')]
    # usuń linie /*...*/ i XML-comment <!-- -->
    code_lines = [l for l in code_lines if not l.strip().startswith('/*') and not l.strip().startswith('<!--')]
    return len(code_lines)

def count_statements(code):
    """Zlicz przynajmniej CREATE, ALTER, DROP, INSERT, UPDATE, DELETE."""
    return len(re.findall(r'\b(CREATE|ALTER|DROP|INSERT|UPDATE|DELETE)\b', code, flags=re.IGNORECASE))

def max_tag_depth(elem, tags):
    """Rekurencyjnie zmierz głębokość zagnieżdżeń wybranych tagów."""
    def dfs(node, depth):
        best = depth if node.tag in tags else 0
        for ch in node:
            best = max(best, dfs(ch, depth + (1 if node.tag in tags else 0)))
        return best
    return dfs(elem, 0)

def count_cyclomatic(code):
    """Przybliżone McCabe: 1 + liczba if/while/loop/case."""
    branches = re.findall(r'\b(IF|ELSIF|LOOP|CASE|WHEN)\b', code, flags=re.IGNORECASE)
    return 1 + len(branches)

def comment_ratio(code):
    """Stosunek linii komentarzy SQL do wszystkich linii."""
    lines = code.splitlines()
    total = len([l for l in lines if l.strip()])
    comments = len([l for l in lines if l.strip().startswith('--') or l.strip().startswith('/*')])
    return comments / total if total else 0

# Zbierz metryki dla każdego changeSet
results = []
for cs in root.findall('lb:changeSet', ns):
    cs_id      = cs.get('id')
    ctx        = cs.get('context')
    # skrypt: SQL + XML wewnątrz <addColumn>, <dropColumn> itd.
    sql_code   = get_sql_text(cs)
    xml_str    = ET.tostring(cs, encoding='unicode')
    code       = xml_str + '\n' + sql_code

    m = Metrics(
        loc          = count_loc(code),
        stmt_count   = count_statements(code),
        max_depth    = max_tag_depth(cs, {'{http://www.liquibase.org/xml/ns/dbchangelog}and',
                                          '{http://www.liquibase.org/xml/ns/dbchangelog}or',
                                          '{http://www.liquibase.org/xml/ns/dbchangelog}not',
                                          '{http://www.liquibase.org/xml/ns/dbchangelog}preConditions'}),
        cyclomatic   = count_cyclomatic(code),
        comment_ratio= comment_ratio(code),
    )
    results.append((cs_id, ctx, m))

with open('liquibase_metrics.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['changeSet', 'context', 'LOC', 'Statements', 'MaxDepth', 'Cyclomatic', 'CommentRatio'])
    for cs_id, ctx, m in results:
        writer.writerow([cs_id, ctx, m.loc, m.stmt_count, m.max_depth, m.cyclomatic, f"{m.comment_ratio:.2f}"])

print("Wyniki zapisane do 'liquibase_metrics.csv'.")

# Wyświetl podsumowanie
for cs_id, ctx, m in results:
    print(f"changeSet {cs_id} (ctx={ctx}):")
    print(f"  LOC          = {m.loc}")
    print(f"  Statements   = {m.stmt_count}")
    print(f"  MaxDepth     = {m.max_depth}")
    print(f"  Cyclomatic   = {m.cyclomatic}")
    print(f"  CommentRatio = {m.comment_ratio:.2f}\n")
