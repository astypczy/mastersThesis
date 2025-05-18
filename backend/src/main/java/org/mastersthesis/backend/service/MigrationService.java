package org.mastersthesis.backend.service;

import liquibase.Liquibase;
import liquibase.database.Database;
import liquibase.database.DatabaseFactory;
import liquibase.database.jvm.JdbcConnection;
import liquibase.exception.DatabaseException;
import liquibase.resource.ClassLoaderResourceAccessor;
import org.flywaydb.core.Flyway;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.init.ScriptUtils;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.Statement;
import java.util.*;
import javax.sql.DataSource;

import java.io.IOException;
import java.lang.InterruptedException;
import java.util.stream.Collectors;

@Service
public class MigrationService {
    private DataSource dataSource;
    private JdbcTemplate jdbcTemplate;

    @Autowired
    public MigrationService(DataSource dataSource, JdbcTemplate jdbcTemplate) {
        this.dataSource   = dataSource;
        this.jdbcTemplate = jdbcTemplate;
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

    public TestResult runFlywayScenario(String context) {
        String script = getFlywayScriptForContext(context);

        try (Connection conn = dataSource.getConnection()) {
            Flyway flyway = Flyway.configure()
                    .dataSource(dataSource)
                    .locations("classpath:db/migration/")
                    .baselineOnMigrate(true)
                    .target(String.valueOf(Integer.parseInt(context)+1))
                    .load();

            System.out.println(">>> Flyway.migrate single script: " + script);

            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();

            long start = System.nanoTime();
            flyway.migrate();
            long migrationTime = System.nanoTime() - start;

            monitor.stop();
            Thread.sleep(200);

            double avgCpu    = monitor.getAverageCpu();
            long   avgMemory = monitor.getAverageMemory();

            int lines = countFlywayLines(script);

            return new TestResult("Flyway", context, migrationTime, 0, 0, lines, avgCpu, avgMemory);
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Flyway", context, 0, 0, -1, 0, 0, 0);
        }
    }

    public TestResult runFlywayRollback(String context) {
        String undoScript = getFlywayScriptForContextRollback(context);
        ClassPathResource resource = new ClassPathResource("db/migration/" + undoScript);

        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement()) {

            System.out.println(">>> Flyway.rollback custom execute: " + undoScript);

            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();

            String sql = new BufferedReader(
                    new InputStreamReader(resource.getInputStream(), StandardCharsets.UTF_8))
                    .lines()
                    .collect(Collectors.joining("\n"));

            long start = System.nanoTime();
            stmt.execute(sql);

            String version = String.valueOf(Integer.parseInt(context) + 1);
            stmt.executeUpdate(
                    "DELETE FROM flyway_schema_history WHERE version = '" + version + "'"
            );
            long rollbackTime = System.nanoTime() - start;

            monitor.stop();
            Thread.sleep(200);

            double avgCpu    = monitor.getAverageCpu();
            long   avgMemory = monitor.getAverageMemory();

            int lines = countFlywayLines(undoScript);
            return new TestResult("Flyway-Rollback", context, 0, rollbackTime, 0, lines, avgCpu, avgMemory);
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Flyway-Rollback", context, 0, 0, -1, 0, 0, 0);
        }
    }


    private int countFlywayLines(String scriptName) {
        boolean inBlockComment = false;
        int count = 0;

        try (InputStream is = getClass().getClassLoader()
                .getResourceAsStream("db/migration/" + scriptName);
             BufferedReader reader = new BufferedReader(new InputStreamReader(is))) {

            String line;
            while ((line = reader.readLine()) != null) {
                String trimmed = line.trim();

                if (inBlockComment) {
                    if (trimmed.endsWith("*/")) {
                        inBlockComment = false;
                    }
                    continue;
                }
                if (trimmed.startsWith("/*")) {
                    inBlockComment = true;
                    continue;
                }

                if (trimmed.isEmpty() || trimmed.startsWith("--")) {
                    continue;
                }

                count++;
            }
        } catch (IOException e) {
            return 0;
        }
        return count;
    }

    public TestResult runFlywayScenario1() {
        List<String> contexts = List.of("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13");
        List<String> contextsRB = List.of("13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1");

        long totalMigrationTime = 0;
        long totalRollbackTime  = 0;
        int  totalLines         = 0;

        try (Connection conn = dataSource.getConnection()) {
            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();
            for (String ctx : contexts) {
                TestResult result = runFlywayScenario(ctx);
                if (result.getExitCode() == 0) {
                    totalMigrationTime += result.getMigrationTimeNs();
                    totalLines         += result.getScriptLines();
                }
            }

            for (String ctx : contextsRB) {
                TestResult result = runFlywayRollback(ctx);
                if (result.getExitCode() == 0) {
                    totalRollbackTime += result.getRollbackTimeNs();
                }
            }
            monitor.stop();
            Thread.sleep(200);
            double avgCpu = monitor.getAverageCpu();
            long avgMemory = monitor.getAverageMemory();

            return new TestResult("Flyway-Group-scen1-1-13", "Flyway-Group-scen1-1-13", totalMigrationTime, totalRollbackTime, 0, totalLines, avgCpu, avgMemory);
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Flyway-Group-scen1-1-13", "Flyway-Group-scen1-1-13", 0, 0, -1, 0, 0, 0);
        }
    }

