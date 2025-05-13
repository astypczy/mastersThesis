import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastrService } from 'ngx-toastr';

import {RouterLink, RouterOutlet} from '@angular/router';
import {MigrationService, TestResult} from '../../services/migration.service';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterLink,
    FormsModule
  ],
  templateUrl: './main.component.html'
})
export class MainComponent {
  resultsFlyway: TestResult[]    = [];
  resultsLiquibase: TestResult[] = [];
  resetStatus: number | null     = null;
  rollbackContext = 1;
  rollbackResult?: TestResult;
  scenario1_iter_lb = 1;
  scenario2_iter_lb = 1;

  constructor(
    private migrationService: MigrationService,
    private toastr: ToastrService
  ) {}

  runTestsLiquibaseS1() {
    this.migrationService.runTestsLiquibaseS1().subscribe(data => {
      this.resultsLiquibase = data;
    });
  }

  resetDB() {
    this.toastr.info('Resetowanie bazy danych…', 'Proszę czekać', {timeOut: 10000});
    console.log('Resetowanie bazy danych…');
    this.migrationService.resetDB().subscribe({
      next: status => {
        this.resetStatus = status;
        this.resultsFlyway = [];
        this.resultsLiquibase = [];
        this.toastr.success('Baza danych została zresetowana', 'Sukces', {timeOut: 3000});
        console.log('Baza danych została zresetowana');
      },
      error: err => {
        console.error(err);
        this.toastr.error('Nie udało się zresetować bazy', 'Błąd');
        console.log('Nie udało się zresetować bazy');
      }
    });
  }
  runLiquibaseStep(step: number) {
    console.log('Frontend: wywołuję Liquibase step', step);
    this.toastr.info('Liquibase: Wykonuję krok nr ' + step, 'W toku ...')
    this.migrationService.runTestsLiquibaseStep(step)
      .subscribe(res => {
        this.resultsLiquibase = res;
        console.log('Frontend: odpowiedź Liquibase step', res);
        this.toastr.success('Liquibase: Wykonano krok nr ' + step, 'Sukces');
      });
  }

  runLiquibaseRollback(context: number) {
    this.migrationService.runLiquibaseRollback(context).subscribe(res => {
      this.rollbackResult = res;
    });
  }
  runLiquibaseScenario1_Iterations(iter: number) {
    console.log('Frontend: Scen. 1. Liquibase: ', iter);
    this.toastr.info('Liquibase: Scen. 1. Liquibase ' + iter, 'W toku ...')
    this.migrationService.runLiquibaseScenario1_Iterations(iter).subscribe(data => {
      this.resultsLiquibase = data;
      console.log('Frontend: Scen. 1. Liquibase step', data);
      this.toastr.success('Liquibase: Scen. 1. Liquibase: ' + iter + ' iteracji', 'Sukces');
    });
  }

  runLiquibaseScenario2_Iterations(iter: number) {
    console.log('Frontend: Scen. 2. Liquibase: ', iter);
    this.toastr.info('Liquibase: Scen. 2. Liquibase ' + iter, 'W toku ...')
    this.migrationService.runLiquibaseScenario2_Iterations(iter).subscribe(data => {
      this.resultsLiquibase = data;
      console.log('Frontend: Scen. 2. Liquibase step', data);
      this.toastr.success('Liquibase: Scen. 2. Liquibase: ' + iter + ' iteracji', 'Sukces');
    });
  }

  runTestsFlywayS1() {
    this.migrationService.runTestsFlywayS1().subscribe(data => {
      this.resultsFlyway = data;
    });
  }

  runFlywayStep(step: number) {
    console.log('Frontend: wywołuję Flyway step', step);
    this.toastr.info('Flyway: Wykonuję krok nr ' + step, 'W toku ...')
    this.migrationService.runTestsFlywayStep(step)
      .subscribe(res => {
        this.resultsFlyway = res;
        console.log('Frontend: odpowiedź Flyway step', res);
        this.toastr.success('Flyway: Wykonano krok nr ' + step, 'Sukces');
      });
  }

  runFlywayScenario1_Iterations(iter: number) {
    console.log('Frontend: Scen. 1. Flyway: ', iter);
    this.toastr.info('Liquibase: Scen. 1. Flyway ' + iter, 'W toku ...')
    this.migrationService.runFlywayScenario1_Iterations(iter).subscribe(data => {
      this.resultsFlyway = data;
      console.log('Frontend: Scen. 1. Flyway step', data);
      this.toastr.success('Flyway: Scen. 1. Flyway: ' + iter + ' iteracji', 'Sukces');
    });
  }

  runFlywayScenario2_Iterations(iter: number) {
    console.log('Frontend: Scen. 2. Flyway: ', iter);
    this.toastr.info('Flyway: Scen. 2. Flyway ' + iter, 'W toku ...')
    this.migrationService.runFlywayScenario2_Iterations(iter).subscribe(data => {
      this.resultsFlyway = data;
      console.log('Frontend: Scen. 2. Flyway step', data);
      this.toastr.success('Flyway: Scen. 2. Flyway: ' + iter + ' iteracji', 'Sukces');
    });
  }

  runFlywayRollback(rollbackContext: number) {
    this.migrationService.runFlywayRollback(rollbackContext).subscribe(res => {
      this.rollbackResult = res;
    });
  }
}

