import pandas as pd
from scipy.stats import ttest_rel
from scipy.stats import shapiro, wilcoxon
import matplotlib.pyplot as plt
import numpy as np
df_fw = pd.read_csv('flyway.csv')

avg_per_ctx_mig_fw = (df_fw[df_fw['tool'] == 'Flyway']
               .groupby('ctx')['migrationTimeNs']
               .mean()
               .reset_index())
avg_per_ctx_mig_fw['migrationTime_s'] = avg_per_ctx_mig_fw['migrationTimeNs'] * 10**(-9)
print(avg_per_ctx_mig_fw)

sumaAvgCtxNs_fw = sum(avg_per_ctx_mig_fw['migrationTimeNs'])
sumaAvgCtxS_fw = sum(avg_per_ctx_mig_fw['migrationTime_s'])

print(f"Flyway: Średni czas migracji Scenariusza 1.: {sumaAvgCtxNs_fw:.2f} ns")
print(f"Flyway: Średni czas migracji Scenariusza 1.: {sumaAvgCtxS_fw:.2f} s")

avg_per_ctx_rb_fw = (df_fw[df_fw['tool'] == 'Flyway-R']
               .groupby('ctx')['rollbackTimeNs']
               .mean()
               .reset_index())
avg_per_ctx_rb_fw['rollbackTime_s'] = avg_per_ctx_rb_fw['rollbackTimeNs'] * 10**(-9)
print(avg_per_ctx_rb_fw)

sumaAvgCtxNs_fw_rb = sum(avg_per_ctx_rb_fw['rollbackTimeNs'])
sumaAvgCtxS_fw_rb = sum(avg_per_ctx_rb_fw['rollbackTime_s'])

print(f"Flyway: Średni czas rollbacku Scenariusza 1.: {sumaAvgCtxNs_fw_rb:.2f} ns")
print(f"Flyway: Średni czas rollbacku Scenariusza 1.: {sumaAvgCtxS_fw_rb:.2f} s")

mig = (
    df_fw[df_fw['tool']=='Flyway']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount()+1)
    .set_index(['ctx','rep'])
)[['migrationTimeNs']]

rol = (
    df_fw[df_fw['tool']=='Flyway-R']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount()+1)
    .set_index(['ctx','rep'])
)[['rollbackTimeNs']]

paired_fw = pd.concat([mig, rol], axis=1).dropna().reset_index()
print(paired_fw)


df_lb = pd.read_csv('liquibase.csv')

avg_per_ctx_mig_lb = (df_lb[df_lb['tool'] == 'Liquibase']
               .groupby('ctx')['migrationTimeNs']
               .mean()
               .reset_index())
avg_per_ctx_mig_lb['migrationTime_s'] = avg_per_ctx_mig_lb['migrationTimeNs'] * 10**(-9)
print(avg_per_ctx_mig_lb)

sumaAvgCtxNs_lb = sum(avg_per_ctx_mig_lb['migrationTimeNs'])
sumaAvgCtxS_lb = sum(avg_per_ctx_mig_lb['migrationTime_s'])

print(f"Liquibase: Średni czas migracji Scenariusza 1.: {sumaAvgCtxNs_lb:.2f} ns")
print(f"Liquibase: Średni czas migracji Scenariusza 1.: {sumaAvgCtxS_lb:.2f} s")

avg_per_ctx_rb_lb = (df_lb[df_lb['tool'] == 'Liquibase-R']
               .groupby('ctx')['rollbackTimeNs']
               .mean()
               .reset_index())
avg_per_ctx_rb_lb['rollbackTime_s'] = avg_per_ctx_rb_lb['rollbackTimeNs'] * 10**(-9)
print(avg_per_ctx_rb_lb)

sumaAvgCtxNs_lb_rb = sum(avg_per_ctx_rb_lb['rollbackTimeNs'])
sumaAvgCtxS_lb_rb = sum(avg_per_ctx_rb_lb['rollbackTime_s'])

print(f"Liquibase: Średni czas rollbacku Scenariusza 1.: {sumaAvgCtxNs_lb_rb:.2f} ns")
print(f"Liquibase: Średni czas rollbacku Scenariusza 1.: {sumaAvgCtxS_lb_rb:.2f} s")

