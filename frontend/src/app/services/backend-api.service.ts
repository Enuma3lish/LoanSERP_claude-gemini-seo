import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TimeseriesResponse, CompareResponse } from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class BackendApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  /**
   * Get top 5 keywords timeseries data (from database only)
   */
  getTop5Timeseries(start: string, end: string): Observable<TimeseriesResponse> {
    const params = new HttpParams()
      .set('start', start)
      .set('end', end);

    return this.http.get<TimeseriesResponse>(`${this.baseUrl}/exposure/top5_timeseries`, { params });
  }

  /**
   * Get top 5 keywords timeseries data with auto-pull from GSC if missing
   */
  getTop5TimeseriesAuto(start: string, end: string, enablePull: boolean = true): Observable<TimeseriesResponse> {
    const params = new HttpParams()
      .set('start', start)
      .set('end', end)
      .set('pull', enablePull.toString());

    return this.http.get<TimeseriesResponse>(`${this.baseUrl}/exposure/top5_timeseries_auto`, { params });
  }

  /**
   * Get comparison data with all top 5 keywords
   */
  getTop5Compare(
    start: string,
    end: string,
    options?: {
      normalized?: boolean;
      cumulative?: boolean;
      smooth?: number;
    }
  ): Observable<CompareResponse> {
    let params = new HttpParams()
      .set('start', start)
      .set('end', end);

    if (options?.normalized !== undefined) {
      params = params.set('normalized', options.normalized.toString());
    }
    if (options?.cumulative !== undefined) {
      params = params.set('cum', options.cumulative.toString());
    }
    if (options?.smooth !== undefined && options.smooth > 0) {
      params = params.set('smooth', options.smooth.toString());
    }

    return this.http.get<CompareResponse>(`${this.baseUrl}/exposure/top5_compare`, { params });
  }
}
