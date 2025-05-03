package org.mastersthesis.backend.controller;
import org.mastersthesis.backend.service.MigrationService;
import org.mastersthesis.backend.service.TestResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:4200")
public class MigrationController {

    @Autowired
    private MigrationService migrationService;

    @GetMapping("/run-tests/Flyway")
    public List<TestResult> runTestsFlyway() {
        return migrationService.runTestsFlyway();
    }

    @GetMapping("/run-tests/Liquibase")
    public List<TestResult> runTestsLiquibase() {
        return migrationService.runTestsLiquibase();
    }
    @GetMapping("/run-tests/reset")
    public int resetDataBase() {
        return migrationService.resetDB();
    }
}
