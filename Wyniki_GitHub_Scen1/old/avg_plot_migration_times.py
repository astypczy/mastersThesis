import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

flyway_df    = pd.read_csv('flyway.csv')
liquibase_df = pd.read_csv('liquibase.csv')

flyway_df['ctx'] -= 1

avg_flyway    = flyway_df.groupby('ctx')['migrationTimeNs'].mean().rename('flyway_avg')
avg_liquibase = liquibase_df.groupby('ctx')['migrationTimeNs'].mean().rename('liquibase_avg')
avg_mig = pd.concat([avg_liquibase, avg_flyway], axis=1).reset_index()

plt.figure(figsize=(10,5))
x = avg_mig['ctx']
width = 0.35
plt.bar(x - width/2, avg_mig['liquibase_avg'], width, label='Liquibase')
plt.bar(x + width/2, avg_mig['flyway_avg'],    width, label='Flyway')
plt.xlabel('Context')
plt.ylabel('Average migration time (ns)')
plt.title('Scenario 1.: Average Migration Time by Context')
plt.xticks(x)
plt.legend()
plt.tight_layout()
plt.show()

avg_flyway_rb    = flyway_df.groupby('ctx')['rollbackTimeNs'].mean().rename('flyway_avg_rb')
avg_liquibase_rb = liquibase_df.groupby('ctx')['rollbackTimeNs'].mean().rename('liquibase_avg_rb')
avg_rb = pd.concat([avg_liquibase_rb, avg_flyway_rb], axis=1).reset_index()

plt.figure(figsize=(10,5))
x = avg_rb['ctx']
plt.bar(x - width/2, avg_rb['liquibase_avg_rb'], width, label='Liquibase')
plt.bar(x + width/2, avg_rb['flyway_avg_rb'],    width, label='Flyway')
plt.xlabel('Context')
plt.ylabel('Average rollback time (ns)')
plt.title('Scenario 1.: Average Rollback Time by Context')
plt.xticks(x)
plt.legend()
plt.tight_layout()
plt.show()

avg_flyway_sr    = flyway_df.groupby('ctx')['successRate'].mean().rename('flyway_avg_sr')
avg_liquibase_sr = liquibase_df.groupby('ctx')['successRate'].mean().rename('liquibase_avg_sr')
avg_sr = pd.concat([avg_liquibase_sr, avg_flyway_sr], axis=1).reset_index()

plt.figure(figsize=(10,5))
x = avg_sr['ctx']
plt.bar(x - width/2, avg_sr['liquibase_avg_sr'], width, label='Liquibase')
plt.bar(x + width/2, avg_sr['flyway_avg_sr'],    width, label='Flyway')
plt.xlabel('Context')
plt.ylabel('Average Success Rate (%)')
plt.title('Scenario 1.: Average Success Rate by Context')
plt.xticks(x)
plt.legend()
plt.tight_layout()
