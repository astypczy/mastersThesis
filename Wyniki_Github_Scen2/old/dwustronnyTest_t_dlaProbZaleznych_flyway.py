import pandas as pd
from scipy.stats import ttest_rel
from scipy.stats import shapiro, wilcoxon
import matplotlib.pyplot as plt

df = pd.read_csv('flyway.csv')

avg_per_ctx_mig = (df[df['tool'] == 'Flyway']
               .groupby('ctx')['migrationTimeNs']
               .mean()
               .reset_index())
avg_per_ctx_mig['migrationTime_s'] = avg_per_ctx_mig['migrationTimeNs'] * 10**(-9)
print(avg_per_ctx_mig)

sumaAvgCtxNs = sum(avg_per_ctx_mig['migrationTimeNs'])
sumaAvgCtxS = sum(avg_per_ctx_mig['migrationTime_s'])

print(f"Średni czas migracji Scenariusza 1.: {sumaAvgCtxNs:.2f} ns")
print(f"Średni czas migracji Scenariusza 1.: {sumaAvgCtxS:.2f} s")

avg_per_ctx_rb = (df[df['tool'] == 'Flyway-R']
               .groupby('ctx')['rollbackTimeNs']
               .mean()
               .reset_index())
avg_per_ctx_rb['rollbackTime_s'] = avg_per_ctx_rb['rollbackTimeNs'] * 10**(-9)
print(avg_per_ctx_rb)

sumaAvgCtxNs_rb = sum(avg_per_ctx_rb['rollbackTimeNs'])
sumaAvgCtxS_rb = sum(avg_per_ctx_rb['rollbackTime_s'])

print(f"Średni czas rollbacku Scenariusza 1.: {sumaAvgCtxNs_rb:.2f} ns")
print(f"Średni czas rollbacku Scenariusza 1.: {sumaAvgCtxS_rb:.2f} s")

mig = (
    df[df['tool']=='Flyway']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount()+1)
    .set_index(['ctx','rep'])
)[['migrationTimeNs']]

rol = (
    df[df['tool']=='Flyway-R']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount()+1)
    .set_index(['ctx','rep'])
)[['rollbackTimeNs']]

paired = pd.concat([mig, rol], axis=1).dropna().reset_index()
print(paired)
t_stat, p_val = ttest_rel(paired['migrationTimeNs'], paired['rollbackTimeNs'])

print(f"t-statistic: {t_stat:.4f}")
print(f"p-value (two-tailed): {p_val}")

paired['diff'] = paired['migrationTimeNs'] - paired['rollbackTimeNs']

# 1) Test Shapiro-Wilka na normalność różnic
W, p_normal = shapiro(paired['diff'])
print(f"Shapiro-Wilk: W = {W:.4f}, p = {p_normal}")

# 2) Wykrywanie outlierów metodą IQR
Q1 = paired['diff'].quantile(0.25)
Q3 = paired['diff'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = paired[(paired['diff'] < lower) | (paired['diff'] > upper)]
print(f"Liczba outlierów: {len(outliers)} z {len(paired)}")
print("Outliery (diff):")
print(outliers[['ctx','rep','diff']])

# 3) (opcjonalnie) histogram i boxplot różnic
plt.figure()
plt.hist(paired['diff'], bins=10)
plt.title('Histogram różnic czasów')
plt.xlabel('Diff [ns]')
plt.ylabel('Częstotliwość')
plt.show()

plt.figure()
plt.boxplot(paired['diff'], vert=False)
plt.title('Boxplot różnic czasów')
plt.xlabel('Diff [ns]')
plt.show()

# Jeśli rozkład nie jest normalny, możesz użyć testu Wilcoxona:
stat, p_wilc = wilcoxon(paired['diff'])
print(f"Test Wilcoxona: stat = {stat:.4f}, p = {p_wilc}")