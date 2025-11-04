import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { TrendRequest, TrendResponse } from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class LlmApiService {
  private baseUrl = 'http://localhost:9001/v1';

  constructor(private http: HttpClient) {}

  /**
   * Summarize trend using LLM service (Gemini + Claude)
   */
  summarizeTrend(request: TrendRequest): Observable<TrendResponse> {
    return this.http.post<TrendResponse>(`${this.baseUrl}/summarize/trend`, request);
  }

  /**
   * Health check for LLM service
   */
  health(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }
}
