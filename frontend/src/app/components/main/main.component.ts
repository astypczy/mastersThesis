import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastrService } from 'ngx-toastr';

import {RouterLink, RouterOutlet} from '@angular/router';
import {MigrationService, TestResult} from '../../services/migration.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    RouterOutlet
  ],
  templateUrl: './main.component.html'
})
export class MainComponent {
  resultsFlyway: TestResult[]    = [];
  resultsLiquibase: TestResult[] = [];
  resetStatus: number | null     = null;

  constructor(
    private migrationService: MigrationService,
    private toastr: ToastrService
  ) {}

  runTestsFlyway() {
    this.migrationService.runTestsFlyway().subscribe(data => {
      this.resultsFlyway = data;
    });
  }

  runTestsLiquibase() {
    this.migrationService.runTestsLiquibase().subscribe(data => {
      this.resultsLiquibase = data;
    });
  }

  resetDB() {
    this.toastr.info('Resetowanie bazy danych…', 'Proszę czekać');
    console.log('Resetowanie bazy danych…');
    this.migrationService.resetDB().subscribe({
      next: status => {
        this.resetStatus = status;
        this.resultsFlyway = [];
        this.resultsLiquibase = [];
        this.toastr.success('Baza danych została zresetowana', 'Sukces');
        console.log('Baza danych została zresetowana');
      },
      error: err => {
        console.error(err);
        this.toastr.error('Nie udało się zresetować bazy', 'Błąd');
        console.log('Nie udało się zresetować bazy');
      }
    });
  }
}
