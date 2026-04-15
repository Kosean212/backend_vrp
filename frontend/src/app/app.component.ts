import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidebarComponent } from './core/layout/sidebar.component';
import { ToastComponent } from './shared/components/toast.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, SidebarComponent, ToastComponent],
  template: `
    <div style="display:grid;grid-template-columns:270px 1fr;min-height:100vh;">
      <app-sidebar />
      <main style="padding:1.2rem;overflow:auto;">
        <router-outlet />
      </main>
    </div>
    <app-toast />
  `,
})
export class AppComponent {}
