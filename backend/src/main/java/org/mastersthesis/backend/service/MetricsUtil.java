package org.mastersthesis.backend.service;

import com.sun.management.OperatingSystemMXBean;
import java.lang.management.ManagementFactory;

public class MetricsUtil {

    private static final OperatingSystemMXBean OS_BEAN =
            (OperatingSystemMXBean) ManagementFactory.getOperatingSystemMXBean();

    private static final Runtime RUNTIME = Runtime.getRuntime();

    public static ResourceUsage capture() {
        double cpuLoad = OS_BEAN.getProcessCpuLoad() * 100.0;
        long usedMemory = RUNTIME.totalMemory() - RUNTIME.freeMemory();
        return new ResourceUsage(cpuLoad, usedMemory);
    }
}
