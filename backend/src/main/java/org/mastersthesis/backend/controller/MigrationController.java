package org.mastersthesis.backend.controller;


import org.mastersthesis.backend.service.MigrationService;
import org.mastersthesis.backend.service.TestResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api")
public class MigrationController {

    @Autowired
    private MigrationService migrationService;

    @GetMapping("/run-tests")
    public List<TestResult> runTests() {
        return migrationService.runAllTests();
    }
}
