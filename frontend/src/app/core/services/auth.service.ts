import { Injectable, computed, signal } from '@angular/core';

export type UserRole = 'admin' | 'operador' | 'supervisor';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly roleState = signal<UserRole>('admin');
  private readonly usernameState = signal('Usuario Demo');

  readonly role = computed(() => this.roleState());
  readonly username = computed(() => this.usernameState());
  readonly isAdmin = computed(() => this.roleState() === 'admin');

  setRole(role: UserRole): void {
    this.roleState.set(role);
  }

  login(username: string, role: UserRole): void {
    this.usernameState.set(username);
    this.roleState.set(role);
  }
}
