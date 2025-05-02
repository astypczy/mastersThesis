import { Component } from '@angular/core';
import { MigrationService, TestResult } from './services/migration.service';

@Component({
  selector: 'app-root',
  standalone: true,
  templateUrl: './app.component.html'
})
export class AppComponent {
  results: TestResult[] = [];

  constructor(private migrationService: MigrationService) { }

  runTests() {
    this.migrationService.runTests().subscribe(data => {
      this.results = data;
    });
  }
}
