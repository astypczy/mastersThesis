import pandas as pd
from scipy.stats import ttest_rel, shapiro, wilcoxon
import matplotlib.pyplot as plt

# 1. Wczytaj dane i odfiltruj nieudane (exit_code == -1)
df = pd.read_csv('benchmark_raw_context_cycles.csv')
df = df[df['exit_code'] != -1]

# 2. Przygotuj dane migracji Flyway
mig_fly = (
    df[(df['tool'] == 'Flyway') & df['identifier'].str.contains(r'\.fwd\.')]
    .copy()
    .assign(
        rep=lambda d: d.groupby('context').cumcount() + 1,
        ctx=lambda d: d['context']  
    )
    .loc[:, ['ctx', 'rep', 'migration_ns']]
    .rename(columns={'migration_ns': 'migrationTimeNs_flyway'})
)

# 3. Przygotuj dane migracji Liquibase
mig_liq = (
    df[(df['tool'] == 'Liquibase') & df['identifier'].str.contains(r'\.fwd\.')]
    .copy()
    .assign(
        rep=lambda d: d.groupby('context').cumcount() + 1,
        ctx=lambda d: d['context']  
    )
    .loc[:, ['ctx', 'rep', 'migration_ns']]
    .rename(columns={'migration_ns': 'migrationTimeNs_liquibase'})
)

# 4. Sparuj po ctx i rep
paired = pd.merge(
    mig_fly, mig_liq,
    on=['ctx', 'rep'],
    how='inner'
)

# 5. Obliczenia średnich czasów per ctx
avg_ctx = paired.groupby('ctx').mean().reset_index()
avg_ctx['flyway_s']    = avg_ctx['migrationTimeNs_flyway']    * 1e-9
avg_ctx['liquibase_s'] = avg_ctx['migrationTimeNs_liquibase'] * 1e-9

print("Średnie czasy migracji per ctx:")
print(avg_ctx[['ctx',
                'migrationTimeNs_flyway', 'migrationTimeNs_liquibase',
                'flyway_s', 'liquibase_s']].to_string(index=False))

# 6. Całkowite średnie czasy
total_fly_ns = avg_ctx['migrationTimeNs_flyway'].sum()
total_liq_ns = avg_ctx['migrationTimeNs_liquibase'].sum()
print(f"\nŁączna średnia Flyway:     {total_fly_ns:.2f} ns ({total_fly_ns*1e-9:.2f} s)")
print(f"Łączna średnia Liquibase:  {total_liq_ns:.2f} ns ({total_liq_ns*1e-9:.2f} s)\n")

# 7. Przygotuj różnice
diffs = paired['migrationTimeNs_flyway'] - paired['migrationTimeNs_liquibase']

# 8. Test normalności Shapiro-Wilk
W, p_norm = shapiro(diffs)
print(f"Shapiro-Wilk: W={W:.4f}, p={p_norm}")

# 9. Test statystyczny parowanych różnic
t_stat, p_val = ttest_rel(paired['migrationTimeNs_flyway'],
                          paired['migrationTimeNs_liquibase'])
print(f"Paired t-test: t={t_stat}, p={p_val}")

stat, p_wilc = wilcoxon(diffs)
print(f"Wilcoxon test: stat={stat}, p={p_wilc}")

# 10. Wizualizacje
plt.figure()
plt.hist(diffs, bins=10)
plt.title('Histogram różnic czasów: Flyway - Liquibase (ns)')
plt.xlabel('Różnica [ns]')
plt.ylabel('Częstotliwość')
plt.tight_layout()
plt.show()
