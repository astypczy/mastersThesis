package org.mastersthesis.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "http://localhost:4200")
public class PreviewController {

    private final JdbcTemplate jdbcTemplate;

    public PreviewController(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @GetMapping("/preview")
    public ResponseEntity<Map<String, List<Map<String, Object>>>> previewTables() {
        List<String> tables = List.of("person", "address", "orders");
        Map<String, List<Map<String, Object>>> data = new HashMap<>();

        for (String table : tables) {
            data.put(table, jdbcTemplate.queryForList("SELECT * FROM " + table + " LIMIT 5"));
        }

        try {
            jdbcTemplate.queryForList("SELECT * FROM big_table LIMIT 1");
            data.put("big_table", jdbcTemplate.queryForList("SELECT * FROM big_table LIMIT 5"));
        } catch (Exception e) {
            data.put("big_table", List.of(Map.of("info", "Tabela nie istnieje")));
        }

        return ResponseEntity.ok(data);
    }
}

