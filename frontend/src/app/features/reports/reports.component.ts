import { Component, inject, signal } from '@angular/core';
import { NgFor } from '@angular/common';
import * as XLSX from 'xlsx';
import { ApiService } from '../../services/api.service';

type Row = { id_recoleccion: number; id_ruta: number; biochar_estimado_kg: number };

@Component({
  standalone: true,
  imports: [NgFor],
  template: `
    <h1>Reportes y exportación</h1>
    <article class="card">
      <div style="display:flex;gap:.6rem;margin-bottom:.8rem;">
        <button class="btn" (click)="exportExcel()">Exportar a Excel</button>
        <button class="btn secondary" (click)="reload()">Actualizar</button>
      </div>
      <ul>
        <li *ngFor="let row of projection()">
          Recolección #{{ row.id_recoleccion }} | Ruta #{{ row.id_ruta }} | {{ row.biochar_estimado_kg }} kg estimado
        </li>
      </ul>
    </article>
  `,
})
export class ReportsComponent {
  private readonly api = inject(ApiService);
  readonly projection = signal<Row[]>([]);

  constructor() {
    this.reload();
  }

  reload(): void {
    this.api.getProyeccionBiochar().subscribe({
      next: data => this.projection.set(data),
      error: () => this.projection.set([]),
    });
  }

  exportExcel(): void {
    const worksheet = XLSX.utils.json_to_sheet(this.projection());
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Reporte');
    XLSX.writeFile(workbook, 'reporte_biochar.xlsx');
  }
}
