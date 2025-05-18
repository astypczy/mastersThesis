package org.mastersthesis.backend.controller;
import org.mastersthesis.backend.service.MigrationService;
import org.mastersthesis.backend.service.TestResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:4200")
public class MigrationController {

    @Autowired
    private MigrationService migrationService;

    @GetMapping("/run-tests/Liquibase/{id}")
    public List<TestResult> runTestsLiquibaseById(@PathVariable String id) {
        return List.of(migrationService.runLiquibaseScenario(id));
    }
    @GetMapping("/run-tests/Liquibase/scenario2/{n}")
    public List<TestResult> runLiquibaseScenario2Average(@PathVariable String n) {
        return List.of(migrationService.runLiquibaseScenario2Average(Integer.parseInt(n)));
    }
    @GetMapping("/run-tests/Liquibase/scenario2")
    public List<TestResult> runLiquibaseScenario2() {
        return List.of(migrationService.runLiquibaseScenario2());
    }
    @GetMapping("/run-tests/Liquibase/scenario1")
    public List<TestResult> runTestsLiquibaseScenario1() {
        return List.of(migrationService.runLiquibaseScenario1());
    }
    @GetMapping("/run-tests/Liquibase/scenario1/{n}")
    public List<TestResult> runLiquibaseScenario1Average(@PathVariable String n) {
        return List.of(migrationService.runLiquibaseScenario1Average(Integer.parseInt(n)));
    }
    @GetMapping("/run-tests/Liquibase/rollback/{id}")
    public TestResult rollbackLiquibaseByContext(@PathVariable String id) {
        return migrationService.runLiquibaseRollback(id);
    }
    @GetMapping("/run-tests/reset")
    public int resetDataBase() {
        return migrationService.resetDB();
    }
    @GetMapping("/run-tests/Flyway/{id}")
    public List<TestResult> runTestsFlywayById(@PathVariable String id) {
        return List.of(migrationService.runFlywayScenario(id));
    }
    @GetMapping("/run-tests/Flyway/scenario2/{n}")
    public List<TestResult> runFlywayScenario2Average(@PathVariable String n) {
        return List.of(migrationService.runFlywayScenario2Average(Integer.parseInt(n)));
    }
    @GetMapping("/run-tests/Flyway/scenario2")
    public List<TestResult> runFlywayScenario2() {
        return List.of(migrationService.runFlywayScenario2());
    }
    @GetMapping("/run-tests/Flyway/scenario1")
    public List<TestResult> runTestsFlywayScenario1() {
        return List.of(migrationService.runFlywayScenario1());
    }
    @GetMapping("/run-tests/Flyway/scenario1/{n}")
    public List<TestResult> runFlywayScenario1Average(@PathVariable String n) {
        return List.of(migrationService.runFlywayScenario1Average(Integer.parseInt(n)));
    }

    @GetMapping("/run-tests/Flyway/rollback/{id}")
    public TestResult rollbackFlywayByContext(@PathVariable String id) {
        return migrationService.runFlywayRollback(id);
    }
}
