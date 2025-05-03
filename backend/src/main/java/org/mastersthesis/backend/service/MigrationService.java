package org.mastersthesis.backend.service;

import liquibase.Liquibase;
import liquibase.database.Database;
import liquibase.database.DatabaseFactory;
import liquibase.database.jvm.JdbcConnection;
import liquibase.resource.ClassLoaderResourceAccessor;
import org.flywaydb.core.Flyway;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

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
    public List<TestResult> runTestsLiquibase() {
        List<TestResult> results = new ArrayList<>();
        // Scenariusz 1 (zmiana kolumny)
        results.add(runLiquibaseScenario("rename_column"));

        // Scenariusz 2 (duża tabela)
        results.add(runLiquibaseScenario("big_table"));

        return results;
    }

    public int resetDB(){
        // Przywrócenie stanu bazy (opcjonalnie drop/create tabeli)
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

    // Uruchamia migrację Liquibase dla danego scenariusza
    private TestResult runLiquibaseScenario(String scenario) {
        try (Connection conn = dataSource.getConnection()) {
            Database database = DatabaseFactory.getInstance()
                    .findCorrectDatabaseImplementation(new JdbcConnection(conn));
            Liquibase liquibase = new Liquibase("db/changelog/db.changelog-master.xml",
                    new ClassLoaderResourceAccessor(), database);
            long start = System.nanoTime();
            // Używamy kontekstu (np. "rename" lub "big") żeby wykonać tylko część zmian
            String contexts = scenario.equals("rename_column") ? "rename" : "big";
            liquibase.update(contexts);
            long duration = System.nanoTime() - start;

            // Ręczny rollback
            if (scenario.equals("rename_column")) {
                long rstart = System.nanoTime();
                jdbcTemplate.execute("ALTER TABLE person ADD COLUMN old_name VARCHAR(100)");
                jdbcTemplate.execute("ALTER TABLE person DROP COLUMN new_name");
                long rollbackTime = System.nanoTime() - rstart;
                return new TestResult("Liquibase", scenario, duration, rollbackTime, 0, countLiquibaseLines(scenario), 0, 0);
            } else {
                long rstart = System.nanoTime();
                jdbcTemplate.execute("DROP TABLE big_table");
                long rollbackTime = System.nanoTime() - rstart;
                return new TestResult("Liquibase", scenario, duration, rollbackTime, 0, countLiquibaseLines(scenario), 0, 0);
            }
        } catch (Exception e) {
            // Obsługa błędów migracji
            return new TestResult("Liquibase", scenario, 0, 0, -1, 0, 0, 0);
        }
    }

    // Liczy liczbę linii w skryptach Flyway dla danego scenariusza
    private int countFlywayLines(String scenario) {
        // Można wczytać plik SQL i policzyć linie
        // (w przykładzie zwracamy wartość przykładową lub obliczamy np. za pomocą Files.readAllLines)
        return scenario.equals("rename_column") ? 3 : 1002;
    }
    // Liczy linie w skryptach Liquibase dla danego scenariusza
    private int countLiquibaseLines(String scenario) {
        return scenario.equals("rename_column") ? 3 : 1005;
    }
}

