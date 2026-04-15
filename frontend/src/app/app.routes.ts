import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  {
    path: 'auth',
    loadComponent: () => import('./features/auth/auth.component').then(m => m.AuthComponent),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./features/dashboard/dashboard.component').then(m => m.DashboardComponent),
  },
  {
    path: 'routing',
    loadComponent: () => import('./features/routing/routing-map.component').then(m => m.RoutingMapComponent),
  },
  {
    path: 'waste-management',
    loadComponent: () => import('./features/waste-management/waste-management.component').then(m => m.WasteManagementComponent),
  },
  {
    path: 'biochar-production',
    loadComponent: () => import('./features/biochar-production/biochar-production.component').then(m => m.BiocharProductionComponent),
  },
  {
    path: 'reports',
    loadComponent: () => import('./features/reports/reports.component').then(m => m.ReportsComponent),
  },
  { path: '**', redirectTo: 'dashboard' },
];
