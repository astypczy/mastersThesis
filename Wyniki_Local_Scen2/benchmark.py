import requests
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import subprocess, sys

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:8080/api"
TOOLS = {
    "Flyway": {
        "scenario_endpoint": "/run-tests/Flyway/scenario2",
        "context_endpoint": "/run-tests/Flyway/",
        "rollback_endpoint": "/run-tests/Flyway/rollback/",
        "contexts": [str(i) for i in range(14, 24)]
    },
    "Liquibase": {
        "scenario_endpoint": "/run-tests/Liquibase/scenario2",
        "context_endpoint": "/run-tests/Liquibase/",
        "rollback_endpoint": "/run-tests/Liquibase/rollback/",
        "contexts": [str(i) for i in range(14, 24)]
    }
}
NUM_RUNS = 100  # liczba powtórzeń pełnego scenariusza i cykli kontekstów
PHASES = ['full_scenario', 'context_cycles']

# Pliki i szablony
RAW_TEMPLATE      = "benchmark_raw_{phase}.csv"
SUMMARY_TEMPLATE  = "benchmark_summary_{phase}.csv"
PLOT_TIME_FULL    = "benchmark_time_full_{phase}.png"
PLOT_HIST_FULL    = "benchmark_hist_full_{phase}.png"
PLOT_TIME_BAR     = "benchmark_time_bar_{phase}.png"
PLOT_CPU_BAR      = "benchmark_cpu_bar_{phase}.png"
PLOT_MEM_BAR      = "benchmark_mem_bar_{phase}.png"

# Nagłówki CSV
HEADERS_RAW = [
    "tool", "identifier", "context",
    "migration_ns", "rollback_ns", "exit_code",
    "script_lines", "cpu_pct", "mem_bytes", "success_pct"
]
HEADERS_SUMMARY = [
    "tool", "count", "avg_migration_ns", "avg_rollback_ns",
    "avg_cpu_pct", "avg_mem_bytes", "success_pct"
]


def init_files(phase):
    raw_file = RAW_TEMPLATE.format(phase=phase)
    summary_file = SUMMARY_TEMPLATE.format(phase=phase)
    for path, hdrs in ((raw_file, HEADERS_RAW), (summary_file, HEADERS_SUMMARY)):
        if not os.path.exists(path):
            with open(path, 'w', newline='') as f:
                csv.writer(f).writerow(hdrs)
    return raw_file, summary_file


def run_full_scenario(tool, phase):
    raw, summary = init_files(phase)
    records = []
    for i in range(1, NUM_RUNS + 1):
        resp = requests.get(f"{API_BASE_URL}{TOOLS[tool]['scenario_endpoint']}")
        data = extract_data(resp)
        records.append(make_record(tool, f"run{i}", None, data))
    # write raw
    with open(raw, 'a', newline='') as f:
        csv.writer(f).writerows(records)
    # compute averages
    migs = np.array([r[3] for r in records], dtype=np.float64)
    rols = np.array([r[4] for r in records], dtype=np.float64)
    cpus = np.array([r[7] for r in records], dtype=np.float64)
    mems = np.array([r[8] for r in records], dtype=np.float64)
    avg_mig = np.nanmean(migs)
    avg_rol = np.nanmean(rols)
    avg_cpu = np.nanmean(cpus)
    avg_mem = np.nanmean(mems)
    succ_pct = sum(r[5]==0 for r in records)/len(records)*100
    with open(summary, 'a', newline='') as f:
        csv.writer(f).writerow((tool, len(records), avg_mig, avg_rol, avg_cpu, avg_mem, succ_pct))
    return migs, rols, cpus, mems


