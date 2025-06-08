import pandas as pd
from scipy.stats import ttest_rel, shapiro, wilcoxon
import matplotlib.pyplot as plt

# Wczytanie danych z plików
flyway_df = pd.read_csv('flyway.csv')
liquibase_df = pd.read_csv('liquibase.csv')

# Przygotowanie danych migracji
mig_fly = (
    flyway_df[flyway_df['tool'] == 'Flyway']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount() + 1,
            ctx=lambda d: d['ctx'] - 1)
    .loc[:, ['ctx', 'rep', 'migrationTimeNs']]
)
mig_liq = (
    liquibase_df[liquibase_df['tool'] == 'Liquibase']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount() + 1)
    .loc[:, ['ctx', 'rep', 'migrationTimeNs']]
)

# Połączenie zestawów po zmodyfikowanym ctx i rep
paired = pd.merge(
    mig_fly, mig_liq,
    on=['ctx', 'rep'],
    how='inner',
    suffixes=('_flyway', '_liquibase')
)

# Obliczenia średnich czasów
avg_ctx = paired.groupby('ctx').mean().reset_index()
avg_ctx['flyway_s'] = avg_ctx['migrationTimeNs_flyway'] * 1e-9
avg_ctx['liquibase_s'] = avg_ctx['migrationTimeNs_liquibase'] * 1e-9
print("Średnie czasy migracji per ctx:")
print(avg_ctx[['ctx', 'migrationTimeNs_flyway', 'migrationTimeNs_liquibase', 'flyway_s', 'liquibase_s']])

# Całkowite średnie czasy
total_fly_ns = avg_ctx['migrationTimeNs_flyway'].sum()
total_liq_ns = avg_ctx['migrationTimeNs_liquibase'].sum()
print(f"\nŁączna średnia Flyway: {total_fly_ns:.2f} ns ({total_fly_ns*1e-9:.2f} s)")
print(f"Łączna średnia Liquibase: {total_liq_ns:.2f} ns ({total_liq_ns*1e-9:.2f} s)\n")

# Test statystyczny parowanych różnic
diffs = paired['migrationTimeNs_flyway'] - paired['migrationTimeNs_liquibase']

# Test Shapiro-Wilka
W, p_norm = shapiro(diffs)
print(f"Shapiro-Wilk: W={W:.4f}, p={p_norm}")

# if p_norm > 0.05:
#     t_stat, p_val = ttest_rel(paired['migrationTimeNs_flyway'], paired['migrationTimeNs_liquibase'])
#     print(f"Paired t-test: t={t_stat:.4f}, p={p_val:.4f}")
# else:
#     stat, p_wilc = wilcoxon(diffs)
#     print(f"Wilcoxon test: stat={stat:.4f}, p={p_wilc:.4f}")

t_stat, p_val = ttest_rel(paired['migrationTimeNs_flyway'], paired['migrationTimeNs_liquibase'])
print(f"Paired t-test: t={t_stat}, p={p_val}")
stat, p_wilc = wilcoxon(diffs)
print(f"Wilcoxon test: stat={stat}, p={p_wilc}")

# Wizualizacje
plt.figure()
plt.hist(diffs, bins=10)
plt.title('Histogram różnic czasów: Flyway - Liquibase (ns)')
plt.xlabel('Różnica [ns]')
plt.ylabel('Częstotliwość')
plt.tight_layout()
plt.show()