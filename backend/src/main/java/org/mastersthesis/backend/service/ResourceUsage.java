package org.mastersthesis.backend.service;

public class ResourceUsage {
    private final double cpuPercent;
    private final long memoryBytes;

    public ResourceUsage(double cpuPercent, long memoryBytes) {
        this.cpuPercent = cpuPercent;
        this.memoryBytes = memoryBytes;
    }

    public double getCpuPercent() {
        return cpuPercent;
    }

    public long getMemoryBytes() {
        return memoryBytes;
    }

    @Override
    public String toString() {
        return String.format("CPU: %.1f%%, Memory: %,d B", cpuPercent, memoryBytes);
    }
}