def run_context_cycles(tool, phase):
    raw, summary = init_files(phase)
    forward, rollback = [], []
    for cycle in range(1, NUM_RUNS + 1):
        for ctx in TOOLS[tool]['contexts']:
            resp = requests.get(f"{API_BASE_URL}{TOOLS[tool]['context_endpoint']}{ctx}")
            data = extract_data(resp)
            forward.append(make_record(tool, f"{cycle}.fwd.{ctx}", ctx, data))
        for ctx in reversed(TOOLS[tool]['contexts']):
            resp = requests.get(f"{API_BASE_URL}{TOOLS[tool]['rollback_endpoint']}{ctx}")
            data = extract_data(resp)
            rollback.append(make_record(tool, f"{cycle}.rbk.{ctx}", ctx, data))
    all_recs = forward + rollback
    with open(raw, 'a', newline='') as f:
        csv.writer(f).writerows(all_recs)
    # compute per-context average
    ctxs = TOOLS[tool]['contexts']
    f_times = np.array([np.nanmean([r[3] for r in forward if r[2]==ctx]) for ctx in ctxs])
    r_times = np.array([np.nanmean([r[4] for r in rollback if r[2]==ctx]) for ctx in ctxs])
    f_cpu   = np.array([np.nanmean([r[7] for r in forward if r[2]==ctx]) for ctx in ctxs])
    r_cpu   = np.array([np.nanmean([r[7] for r in rollback if r[2]==ctx]) for ctx in ctxs])
    f_mem   = np.array([np.nanmean([r[8] for r in forward if r[2]==ctx]) for ctx in ctxs])
    r_mem   = np.array([np.nanmean([r[8] for r in rollback if r[2]==ctx]) for ctx in ctxs])
    # write summary forward+rollback
    with open(summary, 'a', newline='') as f:
        w = csv.writer(f)
        w.writerow((tool+'-forward', len(ctxs), np.mean(f_times), np.nan, np.mean(f_cpu), np.mean(f_mem), np.nan))
        w.writerow((tool+'-rollback', len(ctxs), np.mean(r_times), np.nan, np.mean(r_cpu), np.mean(r_mem), np.nan))
    return ctxs, f_times, r_times, f_cpu, r_cpu, f_mem, r_mem


def extract_data(resp):
    if resp.status_code!=200: return {}
    p = resp.json(); return p[0] if isinstance(p,list) and p else p


def make_record(tool, identifier, ctx, data):
    return (
        tool, identifier, ctx,
        data.get('migrationTimeNs', np.nan),
        data.get('rollbackTimeNs', np.nan),
        data.get('exitCode', -1),
        data.get('scriptLines', 0),
        data.get('cpuUsage', np.nan),
        data.get('memoryUsage', np.nan),
        data.get('successRate', np.nan)
    )


