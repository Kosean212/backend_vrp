import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { DatePipe, NgFor, NgIf } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { NotificationService } from '../../core/services/notification.service';
import { LoteProduccion } from '../../models/domain.models';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule, NgIf, NgFor, DatePipe],
  template: `
    <h1>Monitoreo de producción de biochar</h1>
    <section style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <form class="card" [formGroup]="form" (ngSubmit)="save()">
        <h3>Registro de lote</h3>
        <label>ID Recolección <input type="number" formControlName="id_recoleccion"></label>
        <label>Fecha proceso <input type="date" formControlName="fecha_proceso"></label>
        <label>Temperatura (°C) <input type="number" formControlName="temperatura_proceso"></label>
        <label>Tiempo (min) <input type="number" formControlName="tiempo_proceso_min"></label>
        <label>Biochar obtenido (kg) <input type="number" formControlName="biochar_obtenido_kg"></label>
        <button class="btn" type="submit" [disabled]="form.invalid">Guardar lote</button>
        <p *ngIf="msg()" style="color:#16a34a;">{{ msg() }}</p>
      </form>

      <article class="card">
        <h3>Historial de producción</h3>
        <ul style="list-style:none;padding:0;margin:0;display:grid;gap:.6rem;">
          <li *ngFor="let lote of lotes()" style="border:1px solid #e5e7eb;border-radius:8px;padding:.5rem;">
            <strong>Lote #{{ lote.id_lote }}</strong><br>
            {{ lote.fecha_proceso | date }} · {{ lote.biochar_obtenido_kg }}kg · Eficiencia {{ lote.eficiencia_real }}%
          </li>
        </ul>
      </article>
    </section>
  `,
})
export class BiocharProductionComponent {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  private readonly notifications = inject(NotificationService);

  readonly msg = signal('');
  readonly lotes = signal<LoteProduccion[]>([]);

  readonly form = this.fb.nonNullable.group({
    id_recoleccion: [1, Validators.required],
    fecha_proceso: [new Date().toISOString().slice(0, 10), Validators.required],
    temperatura_proceso: [450, Validators.required],
    tiempo_proceso_min: [70, Validators.required],
    biochar_obtenido_kg: [32, Validators.required],
  });

  constructor() {
    this.load();
  }

  save(): void {
    if (this.form.invalid) return;
    this.api.registrarLote(this.form.getRawValue()).subscribe({
      next: () => {
        this.msg.set('Lote registrado correctamente');
        this.notifications.push({ type: 'success', title: 'Biochar', message: 'Lote registrado correctamente' });
        this.load();
      },
      error: () => {
        this.msg.set('No se pudo registrar; verifica backend/datos');
        this.notifications.push({ type: 'error', title: 'Biochar', message: 'No se pudo registrar el lote' });
      },
    });
  }

  private load(): void {
    this.api.getLotesBiochar().subscribe({ next: data => this.lotes.set(data), error: () => this.lotes.set([]) });
  }
}
