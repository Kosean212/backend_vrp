import { Component, inject, signal } from '@angular/core';
import { DatePipe, NgFor } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Recoleccion } from '../../models/domain.models';

@Component({
  standalone: true,
  imports: [NgFor, DatePipe],
  template: `
    <h1>Gestión de residuos recolectados</h1>
    <article class="card">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th><th>Fecha</th><th>Peso (kg)</th><th>Tiempo (min)</th><th>Biochar estimado (kg)</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let item of rows()">
            <td>{{ item.id_recoleccion }}</td>
            <td>{{ item.fecha_recoleccion | date:'short' }}</td>
            <td>{{ item.peso_captado_kg }}</td>
            <td>{{ item.tiempo_empleado_min }}</td>
            <td>{{ item.biochar_estimado_kg }}</td>
          </tr>
        </tbody>
      </table>
    </article>
  `,
})
export class WasteManagementComponent {
  private readonly api = inject(ApiService);
  readonly rows = signal<Recoleccion[]>([]);

  constructor() {
    this.api.getRecolecciones().subscribe({ next: data => this.rows.set(data), error: () => this.rows.set([]) });
  }
}
