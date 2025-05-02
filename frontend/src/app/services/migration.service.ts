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

@Injectable({ providedIn: 'root' })
export class MigrationService {
  constructor(private http: HttpClient) { }
  runTests(): Observable<TestResult[]> {
    return this.http.get<TestResult[]>('/api/run-tests');
  }
}
