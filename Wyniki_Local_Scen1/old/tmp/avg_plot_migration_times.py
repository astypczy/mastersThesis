import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('benchmark_raw_context_cycles.csv')
df = df[df['exit_code'] != -1]

mig = df[df['identifier'].str.contains('.fwd.')]
rbk = df[df['identifier'].str.contains('.rbk.')]

fw_mig = mig[mig['tool']=='Flyway'].groupby('context')['migration_ns'].mean().rename('flyway_mig')
lb_mig = mig[mig['tool']=='Liquibase'].groupby('context')['migration_ns'].mean().rename('liquibase_mig')
avg_mig = pd.concat([fw_mig, lb_mig], axis=1).fillna(0).sort_index()

fw_rb = rbk[rbk['tool']=='Flyway'].groupby('context')['rollback_ns'].mean().rename('flyway_rb')
lb_rb = rbk[rbk['tool']=='Liquibase'].groupby('context')['rollback_ns'].mean().rename('liquibase_rb')
avg_rb = pd.concat([fw_rb, lb_rb], axis=1).fillna(0).sort_index()

def plot_pair(df, col1, col2, ylabel, title):
    plt.figure(figsize=(10,5))
    x = df.index
    width = 0.35
    plt.bar(x - width/2, df[col1], width, label=col1.split('_')[0])
    plt.bar(x + width/2, df[col2], width, label=col2.split('_')[0])
    plt.xlabel('Context')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x)
    plt.legend()
    plt.tight_layout()
    plt.show()

# 5. Wykresy
plot_pair(avg_mig, 'flyway_mig',    'liquibase_mig',    'Migration time (ns)', 'Avg Migration Time by Context')
plot_pair(avg_rb,  'flyway_rb',     'liquibase_rb',     'Rollback time (ns)',  'Avg Rollback Time by Context')