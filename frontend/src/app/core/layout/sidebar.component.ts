import { Component, computed, inject, signal } from '@angular/core';
import { TitleCasePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { AuthService, UserRole } from '../services/auth.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, FormsModule, TitleCasePipe],
  template: `
    <aside class="card" style="margin:.8rem;display:flex;flex-direction:column;gap:1rem;">
      <div>
        <h2 style="margin:.2rem 0;">Biochar VRP</h2>
        <small style="color:var(--muted)">{{ auth.username() }} · {{ auth.role() | titlecase }}</small>
      </div>

      <label>Rol activo
        <select [ngModel]="auth.role()" (ngModelChange)="onRoleChange($event)">
          <option value="admin">Admin</option>
          <option value="operador">Operador</option>
          <option value="supervisor">Supervisor</option>
        </select>
      </label>

      <nav style="display:grid;gap:.4rem;">
        <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
        <a routerLink="/routing" routerLinkActive="active">Ruteo</a>
        <a routerLink="/waste-management" routerLinkActive="active">Residuos</a>
        <a routerLink="/biochar-production" routerLinkActive="active">Biochar</a>
        <a routerLink="/reports" routerLinkActive="active">Reportes</a>
        <a routerLink="/auth" routerLinkActive="active">Acceso</a>
      </nav>

      <button class="btn secondary" (click)="toggleDarkMode()">{{ darkLabel() }}</button>
    </aside>
  `,
  styles: [
    `a{padding:.55rem .7rem;border-radius:8px;color:var(--text);text-decoration:none} a.active{background:#dbeafe;color:#1d4ed8}`,
  ],
})
export class SidebarComponent {
  readonly auth = inject(AuthService);
  private readonly isDark = signal(false);
  readonly darkLabel = computed(() => this.isDark() ? 'Modo claro' : 'Modo oscuro');

  toggleDarkMode(): void {
    this.isDark.update(v => !v);
    document.body.classList.toggle('dark', this.isDark());
  }

  onRoleChange(role: UserRole): void {
    this.auth.setRole(role);
  }
}
