# Frontend Angular - Biochar VRP

Frontend profesional para visualización de rutas VRP, gestión de residuos y monitoreo de producción de biochar.

## Requisitos
- Node.js 20+
- Angular CLI 18+

## Ejecutar
```bash
cd frontend
npm install
npm start
```

Aplicación en `http://localhost:4200`.

## Integración API
Configura `src/environments/environment.ts`:
- `apiBaseUrl`: URL del backend FastAPI (por defecto `http://localhost:8000`)
- `simulationMode`: `true` para datos mock, `false` para API real.

## Módulos
- Dashboard (KPIs + gráficas)
- Routing (Leaflet: puntos, rutas, capas, heatmap, geolocalización, animación, confirmar rutas)
- Waste Management
- Biochar Production (registro de lotes con formularios reactivos)
- Reports (proyección de biochar y exportación Excel)
- Auth (selección de roles: admin / operador / supervisor)

## Capacidades avanzadas implementadas
- Notificaciones toast globales para eventos operativos y errores.
- Modo simulación completo para pruebas sin backend.
- Detección de rutas ineficientes (alerta por tiempo elevado).
- Diseño responsive con tema claro/oscuro.

## Arquitectura
- `core/`: servicios transversales (auth, notificaciones, interceptor global)
- `shared/`: componentes reutilizables (toasts)
- `features/`: módulos funcionales desacoplados
- `models/` y `services/`: contratos tipados y acceso HTTP

Estructura preparada para ampliar a PWA/offline en iteraciones posteriores.
