import time
import requests
import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# --- CONFIG ---
BASE_URL   = "http://localhost:8080/api"
ENDPOINT   = "/run-tests/Liquibase/scenario2" 
ITERATIONS = 2

RAW_CSV     = "results_liquibase_scenario2.csv"
SUMMARY_CSV = "summary_liquibase_scenario2.csv"
AVG_PNG     = "avg_migration_latency_liquibase_scenario2.png"
HIST_PNG    = "migration_latency_histogram_liquibase_scenario2.png"

# CSV column headers
RAW_HEADERS = [
    "iteration", "tool", "scenario", "ctx",
    "migrationTimeNs", "rollbackTimeNs", "exitCode",
    "scriptLines", "cpuUsage", "memoryUsage", "successRate"
]

SUMMARY_HEADERS = [
    "iterations", "mean_migration_ns", "median_migration_ns", "stddev_migration_ns",
    "min_migration_ns", "max_migration_ns", "mean_rollback_ns", "success_rate_pct"
]

def ensure_csv_headers():
    if not os.path.exists(RAW_CSV):
        with open(RAW_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(RAW_HEADERS)
    if not os.path.exists(SUMMARY_CSV):
        with open(SUMMARY_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(SUMMARY_HEADERS)


def measure_and_record(n):
    results = []
    ensure_csv_headers()
    with open(RAW_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        for i in range(1, n+1):
            # call average endpoint per iteration to include all metrics
            url = f"{BASE_URL}{ENDPOINT}"  
            start = time.perf_counter_ns()
            resp = requests.get(url)
            elapsed = time.perf_counter_ns() - start

            if resp.status_code != 200:
                print(f"Request {i} failed: HTTP {resp.status_code}")
                continue

            # parse JSON array with TestResult
            data = resp.json()[0]
            # merge perf_counter latency override or use migrationTimeNs
            migration_ns = data.get("migrationTimeNs", elapsed)
            rollback_ns  = data.get("rollbackTimeNs", 0)

            row = [
                i,
                data.get("tool"),
                data.get("scenario"),
                data.get("ctx"),
                migration_ns,
                rollback_ns,
                data.get("exitCode"),
                data.get("scriptLines"),
                data.get("cpuUsage"),
                data.get("memoryUsage"),
                data.get("successRate", np.nan)
            ]

            results.append(migration_ns)
            writer.writerow(row)

            if i % 10 == 0:
                print(f"→ Completed {i}/{n}")

    return np.array(results, dtype=np.float64)


def summarize_and_record(migration_times, n):
    valid = migration_times[~np.isnan(migration_times)]
    mean   = np.mean(valid)
    median = np.median(valid)
    std    = np.std(valid)
    mn     = np.min(valid)
    mx     = np.max(valid)

    # compute success rate from RAW_CSV entries
    with open(RAW_CSV) as f:
        reader = csv.DictReader(f)
        total = 0
        successes = 0
        for row in reader:
            total += 1
            if int(row['exitCode']) == 0:
                successes += 1
    success_rate = (successes / total * 100) if total else 0

    with open(SUMMARY_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([n, mean, median, std, mn, mx, np.nan, success_rate])

    return mean, median, std, mn, mx, success_rate


def plot_results(migration_times):
    valid = migration_times[~np.isnan(migration_times)]
    running_avg = np.cumsum(valid) / np.arange(1, len(valid)+1)

    # Running average plot
    plt.figure(figsize=(10,4))
    plt.plot(running_avg, label="Avg Migration Latency (ns)")
    plt.xlabel("Iteration #")
    plt.ylabel("Avg Migration Latency (ns)")
    plt.title(f"Liquibase Scenario2 ({ITERATIONS} runs): Running Avg Migration Latency")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(AVG_PNG)
    plt.clf()

    # Histogram of migration latencies
    plt.figure(figsize=(6,4))
    plt.hist(valid, bins=50)
    plt.xlabel("Migration Latency (ns)")
    plt.ylabel("Frequency")
    plt.title(f"Liquibase Scenario2 ({ITERATIONS} runs): Migration Latency Distribution")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(HIST_PNG)
    plt.clf()


def main():
    print(f"Starting Liquibase benchmark: {ITERATIONS} runs of {ENDPOINT}")
    migration_times = measure_and_record(ITERATIONS)
    print("Done measurements. Computing summary and plots...")
    summarize_and_record(migration_times, ITERATIONS)
    plot_results(migration_times)
    print(f"Raw data → {RAW_CSV}")
    print(f"Summary   → {SUMMARY_CSV}")
    print(f"Plots     → {AVG_PNG}, {HIST_PNG}")


if __name__ == "__main__":
    main()
