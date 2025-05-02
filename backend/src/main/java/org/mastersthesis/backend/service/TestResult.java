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
}
