import pandas as pd
from scipy.stats import ttest_rel, shapiro, wilcoxon
import matplotlib.pyplot as plt

# 1. Wczytaj nowy plik i odfiltruj nieudane (exit_code == -1)
df = pd.read_csv('benchmark_raw_context_cycles.csv')
df = df[df['exit_code'] != -1]

# 2. Przygotuj pary Liquibase vs Liquibase-R według context i repliki
#    – nadaj replikę wewnątrz każdej grupy context
df_fw_mig = (
    df[(df['tool']=='Liquibase') & df['identifier'].str.contains('.fwd.')]
      .assign(rep=lambda d: d.groupby('context').cumcount()+1)
      .set_index(['context','rep'])['migration_ns']
)
df_fw_rb = (
    df[(df['tool']=='Liquibase') & df['identifier'].str.contains('.rbk.')]
      .assign(rep=lambda d: d.groupby('context').cumcount()+1)
      .set_index(['context','rep'])['rollback_ns']
)

paired = pd.concat([df_fw_mig, df_fw_rb], axis=1).dropna().reset_index()
paired.columns = ['ctx','rep','migration_ns','rollback_ns']

# 3. Średnie czasy per ctx
avg_mig = paired.groupby('ctx')['migration_ns'].mean().rename('avg_mig_ns').reset_index()
avg_mig['avg_mig_s'] = (avg_mig['avg_mig_ns'] * 1e-9).round(2)
avg_rb  = paired.groupby('ctx')['rollback_ns'].mean().rename('avg_rb_ns').reset_index()
avg_rb['avg_rb_s']   = (avg_rb['avg_rb_ns']   * 1e-9).round(2)

print("Średnie czasy migracji per ctx:")
print(avg_mig.to_string(index=False))
print("\nŚrednie czasy rollbacku per ctx:")
print(avg_rb.to_string(index=False))

# 4. Test t dla prób zależnych
t_stat, p_val = ttest_rel(paired['migration_ns'], paired['rollback_ns'])
print(f"\nt-statistic: {t_stat:.4f}")
print(f"p-value (two-tailed): {p_val:.4e}")

# 5. Analiza różnic
paired['diff'] = paired['migration_ns'] - paired['rollback_ns']

# 5.1. Test normalności (Shapiro-Wilk)
W, p_shap = shapiro(paired['diff'])
print(f"\nShapiro-Wilk: W = {W:.4f}, p = {p_shap}")

# 5.2. Outliery metodą IQR
Q1 = paired['diff'].quantile(0.25)
Q3 = paired['diff'].quantile(0.75)
IQR = Q3 - Q1
lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
outliers = paired[(paired['diff']<lower) | (paired['diff']>upper)]
print(f"\nLiczba outlierów: {len(outliers)} z {len(paired)}")
print(outliers[['ctx','rep','diff']])

# 6. Rysunki
plt.figure()
plt.hist(paired['diff'], bins=10)
plt.title('Histogram różnic (ns)')
plt.xlabel('migration_ns - rollback_ns')
plt.ylabel('Częstotliwość')
plt.show()

plt.figure()
plt.boxplot(paired['diff'], vert=False)
plt.title('Boxplot różnic (ns)')
plt.xlabel('migration_ns - rollback_ns')
plt.show()

# 7. Test nieparametryczny Wilcoxona (jeśli potrzeba)
stat, p_wilc = wilcoxon(paired['diff'])
print(f"\nTest Wilcoxona: stat = {stat:.4f}, p = {p_wilc}")