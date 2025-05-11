import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {MigrationService} from '../../services/migration.service';
import {RouterLink} from '@angular/router';

@Component({
  selector: 'app-table-preview',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './table-preview.component.html'
})
export class TablePreviewComponent implements OnInit {
  tablesData: Record<string, any[]> = {};
  loading = true;
  errorMessage: string | null = null;

  constructor(private migrationService: MigrationService) {}

  ngOnInit(): void {
    this.migrationService.getTablePreviews().subscribe({
      next: data => {
        this.tablesData = data;
        this.loading = false;
      },
      error: err => {
        this.errorMessage = 'Nie udało się załadować danych z bazy.';
        this.loading = false;
        console.error(err);
      }
    });
  }

  protected readonly Object = Object;
}
