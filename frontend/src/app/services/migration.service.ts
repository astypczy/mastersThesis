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
}

@Injectable({
  providedIn: 'root'
})
export class MigrationService {
  private apiUrl = 'http://localhost:8080';
  constructor(private http: HttpClient) { }
  runTestsFlyway(): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Flyway`);
  }
  runTestsLiquibase(): Observable<TestResult[]> {
    return this.http.get<TestResult[]>(`${this.apiUrl}/api/run-tests/Liquibase`);
  }
  resetDB(): Observable<number> {
    return this.http.get<number>(`${this.apiUrl}/api/run-tests/reset`);
  }
}
