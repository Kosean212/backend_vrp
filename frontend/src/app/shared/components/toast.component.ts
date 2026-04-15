import { Component, inject } from '@angular/core';
import { NgFor } from '@angular/common';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [NgFor],
  template: `
    <div style="position:fixed;top:1rem;right:1rem;display:grid;gap:.5rem;z-index:2000;max-width:320px;">
      <article *ngFor="let n of notifications.notifications()" class="card" [style.border-left]="'6px solid ' + color(n.type)">
        <div style="display:flex;justify-content:space-between;gap:.6rem;align-items:flex-start;">
          <div>
            <strong>{{ n.title }}</strong>
            <p style="margin:.3rem 0 0 0;">{{ n.message }}</p>
          </div>
          <button class="btn secondary" style="padding:.2rem .45rem;" (click)="notifications.dismiss(n.id)">x</button>
        </div>
      </article>
    </div>
  `,
})
export class ToastComponent {
  readonly notifications = inject(NotificationService);

  color(type: 'success' | 'error' | 'info' | 'warning'): string {
    return ({ success: '#16a34a', error: '#dc2626', info: '#2563eb', warning: '#d97706' })[type];
  }
}
