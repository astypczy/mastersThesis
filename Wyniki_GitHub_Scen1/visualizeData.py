import pandas as pd
import matplotlib.pyplot as plt

flyway_data = pd.read_csv('flyway.csv')
liquibase_data = pd.read_csv('liquibase.csv')

flyway_data['ctx'] = flyway_data['ctx'] - 1

# Merge on scenario and ctx for migration times
merged_mig = pd.merge(
    liquibase_data[['scenario', 'ctx', 'migrationTimeNs']],
    flyway_data[['scenario', 'ctx', 'migrationTimeNs']],
    on=['scenario', 'ctx'],
    suffixes=('_liquibase', '_flyway')
)

# Plot migration times
plt.figure()
plt.plot(merged_mig['ctx'], merged_mig['migrationTimeNs_liquibase'], label='Liquibase')
plt.plot(merged_mig['ctx'], merged_mig['migrationTimeNs_flyway'], label='Flyway')
plt.xlabel('Context')
plt.ylabel('Migration Time (ns)')
plt.title('Migration Time by Context')
plt.legend()
plt.tight_layout()
plt.show()

# Merge for rollback times
merged_rollback = pd.merge(
    liquibase_data[['scenario', 'ctx', 'rollbackTimeNs']],
    flyway_data[['scenario', 'ctx', 'rollbackTimeNs']],
    on=['scenario', 'ctx'],
    suffixes=('_liquibase', '_flyway')
)

# Plot rollback times
plt.figure()
plt.plot(merged_rollback['ctx'], merged_rollback['rollbackTimeNs_liquibase'], label='Liquibase')
plt.plot(merged_rollback['ctx'], merged_rollback['rollbackTimeNs_flyway'], label='Flyway')
plt.xlabel('Context')
plt.ylabel('Rollback Time (ns)')
plt.title('Rollback Time by Context')
plt.legend()
plt.tight_layout()
plt.show()