    public TestResult runFlywayScenario1Average(int repetitions) {
        long sumMigrationTime = 0;
        long sumRollbackTime = 0;
        double sumCpu = 0.0;
        long sumMemory = 0;
        int sumLines = 0;
        int successCount = 0;

        System.out.println(">>> Flyway.runFlywayScenario1Average - reset");
        resetDB();
        for (int i = 0; i < repetitions; i++) {
//            resetDB();
            TestResult result = runFlywayScenario1();

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
            System.out.println(">>> Flyway.runLiquibaseScenario1Average - " + i + " - done");
        }

        if (successCount == 0) return new TestResult("Flyway-AVG-"+repetitions+" iteracji", "Flyway-AVG-"+repetitions+" iteracji scen. 1", 0, 0, -1, 0, 0, 0);

        return new TestResult("Flyway-AVG-"+repetitions+" iteracji", "Flyway-AVG-"+repetitions+" iteracji scen. 1", sumMigrationTime / successCount, sumRollbackTime / successCount, 0, sumLines / successCount, sumCpu / successCount, sumMemory / successCount, ((double) successCount / repetitions) * 100.0);
    }

    public TestResult runFlywayScenario2() {
        List<String> contexts = List.of("14", "15", "16", "17", "18", "19", "20", "21", "22", "23");
        List<String> contextsRB = List.of("23", "22", "21", "20", "19", "18", "17", "16", "15", "14");
        long totalMigrationTime = 0;
        long totalRollbackTime  = 0;
        int  totalLines         = 0;

        try (Connection conn = dataSource.getConnection()) {
            ResourceMonitor monitor = new ResourceMonitor();
            monitor.start();
            for (String ctx : contexts) {
                TestResult result = runFlywayScenario(ctx);
                if (result.getExitCode() == 0) {
                    totalMigrationTime += result.getMigrationTimeNs();
                    totalLines         += result.getScriptLines();
                }
            }

            for (String ctx : contextsRB) {
                TestResult result = runFlywayRollback(ctx);
                if (result.getExitCode() == 0) {
                    totalRollbackTime += result.getRollbackTimeNs();
                }
            }
            monitor.stop();
            Thread.sleep(200);
            double avgCpu = monitor.getAverageCpu();
            long avgMemory = monitor.getAverageMemory();

            return new TestResult("Flyway-Group14-23", "Flyway scen 2 14-23", totalMigrationTime, totalRollbackTime, 0, totalLines, avgCpu, avgMemory);
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Flyway-Group14-23", "Flyway scen 2 14-23", 0, 0, -1, 0, 0, 0);
        }
    }
    public TestResult runFlywayScenario2Average(int repetitions) {
        long sumMigrationTime = 0;
        long sumRollbackTime = 0;
        double sumCpu = 0.0;
        long sumMemory = 0;
        int sumLines = 0;
        int successCount = 0;

        System.out.println(">>> Flyway.runFlywayScenario2Average - reset");
        resetDB();
        for (int i = 0; i < repetitions; i++) {
//            resetDB();
            TestResult result = runFlywayScenario2();

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
            System.out.println(">>> Flyway.runLiquibaseScenario2Average - " + i + " - done");
        }

        if (successCount == 0) return new TestResult("Flyway-AVG-"+repetitions+" iteracji scen 2.", "Flyway Scen. 2 ", 0, 0, -1, 0, 0, 0);

        return new TestResult("Flyway-AVG-"+repetitions+" iteracji", "Flyway-AVG-"+repetitions+" iteracji scen. 2 ", sumMigrationTime / successCount, sumRollbackTime / successCount, 0, sumLines / successCount, sumCpu / successCount, sumMemory / successCount, ((double) successCount / repetitions) * 100.0);
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

            return new TestResult("Liquibase", "Liquibase" + context, duration, 0, 0, countLiquibaseLines(context), avgCpu, avgMemory);
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Liquibase", "Liquibase" + context, 0, 0, -1, 0, 0, 0);
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

            return new TestResult("Liquibase-Rollback", "Liquibase Rollback" + context, 0, rollbackTime, 0, countLiquibaseLines(context), avgCpu, avgMemory);
        } catch (Exception e) {
            return new TestResult("Liquibase-Rollback", "Liquibase Rollback" + context, 0, 0, -1, 0, 0, 0);
        }
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
        List<String> contexts = List.of("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13");
        List<String> contextsRB = List.of("13", "12", "11", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1");
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

            return new TestResult("Liquibase-Group1-5", "Liquibase-Group1-10", totalMigrationTime, totalRollbackTime,  0, totalLines, avgCpu,  avgMemory
            );
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Liquibase-Group1-5", "Liquibase-Group1-10", 0, 0, -1, 0, 0, 0);
        }
    }

    public TestResult runLiquibaseScenario2() {
        List<String> contexts = List.of("14", "15", "16", "17", "18", "19", "20", "21", "22", "23");
        List<String> contextsRB = List.of("23", "22", "21", "20", "19", "18", "17", "16", "15", "14");
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

            return new TestResult("Liquibase-Group_scen2-14-23", "Liquibase-scen2-Group14-23", totalMigrationTime, totalRollbackTime,  0, totalLines, avgCpu,  avgMemory
            );
        } catch (Exception e) {
            e.printStackTrace();
            return new TestResult("Liquibase-Group-scen2-14-23", "Liquibase-Group-scen2-14-23", 0, 0, -1, 0, 0, 0);
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

        if (successCount == 0) return new TestResult("Liquibase-AVG-"+repetitions+" iteracji", "Liquibase-AVG-"+repetitions+" iteracji scen. 1", 0, 0, -1, 0, 0, 0);

        return new TestResult("Liquibase-AVG-"+repetitions+" iteracji", "Liquibase-AVG-"+repetitions+" iteracji scen. 1", sumMigrationTime / successCount, sumRollbackTime / successCount, 0, sumLines / successCount, sumCpu / successCount, sumMemory / successCount, ((double) successCount / repetitions) * 100.0);
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

        return new TestResult("Liquibase-AVG-"+repetitions+" iteracji", "Liquibase-AVG-"+repetitions+" iteracji scen. 2 (ctx 6.)", sumMigrationTime / successCount, sumRollbackTime / successCount, 0, sumLines / successCount, sumCpu / successCount, sumMemory / successCount, ((double) successCount / repetitions) * 100.0 );
    }
    public String getFlywayScriptForContext(String context) {
        switch (context) {
            case "1":
                return "V2__add_new_name.sql";
            case "2":
                return "V3__copy_legacy_to_new.sql";
            case "3":
                return "V4__create_person_sync_function.sql";
            case "4":
                return "V5__create_person_sync_trigger.sql";
            case "5":
                return "V6__drop_legacy_name_column.sql";
            case "6":
                return "V7__disable_legacy_trigger.sql";
            case "7":
                return "V8__split_name_columns.sql";
            case "8":
                return "V9__create_name_sync_function.sql";
            case "9":
                return "V10__create_name_sync_trigger.sql";
            case "10":
                return "V11__add_indexes.sql";
            case "11":
                return "V12__create_audit_table.sql";
            case "12":
                return "V13__create_audit_trigger.sql";
            case "13":
                return "V14__change_type_error.sql";
            case "14":
                return "V15__create_big_table.sql";
            case "15":
                return "V16__insert_batch_1.sql";
            case "16":
                return "V17__insert_batch_2.sql";
            case "17":
                return "V18__update_extra_cols.sql";
            case "18":
                return "V19__insert_batch_3.sql";
            case "19":
                return "V20__delete_batch_1.sql";
            case "20":
                return "V21__insert_batch_4.sql";
            case "21":
                return "V22__delete_batch_2.sql";
            case "22":
                return "V23__insert_batch_5.sql";
            case "23":
                return "V24__analyze_big_table.sql";
            default:
                throw new IllegalArgumentException(
                        "Nieznany kontekst: " + context + ". Oczekiwano wartości od \"1\" do \"23\"."
                );
        }
    }
    public String getFlywayScriptForContextRollback(String context) {
        switch (context) {
            case "1":
                return "U2__undo_add_new_name.sql";
            case "2":
                return "U3__undo_copy_legacy_to_new.sql";
            case "3":
                return "U4__undo_create_person_name_sync_function.sql";
            case "4":
                return "U5__undo_create_person_name_sync_trigger.sql";
            case "5":
                return "U6__undo_init_person.sql";
            case "6":
                return "U7__undo_disable_legacy_trigger.sql";
            case "7":
                return "U8__undo_split_name_columns.sql";
            case "8":
                return "U9__undo_create_name_sync_function.sql";
            case "9":
                return "U10__undo_create_name_sync_trigger.sql";
            case "10":
                return "U11__undo_add_indexes.sql";
            case "11":
                return "U12__undo_create_audit_table.sql";
            case "12":
                return "U13__undo_create_audit_trigger.sql";
            case "13":
                return "U14__undo_change_type_error.sql";
            case "14":
                return "U15__undo_create_big_table.sql";
            case "15":
                return "U16__undo_insert_batch_1.sql";
            case "16":
                return "U17__undo_insert_batch_2.sql";
            case "17":
                return "U18__undo_update_extra_cols.sql";
            case "18":
                return "U19__undo_insert_batch_3.sql";
            case "19":
                return "U20__undo_delete_batch_1.sql";
            case "20":
                return "U21__undo_insert_batch_4.sql";
            case "21":
                return "U22__undo_delete_batch_2.sql";
            case "22":
                return "U23__undo_insert_batch_5.sql";
            case "23":
                return "U24__undo_analyze_big_table.sql";
            default:
                throw new IllegalArgumentException(
                        "Nieznany kontekst: " + context + ". Oczekiwano wartości od \"1\" do \"23\"."
                );
        }
    }
}

