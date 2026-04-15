import { AfterViewInit, Component, OnDestroy, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import * as L from 'leaflet';
import 'leaflet.heat';
import { NgFor } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { PuntoRecoleccion, RutaOptimizada } from '../../models/domain.models';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  standalone: true,
  imports: [NgFor, FormsModule],
  template: `
    <h1>Ruteo y mapas interactivos</h1>
    <div style="display:flex;gap:.8rem;margin-bottom:.8rem;flex-wrap:wrap">
      <button class="btn" (click)="generarRutas()">Generar rutas optimizadas</button>
      <button class="btn secondary" (click)="confirmarRutas()" [disabled]="!rutas().length">Confirmar rutas</button>
      <label><input type="checkbox" [(ngModel)]="showPuntos" (change)="refreshLayers()"> Puntos</label>
      <label><input type="checkbox" [(ngModel)]="showRutas" (change)="refreshLayers()"> Rutas</label>
      <label><input type="checkbox" [(ngModel)]="showHeatmap" (change)="refreshLayers()"> Heatmap</label>
      <select [(ngModel)]="filtroResiduo" (change)="refreshLayers()">
        <option value="all">Todos los residuos</option>
        <option value="organico">Orgánico</option>
      </select>
    </div>

    <div style="display:grid;grid-template-columns:3fr 1fr;gap:1rem;">
      <div id="map" class="map-container card"></div>
      <aside class="card">
        <h3>Detalles de ruta</h3>
        <div *ngFor="let ruta of rutas()" style="padding:.5rem 0;border-bottom:1px solid #e5e7eb;">
          <strong>Unidad {{ ruta.placas }}</strong>
          <p style="margin:.25rem 0;">Distancia: {{ ruta.distancia_total_km }} km</p>
          <p style="margin:.25rem 0;">Tiempo: {{ ruta.tiempo_total_min }} min</p>
          <p style="margin:.25rem 0;">Paradas: {{ ruta.puntos.length }}</p>
          <small>Secuencia: {{ sequence(ruta) }}</small>
        </div>
      </aside>
    </div>
  `,
})
export class RoutingMapComponent implements AfterViewInit, OnDestroy {
  private readonly api = inject(ApiService);
  private readonly notifications = inject(NotificationService);
  private map!: L.Map;
  private pointsLayer = L.layerGroup();
  private routesLayer = L.layerGroup();
  private heatLayer?: L.Layer;
  private animationTimer?: number;

  readonly puntos = signal<PuntoRecoleccion[]>([]);
  readonly rutas = signal<RutaOptimizada[]>([]);
  readonly filteredPoints = computed(() =>
    this.filtroResiduo === 'all' ? this.puntos() : this.puntos().filter(p => p.tipo_residuo === this.filtroResiduo)
  );

  showPuntos = true;
  showRutas = true;
  showHeatmap = false;
  filtroResiduo = 'all';

  ngAfterViewInit(): void {
    this.map = L.map('map').setView([19.817, -97.359], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
    }).addTo(this.map);

    this.locateUser();
    this.api.getPuntos().subscribe(points => {
      this.puntos.set(points);
      this.refreshLayers();
    });
  }

  generarRutas(): void {
    this.api.optimizarRutas().subscribe(response => {
      this.rutas.set(response.rutas);
      this.refreshLayers();
      this.animateFirstRoute();
      const risk = response.rutas.some(r => r.tiempo_total_min > 120);
      this.notifications.push({
        type: risk ? 'warning' : 'success',
        title: risk ? 'Alerta de eficiencia' : 'Optimización completa',
        message: risk ? 'Se detectaron rutas con tiempo elevado.' : `Se generaron ${response.rutas.length} rutas optimizadas.`,
      });
    });
  }

  confirmarRutas(): void {
    this.api.confirmarRutas(this.rutas()).subscribe({
      next: ({ mensaje }) => this.notifications.push({ type: 'success', title: 'Rutas confirmadas', message: mensaje }),
      error: err => this.notifications.push({ type: 'error', title: 'Error al confirmar', message: `${err}` }),
    });
  }

  refreshLayers(): void {
    this.pointsLayer.clearLayers();
    this.routesLayer.clearLayers();

    if (this.showPuntos) {
      this.filteredPoints().forEach(point => {
        L.marker([point.latitud, point.longitud]).bindPopup(
          `<b>${point.nombre_sector}</b><br>Tipo: ${point.tipo_residuo}<br>Volumen: ${point.volumen_estimado_kg} kg<br>Estado: pendiente`
        ).addTo(this.pointsLayer);
      });
      this.pointsLayer.addTo(this.map);
    } else {
      this.map.removeLayer(this.pointsLayer);
    }

    if (this.showRutas) {
      const colors = ['#1d4ed8', '#0c7c59', '#f59e0b', '#ef4444'];
      this.rutas().forEach((route, idx) => {
        const latLngs = route.puntos.map(p => L.latLng(p.lat, p.lon));
        L.polyline(latLngs, { color: colors[idx % colors.length], weight: 5 }).addTo(this.routesLayer);
      });
      this.routesLayer.addTo(this.map);
    } else {
      this.map.removeLayer(this.routesLayer);
    }

    this.renderHeatmap();
  }

  private renderHeatmap(): void {
    if (this.heatLayer) {
      this.map.removeLayer(this.heatLayer);
      this.heatLayer = undefined;
    }
    if (!this.showHeatmap) return;

    const heatPoints = this.filteredPoints().map(p => [p.latitud, p.longitud, Math.max(0.2, p.volumen_estimado_kg / 100)] as [number, number, number]);
    const heatFactory = (L as unknown as { heatLayer: (points: [number, number, number][], cfg: Record<string, unknown>) => L.Layer }).heatLayer;
    this.heatLayer = heatFactory(heatPoints, { radius: 28, blur: 20 });
    this.heatLayer.addTo(this.map);
  }

  private locateUser(): void {
    this.map.locate({ setView: false, maxZoom: 15 });
    this.map.on('locationfound', (e: L.LocationEvent) => {
      L.circleMarker(e.latlng, { radius: 8, color: '#2563eb' }).bindPopup('Tu ubicación').addTo(this.map);
    });
  }

  private animateFirstRoute(): void {
    if (this.animationTimer) window.clearInterval(this.animationTimer);
    const first = this.rutas()[0];
    if (!first?.puntos.length) return;

    let index = 0;
    const marker = L.circleMarker([first.puntos[0].lat, first.puntos[0].lon], { radius: 9, color: '#111827' }).addTo(this.map);
    this.animationTimer = window.setInterval(() => {
      index = (index + 1) % first.puntos.length;
      marker.setLatLng([first.puntos[index].lat, first.puntos[index].lon]);
    }, 1300);
  }

  sequence(ruta: RutaOptimizada): string {
    return ruta.puntos.map(p => p.id).join(' → ');
  }

  ngOnDestroy(): void {
    if (this.animationTimer) window.clearInterval(this.animationTimer);
    if (this.map) this.map.remove();
  }
}