def plot_phase(phase, fly, liq):
    if phase=='full_scenario':
        f_m, f_r, f_cpu, f_mem = fly
        l_m, l_r, l_cpu, l_mem = liq
        # line plot
        plt.figure(figsize=(8,5))
        plt.plot(np.arange(1,len(f_m)+1), f_m, marker='o', label='Flyway migration')
        plt.plot(np.arange(1,len(f_r)+1), f_r, marker='o', label='Flyway rollback')
        plt.plot(np.arange(1,len(l_m)+1), l_m, marker='s', label='Liquibase migration')
        plt.plot(np.arange(1,len(l_r)+1), l_r, marker='s', label='Liquibase rollback')
        plt.title('Full Scenario Times'); plt.xlabel('Run'); plt.ylabel('Time (ns)')
        plt.legend(); plt.grid(True); plt.tight_layout(); plt.savefig(PLOT_TIME_FULL.format(phase=phase)); plt.clf()
        # histogram
        plt.figure(figsize=(8,5))
        plt.hist(f_m, bins=NUM_RUNS, alpha=0.5, label='Flyway mig')
        plt.hist(f_r, bins=NUM_RUNS, alpha=0.5, label='Flyway rbk')
        plt.hist(l_m, bins=NUM_RUNS, alpha=0.5, label='Liquibase mig')
        plt.hist(l_r, bins=NUM_RUNS, alpha=0.5, label='Liquibase rbk')
        plt.title('Full Scenario Distribution'); plt.xlabel('Time (ns)'); plt.ylabel('Freq')
        plt.legend(); plt.tight_layout(); plt.savefig(PLOT_HIST_FULL.format(phase=phase)); plt.clf()
        # CPU/Memory bars
        labels=['Flyway','Liquibase']
        avg_cpu=[np.mean(f_cpu), np.mean(l_cpu)]; avg_mem=[np.mean(f_mem), np.mean(l_mem)]
        plt.figure(figsize=(6,4)); plt.bar(labels, avg_cpu); plt.title('Avg CPU Full'); plt.ylabel('CPU%'); plt.tight_layout(); plt.savefig(PLOT_CPU_BAR.format(phase=phase)); plt.clf()
        plt.figure(figsize=(6,4)); plt.bar(labels, avg_mem); plt.title('Avg Mem Full'); plt.ylabel('Bytes'); plt.tight_layout(); plt.savefig(PLOT_MEM_BAR.format(phase=phase)); plt.clf()
    else:
        ctxs, fm, rm, fc, rc, fm2, rm2 = fly
        _, lm, rr, lc, rc2, lm2, rm3 = liq
        x=np.arange(len(ctxs)); w=0.35
        # time forward/rollback bar charts per context
        plt.figure(figsize=(10,5));
        plt.bar(x-w/2,fm,w,label='Flyway fwd'); plt.bar(x+w/2,lm,w,label='Liqui fwd')
        plt.title('Forward Times'); plt.xticks(x,ctxs,rotation=45); plt.legend(); plt.tight_layout(); plt.savefig(PLOT_TIME_BAR.format(phase=phase)); plt.clf()
        plt.figure(figsize=(10,5));
        plt.bar(x-w/2,rm,w,label='Flyway rbk'); plt.bar(x+w/2,rr,w,label='Liqui rbk')
        plt.title('Rollback Times'); plt.xticks(x,ctxs,rotation=45); plt.legend(); plt.tight_layout(); plt.savefig(PLOT_TIME_BAR.format(phase=phase)+'_rbk.png'); plt.clf()
        # CPU
        plt.figure(figsize=(10,5)); plt.bar(x-w/2,fc,w,label='Flyway fwd'); plt.bar(x+w/2,lc,w,label='Liqui fwd')
        plt.title('Forward CPU'); plt.xticks(x,ctxs,rotation=45); plt.legend(); plt.tight_layout(); plt.savefig(PLOT_CPU_BAR.format(phase=phase)); plt.clf()
        plt.figure(figsize=(10,5)); plt.bar(x-w/2,rc,w,label='Flyway rbk'); plt.bar(x+w/2,rc2,w,label='Liqui rbk')
        plt.title('Rollback CPU'); plt.xticks(x,ctxs,rotation=45); plt.legend(); plt.tight_layout(); plt.savefig(PLOT_CPU_BAR.format(phase=phase)+'_rbk.png'); plt.clf()
        # Memory
        plt.figure(figsize=(10,5)); plt.bar(x-w/2,fm2,w,label='Flyway fwd'); plt.bar(x+w/2,lm2,w,label='Liqui fwd')
        plt.title('Forward Mem'); plt.xticks(x,ctxs,rotation=45); plt.legend(); plt.tight_layout(); plt.savefig(PLOT_MEM_BAR.format(phase=phase)); plt.clf()
        plt.figure(figsize=(10,5)); plt.bar(x-w/2,rm2,w,label='Flyway rbk'); plt.bar(x+w/2,rm3,w,label='Liqui rbk')
        plt.title('Rollback Mem'); plt.xticks(x,ctxs,rotation=45); plt.legend(); plt.tight_layout(); plt.savefig(PLOT_MEM_BAR.format(phase=phase)+'_rbk.png'); plt.clf()


def main():
    print("Scen2 benchmark: " + str(NUM_RUNS) +" loops")
    reset=os.path.join(os.path.dirname(__file__),'sql','addData.py')
    fly_full = run_full_scenario('Flyway','full_scenario')
    if os.path.exists(reset): subprocess.run([sys.executable,reset],check=True)
    liq_full = run_full_scenario('Liquibase','full_scenario')
    plot_phase('full_scenario',fly_full,liq_full)
    if os.path.exists(reset): subprocess.run([sys.executable,reset],check=True)
    fly_ctx = run_context_cycles('Flyway','context_cycles')
    if os.path.exists(reset): subprocess.run([sys.executable,reset],check=True)
    liq_ctx = run_context_cycles('Liquibase','context_cycles')
    plot_phase('context_cycles',fly_ctx,liq_ctx)
    print('Completed')

if __name__=='__main__':
    main()
