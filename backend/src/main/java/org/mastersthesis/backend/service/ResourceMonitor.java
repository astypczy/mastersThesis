package org.mastersthesis.backend.service;

import java.util.ArrayList;
import java.util.List;

public class ResourceMonitor {
    private final List<Double> cpuSamples = new ArrayList<>();
    private final List<Long> memorySamples = new ArrayList<>();
    private volatile boolean running = false;

    public void start() {
        running = true;
        new Thread(() -> {
            while (running) {
                ResourceUsage usage = MetricsUtil.capture();
                cpuSamples.add(usage.getCpuPercent());
                memorySamples.add(usage.getMemoryBytes());
                try {
                    Thread.sleep(100); // co 100ms próbka
                } catch (InterruptedException ignored) {}
            }
        }).start();
    }

    public void stop() {
        running = false;
    }

    public double getAverageCpu() {
        return cpuSamples.stream().mapToDouble(d -> d).average().orElse(0.0);
    }

    public long getAverageMemory() {
        return (long) memorySamples.stream().mapToLong(d -> d).average().orElse(0);
    }
}
