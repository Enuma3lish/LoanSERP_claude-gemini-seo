import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, DashboardComponent],
  template: `
    <div class="app">
      <app-dashboard></app-dashboard>
    </div>
  `,
  styles: [`
    .app {
      min-height: 100vh;
    }
  `]
})
export class AppComponent {
  title = 'LoanSERP Analytics Dashboard';
}
