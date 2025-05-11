package org.mastersthesis.backend.service;

import liquibase.Liquibase;
import liquibase.database.Database;
import liquibase.database.DatabaseFactory;
import liquibase.database.jvm.JdbcConnection;
import liquibase.exception.DatabaseException;
import liquibase.resource.ClassLoaderResourceAccessor;
import org.flywaydb.core.Flyway;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.sql.Connection;
import java.util.*;
import javax.sql.DataSource;

import java.io.IOException;
import java.lang.InterruptedException;

@Service
public class MigrationService {
    private DataSource dataSource;
    private JdbcTemplate jdbcTemplate;

    @Autowired
    public MigrationService(DataSource dataSource, JdbcTemplate jdbcTemplate) {
        this.dataSource   = dataSource;
        this.jdbcTemplate = jdbcTemplate;
    }
    public List<TestResult> runTestsFlyway() {
        List<TestResult> results = new ArrayList<>();
        // Scenariusz 1 (zmiana kolumny)
        results.add(runFlywayScenario("rename_column"));
        // Scenariusz 2 (duża tabela)
        results.add(runFlywayScenario("big_table"));
        return results;
    }

    public int resetDB(){
        resetDatabaseSchema();
        return 1;
    }

    private void resetDatabaseSchema() {
        jdbcTemplate.execute("DROP TABLE IF EXISTS big_table CASCADE");
        jdbcTemplate.execute("DROP TABLE IF EXISTS person CASCADE");

        try {
            ProcessBuilder pb = new ProcessBuilder("python",
                    "D:\\Dokumenty\\Studia\\mag\\Praca magisterska\\Kod\\mastersThesis\\sql\\addData.py");
            pb.inheritIO();
            Process process = pb.start();
            int exitCode = process.waitFor();

            if (exitCode == 0) {
                System.out.println("Skrypt Python został pomyślnie wykonany.");
            } else {
                System.err.println("Skrypt Python zakończył się błędem. Kod wyjścia: " + exitCode);
            }
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }
    }

    // Uruchamia migrację Flyway dla danego scenariusza
    private TestResult runFlywayScenario(String scenario) {
        // Konfiguracja Flyway (czyszczenie bazy, lokalizacja skryptów)
        Flyway flyway = Flyway.configure()
                .dataSource(dataSource)
                .locations("classpath:db/migration")
                .load();
        flyway.clean();  // czyść schemat bazy przed migracją

        long start = System.nanoTime();
        flyway.migrate();  // wykonaj migracje
        long duration = System.nanoTime() - start;

        // Opcjonalnie: rollback ręczny (przywrócenie zmian)
        if (scenario.equals("rename_column")) {
            long rstart = System.nanoTime();
            jdbcTemplate.execute("ALTER TABLE person ADD COLUMN old_name VARCHAR(100)");
            jdbcTemplate.execute("ALTER TABLE person DROP COLUMN new_name");
            long rollbackTime = System.nanoTime() - rstart;
            return new TestResult("Flyway", scenario, duration, rollbackTime, 0 /*exit*/, countFlywayLines(scenario), 0, 0);
        } else {
            long rstart = System.nanoTime();
            jdbcTemplate.execute("DROP TABLE big_table");
            long rollbackTime = System.nanoTime() - rstart;
            return new TestResult("Flyway", scenario, duration, rollbackTime, 0, countFlywayLines(scenario), 0, 0);
        }
    }
    public TestResult runLiquibaseScenario(String context) {
        try (Connection conn = dataSource.getConnection()) {
            Liquibase lb = createLiquibase(conn);
            System.out.println(">>> Liquibase.update context=" + context);

            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();

            long start = System.nanoTime();
            lb.update(context);
            long duration = System.nanoTime() - start;

            monitor.stop();
            Thread.sleep(200);

            double avgCpu = monitor.getAverageCpu();
            long avgMemory = monitor.getAverageMemory();

            return new TestResult("Liquibase", context, duration, 0, 0, countLiquibaseLines(context), avgCpu, avgMemory);
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Liquibase", context, 0, 0, -1, 0, 0, 0);
        }
    }

