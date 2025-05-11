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

    @GetMapping("/run-tests/Liquibase/1")
    public List<TestResult> runTestsLiquibase_1() {
        return migrationService.runTestsLiquibase_1();
    }
    @GetMapping("/run-tests/Liquibase/2")
    public List<TestResult> runTestsLiquibase_2() {
        return migrationService.runTestsLiquibase_2();
    }
    @GetMapping("/run-tests/Liquibase/3")
    public List<TestResult> runTestsLiquibase_3() {
        return migrationService.runTestsLiquibase_3();
    }
    @GetMapping("/run-tests/Liquibase/4")
    public List<TestResult> runTestsLiquibase_4() {
        return migrationService.runTestsLiquibase_4();
    }
    @GetMapping("/run-tests/Liquibase/5")
    public List<TestResult> runTestsLiquibase_5() {
        return migrationService.runTestsLiquibase_5();
    }
    @GetMapping("/run-tests/Liquibase/6")
    public List<TestResult> runTestsLiquibase_6() {
        return migrationService.runTestsLiquibase_6();
    }
    @GetMapping("/run-tests/reset")
    public int resetDataBase() {
        return migrationService.resetDB();
    }
//    @GetMapping("/preview")
//    public ResponseEntity<Map<String, List<Map<String, Object>>>> previewTables() {
//        List<String> tables = List.of("person", "address", "orders");
//        Map<String, List<Map<String, Object>>> data = new HashMap<>();
//
//        JdbcTemplate jdbc = new JdbcTemplate(dataSource);
//
//        for (String table : tables) {
//            data.put(table, jdbc.queryForList("SELECT * FROM " + table + " LIMIT 5"));
//        }
//
//        try {
//            jdbc.queryForList("SELECT * FROM big_table LIMIT 1");
//            data.put("big_table", jdbc.queryForList("SELECT * FROM big_table LIMIT 5"));
//        } catch (Exception e) {
//            data.put("big_table", List.of(Map.of("info", "Tabela nie istnieje")));
//        }
//
//        return ResponseEntity.ok(data);
//    }

}
