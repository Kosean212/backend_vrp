import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

export const errorInterceptor: HttpInterceptorFn = (req, next) =>
  next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      const message = error.error?.detail || error.message || 'Error no controlado';
      console.error(`API Error [${req.method} ${req.url}]:`, message);
      return throwError(() => new Error(message));
    })
  );
