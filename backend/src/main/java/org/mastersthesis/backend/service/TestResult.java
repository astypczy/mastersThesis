package org.mastersthesis.backend.service;

public class TestResult {
    public String tool;
    public String scenario;
    public long migrationTimeNs;
    public long rollbackTimeNs;
    public int exitCode;
    public int scriptLines;
    public double cpuUsage;
    public long memoryUsage;
    public Double successRate;

    public TestResult(String tool, String scenario, long migrationTimeNs, long rollbackTimeNs,
                      int exitCode, int scriptLines, double cpuUsage, long memoryUsage) {
        this.tool = tool;
        this.scenario = scenario;
        this.migrationTimeNs = migrationTimeNs;
        this.rollbackTimeNs = rollbackTimeNs;
        this.exitCode = exitCode;
        this.scriptLines = scriptLines;
        this.cpuUsage = cpuUsage;
        this.memoryUsage = memoryUsage;
    }
    public TestResult(String tool, String scenario, long migrationTimeNs, long rollbackTimeNs,
                      int exitCode, int scriptLines, double cpuUsage, long memoryUsage, Double successRate) {
        this(tool, scenario, migrationTimeNs, rollbackTimeNs, exitCode, scriptLines, cpuUsage, memoryUsage);
        this.successRate = successRate;
    }

    public String getTool() {
        return tool;
    }

    public void setTool(String tool) {
        this.tool = tool;
    }

    public long getMemoryUsage() {
        return memoryUsage;
    }

    public void setMemoryUsage(long memoryUsage) {
        this.memoryUsage = memoryUsage;
    }

    public double getCpuUsage() {
        return cpuUsage;
    }

    public void setCpuUsage(double cpuUsage) {
        this.cpuUsage = cpuUsage;
    }

    public int getScriptLines() {
        return scriptLines;
    }

    public void setScriptLines(int scriptLines) {
        this.scriptLines = scriptLines;
    }

    public int getExitCode() {
        return exitCode;
    }

    public void setExitCode(int exitCode) {
        this.exitCode = exitCode;
    }

    public long getRollbackTimeNs() {
        return rollbackTimeNs;
    }

    public void setRollbackTimeNs(long rollbackTimeNs) {
        this.rollbackTimeNs = rollbackTimeNs;
    }

    public long getMigrationTimeNs() {
        return migrationTimeNs;
    }

    public void setMigrationTimeNs(long migrationTimeNs) {
        this.migrationTimeNs = migrationTimeNs;
    }

    public String getScenario() {
        return scenario;
    }

    public void setScenario(String scenario) {
        this.scenario = scenario;
    }
    public Double getSuccessRate() {
        return successRate;
    }

    public void setSuccessRate(Double successRate) {
        this.successRate = successRate;
    }
}