    private Liquibase createLiquibase(Connection conn) throws DatabaseException {
        Database db = DatabaseFactory.getInstance()
                .findCorrectDatabaseImplementation(new JdbcConnection(conn));
        return new Liquibase(
                "db/changelog/db.changelog-master.xml",
                new ClassLoaderResourceAccessor(),
                db
        );
    }

    public TestResult runLiquibaseRollback(String context) {
        try (Connection conn = dataSource.getConnection()) {
            Liquibase lb = createLiquibase(conn);

            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();
            long start = System.nanoTime();
            lb.rollback(1, context);
            long rollbackTime = System.nanoTime() - start;
            monitor.stop();
            Thread.sleep(200);

            double avgCpu = monitor.getAverageCpu();
            long avgMemory = monitor.getAverageMemory();

            return new TestResult("Liquibase-Rollback", context, 0, rollbackTime, 0, countLiquibaseLines(context), avgCpu, avgMemory);
        } catch (Exception e) {
            return new TestResult("Liquibase-Rollback", context, 0, 0, -1, 0, 0, 0);
        }
    }


    // Liczy liczbę linii w skryptach Flyway dla danego scenariusza
    private int countFlywayLines(String scenario) {
        // Można wczytać plik SQL i policzyć linie
        // (w przykładzie zwracamy wartość przykładową lub obliczamy np. za pomocą Files.readAllLines)
        return scenario.equals("rename_column") ? 3 : 1002;
    }

    private int countLiquibaseLines(String context) {
        String beginMarker = "<changeSet";
        String ctxAttr    = "context=\"" + context + "\"";
        String endMarker  = "</changeSet>";

        try (InputStream is = getClass().getClassLoader()
                .getResourceAsStream("db/changelog/db.changelog-master.xml");
             BufferedReader reader = new BufferedReader(new InputStreamReader(is))) {

            boolean inBlock = false;
            int count = 0;
            String line;
            while ((line = reader.readLine()) != null) {
                if (!inBlock) {
                    if (line.contains(beginMarker) && line.contains(ctxAttr)) {
                        inBlock = true;
                    }
                } else {
                    if (line.contains(endMarker)) {
                        break;
                    }
                    count++;
                }
            }
            return count;
        } catch (Exception e) {
            return 0;
        }
    }

    public TestResult runLiquibaseScenario1() {
        List<String> contexts = List.of("1", "2", "3", "4", "5");
        List<String> contextsRB = List.of("5", "4", "3", "2", "1");
        long totalMigrationTime = 0;
        long totalRollbackTime  = 0;

        try (Connection conn = dataSource.getConnection()) {
            Liquibase lb = createLiquibase(conn);
            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();

            for (String ctx : contexts) {
                long start = System.nanoTime();
                lb.update(ctx);
                totalMigrationTime += System.nanoTime() - start;
            }

            for (String ctx : contextsRB) {
                long rstart = System.nanoTime();
                lb.rollback(1, ctx);
                totalRollbackTime += System.nanoTime() - rstart;
            }

            monitor.stop();
            Thread.sleep(200);

            double avgCpu = monitor.getAverageCpu();
            long avgMemory = monitor.getAverageMemory();

            int totalLines = 0;
            for (String ctx : contexts) {
                totalLines += countLiquibaseLines(ctx);
            }

            return new TestResult("Liquibase-Group1-5", "1-5", totalMigrationTime, totalRollbackTime,  0, totalLines, avgCpu,  avgMemory
            );
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Liquibase-Group1-5", "1-5", 0, 0, -1, 0, 0, 0);
        }
    }

