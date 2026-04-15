import { Component, inject, signal } from '@angular/core';
import { FormsModule, ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { NgIf } from '@angular/common';
import { AuthService, UserRole } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, NgIf],
  template: `
    <h1>Acceso y roles</h1>
    <form class="card" [formGroup]="form" style="max-width:420px;display:grid;gap:.7rem;" (ngSubmit)="login()">
      <label>Correo<input type="email" formControlName="email"></label>
      <label>Contraseña<input type="password" formControlName="password"></label>
      <label>Rol
        <select [(ngModel)]="role" [ngModelOptions]="{ standalone: true }">
          <option value="admin">Admin</option>
          <option value="operador">Operador</option>
          <option value="supervisor">Supervisor</option>
        </select>
      </label>
      <button class="btn" [disabled]="form.invalid">Ingresar</button>
      <p *ngIf="lastLogin()">Último acceso: {{ lastLogin() }}</p>
    </form>
  `,
})
export class AuthComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly notifications = inject(NotificationService);

  readonly lastLogin = signal('');
  role: UserRole = 'admin';

  readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  login(): void {
    const email = this.form.getRawValue().email;
    const username = email.split('@')[0] || 'Operador';
    this.auth.login(username, this.role);
    this.lastLogin.set(new Date().toLocaleString());
    this.notifications.push({ type: 'success', title: 'Acceso concedido', message: `Sesión iniciada como ${this.role}` });
  }
}
