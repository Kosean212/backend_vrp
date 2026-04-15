import { Injectable, signal } from '@angular/core';

export interface UiNotification {
  id: number;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
}

@Injectable({ providedIn: 'root' })
export class NotificationService {
  readonly notifications = signal<UiNotification[]>([]);

  push(payload: Omit<UiNotification, 'id'>): void {
    const id = Date.now() + Math.floor(Math.random() * 999);
    this.notifications.update(n => [...n, { id, ...payload }]);
    setTimeout(() => this.dismiss(id), 5000);
  }

  dismiss(id: number): void {
    this.notifications.update(n => n.filter(item => item.id !== id));
  }
}
