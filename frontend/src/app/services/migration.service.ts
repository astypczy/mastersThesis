import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface TestResult {
  tool: string;
  scenario: string;
  migrationTimeNs: number;
  rollbackTimeNs: number;
  exitCode: number;
  scriptLines: number;
  cpuUsage: number;
  memoryUsage: number;
  successRate?: number;
}

@Injectable({
  providedIn: 'root'
})
export class MigrationService {
  private apiUrl = 'http://localhost:8080';
  constructor(private http: HttpClient) { }
  runTestsLiquibaseS1(): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Liquibase/scenario1`);
  }
  resetDB(): Observable<number> {
    return this.http.get<number>(`${this.apiUrl}/api/run-tests/reset`);
  }
  getTablePreviews(): Observable<Record<string, any[]>> {
    return this.http.get<Record<string, any[]>>('/api/preview');
  }

  runTestsLiquibaseStep(step: number): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Liquibase/${step}`);
  }
  runLiquibaseRollback(context: number): Observable<TestResult> {
    return this.http.get<TestResult>(`${this.apiUrl}/api/run-tests/Liquibase/rollback/${context}`);
  }

  runLiquibaseScenario1_Iterations(iter: number): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Liquibase/scenario1/${iter}`);
  }

  runLiquibaseScenario2_Iterations(iter: number): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Liquibase/6/${iter}`);
  }

  runTestsFlywayS1(): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Flyway/scenario1`);
  }

  runTestsFlywayStep(step: number): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Flyway/${step}`);
  }

  runFlywayScenario1_Iterations(iter: number): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Flyway/scenario1/${iter}`);
  }

  runFlywayScenario2_Iterations(iter: number): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Flyway/6/${iter}`);
  }

  runFlywayRollback(rollbackContext: number): Observable<TestResult> {
    return this.http.get<TestResult>(`${this.apiUrl}/api/run-tests/Flyway/rollback/${rollbackContext}`);
  }
}

