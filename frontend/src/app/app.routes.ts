import { Routes } from '@angular/router';
import {TablePreviewComponent} from './components/table-preview/table-preview.component';
import {MainComponent} from './components/main/main.component';

export const routes: Routes = [
  {path: '', component: MainComponent},
  { path: 'preview', component: TablePreviewComponent }
];

