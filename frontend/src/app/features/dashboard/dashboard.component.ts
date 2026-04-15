import { AfterViewInit, Component, ElementRef, ViewChild, inject, signal } from '@angular/core';
import { NgFor } from '@angular/common';
import { Chart, registerables } from 'chart.js';
import { ApiService } from '../../services/api.service';
import { ReporteOperativo } from '../../models/domain.models';

Chart.register(...registerables);

@Component({
  standalone: true,
  imports: [NgFor],
  template: `
    <h1>Dashboard Operativo</h1>
    <section class="grid metric-grid" style="margin-bottom:1rem;">
      <article class="card" *ngFor="let metric of metrics()">
        <strong>{{ metric.label }}</strong>
        <h2 style="margin:.4rem 0 0 0;">{{ metric.value }}</h2>
      </article>
    </section>

    <section class="grid" style="grid-template-columns:2fr 1fr;align-items:stretch;">
      <article class="card"><canvas #lineChart></canvas></article>
      <article class="card"><canvas #barChart></canvas></article>
    </section>
  `,
})
export class DashboardComponent implements AfterViewInit {
  @ViewChild('lineChart') lineCanvas!: ElementRef<HTMLCanvasElement>;
  @ViewChild('barChart') barCanvas!: ElementRef<HTMLCanvasElement>;

  private readonly api = inject(ApiService);
  readonly metrics = signal<{ label: string; value: string }[]>([]);

  ngAfterViewInit(): void {
    this.api.getReporteOperativo().subscribe({
      next: (rep: ReporteOperativo) => {
        this.metrics.set([
          { label: 'Total residuos recolectados', value: `${rep.total_peso_kg.toFixed(1)} kg` },
          { label: 'Distancia recorrida', value: `${rep.total_distancia_km.toFixed(1)} km` },
          { label: 'Recolecciones', value: `${rep.total_recolecciones}` },
          { label: 'Producción estimada biochar', value: `${rep.total_biochar_estimado_kg.toFixed(1)} kg` },
        ]);
      },
      error: () => {
        this.metrics.set([
          { label: 'Total residuos recolectados', value: '165.0 kg' },
          { label: 'Distancia recorrida', value: '22.5 km' },
          { label: 'Recolecciones', value: '5' },
          { label: 'Producción estimada biochar', value: '49.5 kg' },
        ]);
      },
    });

    new Chart(this.lineCanvas.nativeElement, {
      type: 'line',
      data: {
        labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'],
        datasets: [{ label: 'Kg recolectados', data: [120, 150, 180, 130, 210, 190], borderColor: '#0c7c59' }],
      },
    });

    new Chart(this.barCanvas.nativeElement, {
      type: 'bar',
      data: {
        labels: ['Ruta A', 'Ruta B', 'Ruta C'],
        datasets: [{ label: 'Tiempo min', data: [95, 80, 120], backgroundColor: ['#1d4ed8', '#0c7c59', '#f59e0b'] }],
      },
    });
  }
}