mig = (
    df_lb[df_lb['tool']=='Liquibase']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount()+1)
    .set_index(['ctx','rep'])
)[['migrationTimeNs']]

rol = (
    df_lb[df_lb['tool']=='Liquibase-R']
    .copy()
    .assign(rep=lambda d: d.groupby('ctx').cumcount()+1)
    .set_index(['ctx','rep'])
)[['rollbackTimeNs']]

paired_lb = pd.concat([mig, rol], axis=1).dropna().reset_index()
print(paired_lb)

df_fw = pd.read_csv('flyway.csv')
df_lb = pd.read_csv('liquibase.csv')

df_fw['ctx'] = df_fw['ctx'] - 1

# 1) Średni czas migracji per ctx dla obu narzędzi (flyway: 2–14, liquibase: 1–13)
avg_mig_fw = (
    df_fw[df_fw['tool']=='Flyway']
      .groupby('ctx')['migrationTimeNs']
      .mean()
      .rename('flyway_avg_mig_ns')
      .reset_index()
)
avg_mig_lb = (
    df_lb[df_lb['tool']=='Liquibase']
      .groupby('ctx')['migrationTimeNs']
      .mean()
      .rename('liquibase_avg_mig_ns')
      .reset_index()
)
# Scalamy zakresy ctx (outer join zachowa wszystkie ctx)
avg_mig = pd.merge(avg_mig_fw, avg_mig_lb, on='ctx', how='outer').sort_values('ctx')

# Konwersja na sekundy i zaokrąglenie do 2 miejsc
avg_mig['flyway_avg_mig_s']    = (avg_mig['flyway_avg_mig_ns']  * 1e-9).round(2)
avg_mig['liquibase_avg_mig_s'] = (avg_mig['liquibase_avg_mig_ns'] * 1e-9).round(2)

print("Average migration time per ctx (s):")
print(avg_mig[['ctx','flyway_avg_mig_s','flyway_avg_mig_ns','liquibase_avg_mig_s','liquibase_avg_mig_ns']].to_string(index=False))


# 2) Średni czas rollbacku per ctx dla obu narzędzi (zakresy te same)
avg_rb_fw = (
    df_fw[df_fw['tool']=='Flyway-R']
      .groupby('ctx')['rollbackTimeNs']
      .mean()
      .rename('flyway_avg_rb_ns')
      .reset_index()
)
avg_rb_lb = (
    df_lb[df_lb['tool']=='Liquibase-R']
      .groupby('ctx')['rollbackTimeNs']
      .mean()
      .rename('liquibase_avg_rb_ns')
      .reset_index()
)
avg_rb = pd.merge(avg_rb_fw, avg_rb_lb, on='ctx', how='outer').sort_values('ctx')

avg_rb['flyway_avg_rb_s']    = (avg_rb['flyway_avg_rb_ns']  * 1e-9).round(2)
avg_rb['liquibase_avg_rb_s'] = (avg_rb['liquibase_avg_rb_ns'] * 1e-9).round(2)

print("\nAverage rollback time per ctx (s):")
print(avg_rb[['ctx','flyway_avg_rb_ns','liquibase_avg_rb_ns','flyway_avg_rb_s','liquibase_avg_rb_s']].to_string(index=False))

plt.figure(figsize=(8,5))
plt.plot(np.arange(1,len(avg_mig['flyway_avg_mig_ns'])+1), avg_mig['flyway_avg_mig_ns'], marker='o', label='Flyway migration')
plt.plot(np.arange(1,len(avg_rb['flyway_avg_rb_ns'])+1), avg_rb['flyway_avg_rb_ns'], marker='o', label='Flyway rollback')
plt.plot(np.arange(1,len(avg_mig['liquibase_avg_mig_ns'])+1), avg_mig['liquibase_avg_mig_ns'], marker='s', label='Liquibase migration')
plt.plot(np.arange(1,len(avg_rb['liquibase_avg_rb_ns'])+1), avg_rb['liquibase_avg_rb_ns'], marker='s', label='Liquibase rollback')
plt.title('Full Scenario Times'); plt.xlabel('Run'); plt.ylabel('Time (ns)')
plt.legend(); plt.grid(True); plt.tight_layout(); plt.savefig('avg_migration_by_ctx.png'); plt.clf()