    public TestResult runLiquibaseScenario2() {
        long totalMigrationTime = 0;
        long totalRollbackTime  = 0;

        try (Connection conn = dataSource.getConnection()) {
            Liquibase lb = createLiquibase(conn);
            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();

            long start = System.nanoTime();
            lb.update("6");
            totalMigrationTime += System.nanoTime() - start;

            long rstart = System.nanoTime();
            lb.rollback(1, "6");
            totalRollbackTime += System.nanoTime() - rstart;

            monitor.stop();
            Thread.sleep(200);

            double avgCpu = monitor.getAverageCpu();
            long avgMemory = monitor.getAverageMemory();

            int totalLines = 0;
            totalLines += countLiquibaseLines("6");


            return new TestResult("Liquibase-Group6", "6", totalMigrationTime, totalRollbackTime,  0, totalLines, avgCpu,  avgMemory
            );
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Liquibase-Group6", "6", 0, 0, -1, 0, 0, 0);
        }
    }

    public TestResult runLiquibaseScenario1Average(int repetitions) {
        long sumMigrationTime = 0;
        long sumRollbackTime = 0;
        double sumCpu = 0.0;
        long sumMemory = 0;
        int sumLines = 0;
        int successCount = 0;
        System.out.println(">>> Liquibase.runLiquibaseScenario1Average - reset");
        resetDB();
        for (int i = 0; i < repetitions; i++) {
//            resetDB();
            TestResult result = runLiquibaseScenario1();

            if (result.getExitCode() == 0) {
                successCount++;
                sumMigrationTime += result.getMigrationTimeNs();
                sumRollbackTime  += result.getRollbackTimeNs();
                sumCpu           += result.getCpuUsage();
                sumMemory        += result.getMemoryUsage();
                sumLines         += result.getScriptLines();
            } else {
                System.out.println("Iteracja " + i + " zakończona błędem.");
            }
            System.out.println(">>> Liquibase.runLiquibaseScenario1Average - " + i + " - done");
        }

        if (successCount == 0) return new TestResult("Liquibase-AVG-"+repetitions+" iteracji", "1-5", 0, 0, -1, 0, 0, 0);

        return new TestResult(
                "Liquibase-AVG-"+repetitions+" iteracji",
                "Liquibase-AVG-"+repetitions+" iteracji scen. 1",
                sumMigrationTime / successCount,
                sumRollbackTime / successCount,
                0,
                sumLines / successCount,
                sumCpu / successCount,
                sumMemory / successCount,
                ((double) successCount / repetitions) * 100.0

        );
    }
    public TestResult runLiquibaseScenario2Average(int repetitions) {
        long sumMigrationTime = 0;
        long sumRollbackTime = 0;
        double sumCpu = 0.0;
        long sumMemory = 0;
        int sumLines = 0;
        int successCount = 0;
        System.out.println(">>> Liquibase.runLiquibaseScenario2Average - reset");
        resetDB();
        for (int i = 0; i < repetitions; i++) {
//            resetDB();

            TestResult result = runLiquibaseScenario2();

            if (result.getExitCode() == 0) {
                successCount++;
                sumMigrationTime += result.getMigrationTimeNs();
                sumRollbackTime  += result.getRollbackTimeNs();
                sumCpu           += result.getCpuUsage();
                sumMemory        += result.getMemoryUsage();
                sumLines         += result.getScriptLines();
            } else {
                System.out.println("Iteracja " + i + " zakończona błędem.");
            }

            System.out.println(">>> Liquibase.runLiquibaseScenario2Average - " + i + " - done");
        }

        if (successCount == 0) return new TestResult("Liquibase-AVG-"+repetitions+" iteracji", "scen. 2 (ctx 6.)", 0, 0, -1, 0, 0, 0);

        return new TestResult(
                "Liquibase-AVG-"+repetitions+" iteracji",
                "Liquibase-AVG-"+repetitions+" iteracji scen. 2 (ctx 6.)",
                sumMigrationTime / successCount,
                sumRollbackTime / successCount,
                0,
                sumLines / successCount,
                sumCpu / successCount,
                sumMemory / successCount,
                ((double) successCount / repetitions) * 100.0
        );
    }
}

