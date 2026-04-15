import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { delay } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import {
  LoteProduccion,
  PuntoRecoleccion,
  Recoleccion,
  ReporteOperativo,
  RespuestaVRP,
  RutaOptimizada,
} from '../models/domain.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiBaseUrl;

  getPuntos(): Observable<PuntoRecoleccion[]> {
    if (environment.simulationMode) {
      return of([
        { id_punto: 1, nombre_sector: 'Centro', latitud: 19.817, longitud: -97.359, volumen_estimado_kg: 50, tipo_residuo: 'organico' },
        { id_punto: 2, nombre_sector: 'Norte', latitud: 19.825, longitud: -97.352, volumen_estimado_kg: 70, tipo_residuo: 'organico' },
        { id_punto: 3, nombre_sector: 'Sur', latitud: 19.807, longitud: -97.368, volumen_estimado_kg: 45, tipo_residuo: 'organico' },
        { id_punto: 4, nombre_sector: 'Poniente', latitud: 19.813, longitud: -97.375, volumen_estimado_kg: 88, tipo_residuo: 'organico' },
      ]).pipe(delay(400));
    }
    return this.http.get<PuntoRecoleccion[]>(`${this.api}/puntos`);
  }

  optimizarRutas(): Observable<RespuestaVRP> {
    if (environment.simulationMode) {
      return of({ rutas: [this.mockRoute()] }).pipe(delay(800));
    }
    return this.http.get<RespuestaVRP>(`${this.api}/rutas/optimizar`);
  }

  confirmarRutas(rutas: RutaOptimizada[]): Observable<{ mensaje: string }> {
    if (environment.simulationMode) {
      return of({ mensaje: 'Rutas confirmadas en modo simulación' }).pipe(delay(450));
    }
    return this.http.post<{ mensaje: string }>(`${this.api}/rutas/confirmar`, {
      fecha: new Date().toISOString().slice(0, 10),
      rutas: rutas.map(r => ({
        id_unidad: r.id_unidad,
        distancia_total_km: r.distancia_total_km,
        tiempo_total_min: r.tiempo_total_min,
        costo_estimado: r.costo_estimado,
        puntos_orden: r.puntos.map(p => p.id),
      })),
    });
  }

  getReporteOperativo(): Observable<ReporteOperativo> {
    if (environment.simulationMode) {
      return of({
        total_recolecciones: 8,
        total_peso_kg: 1240,
        total_biochar_estimado_kg: 372,
        total_distancia_km: 138,
        costo_total: 11400,
        eficiencia_promedio_pct: 28.6,
      }).pipe(delay(250));
    }
    return this.http.get<ReporteOperativo>(`${this.api}/reportes/operativo`);
  }

  getRecolecciones(): Observable<Recoleccion[]> {
    if (environment.simulationMode) {
      return of([
        {
          id_recoleccion: 1,
          id_ruta: 1,
          fecha_recoleccion: new Date().toISOString(),
          peso_captado_kg: 350,
          tiempo_empleado_min: 95,
          consumo_combustible_l: 13,
          costo_operativo: 820,
          porcentaje_capacidad_utilizada: 84,
          biochar_estimado_kg: 105,
        },
      ]).pipe(delay(250));
    }
    return this.http.get<Recoleccion[]>(`${this.api}/recolecciones`);
  }

  getLotesBiochar(): Observable<LoteProduccion[]> {
    if (environment.simulationMode) {
      return of([
        {
          id_lote: 1,
          id_recoleccion: 1,
          fecha_proceso: new Date().toISOString(),
          temperatura_proceso: 450,
          tiempo_proceso_min: 80,
          biochar_obtenido_kg: 94,
          eficiencia_real: 26.8,
        },
      ]).pipe(delay(250));
    }
    return this.http.get<LoteProduccion[]>(`${this.api}/biochar/lotes`);
  }

  registrarLote(payload: Omit<LoteProduccion, 'id_lote' | 'eficiencia_real'>): Observable<LoteProduccion> {
    if (environment.simulationMode) {
      const eficiencia = Math.round((payload.biochar_obtenido_kg / 350) * 10000) / 100;
      return of({ ...payload, id_lote: Date.now(), eficiencia_real: eficiencia }).pipe(delay(300));
    }
    return this.http.post<LoteProduccion>(`${this.api}/biochar/lotes`, payload);
  }

  getProyeccionBiochar(): Observable<Array<{ id_recoleccion: number; id_ruta: number; biochar_estimado_kg: number }>> {
    if (environment.simulationMode) {
      return of([
        { id_recoleccion: 1, id_ruta: 1, biochar_estimado_kg: 105 },
        { id_recoleccion: 2, id_ruta: 2, biochar_estimado_kg: 98 },
      ]).pipe(delay(220));
    }
    return this.http.get<Array<{ id_recoleccion: number; id_ruta: number; biochar_estimado_kg: number }>>(`${this.api}/reportes/proyeccion-biochar`);
  }

  private mockRoute(): RutaOptimizada {
    return {
      id_unidad: 1,
      placas: 'ABC-123',
      distancia_total_km: 22.5,
      tiempo_total_min: 94,
      costo_estimado: 430,
      puntos: [
        { id: 1, lat: 19.817, lon: -97.359, nombre: 'Centro' },
        { id: 2, lat: 19.825, lon: -97.352, nombre: 'Norte' },
        { id: 3, lat: 19.807, lon: -97.368, nombre: 'Sur' },
        { id: 4, lat: 19.813, lon: -97.375, nombre: 'Poniente' },
      ],
    };
  }
}
