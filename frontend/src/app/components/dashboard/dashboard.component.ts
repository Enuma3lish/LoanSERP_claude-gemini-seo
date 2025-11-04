import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { forkJoin } from 'rxjs';
import { DateRangePickerComponent } from '../date-range-picker/date-range-picker.component';
import { ChartCardComponent } from '../chart-card/chart-card.component';
import { BackendApiService } from '../../services/backend-api.service';
import { LlmApiService } from '../../services/llm-api.service';
import { DateRange, TimeseriesResponse, TrendRequest, SeriesItem } from '../../models/api.models';

interface ChartWithExplanation {
  title: string;
  data: any;
  explanation: string;
  loading: boolean;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, DateRangePickerComponent, ChartCardComponent],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  loading = false;
  error = '';
  dates: string[] = [];
  keywords: string[] = [];

  // 6 charts: 1 comparison + 5 individual keyword charts
  charts: ChartWithExplanation[] = [];

  constructor(
    private backendApi: BackendApiService,
    private llmApi: LlmApiService
  ) {}

  ngOnInit(): void {
    // Initialize empty charts
    this.initializeCharts();
  }

  private initializeCharts(): void {
    this.charts = [
      { title: 'Top 5 關鍵字曝光比較', data: null, explanation: '', loading: false },
      { title: '關鍵字 #1 趨勢分析', data: null, explanation: '', loading: false },
      { title: '關鍵字 #2 趨勢分析', data: null, explanation: '', loading: false },
      { title: '關鍵字 #3 趨勢分析', data: null, explanation: '', loading: false },
      { title: '關鍵字 #4 趨勢分析', data: null, explanation: '', loading: false },
      { title: '關鍵字 #5 趨勢分析', data: null, explanation: '', loading: false }
    ];
  }

  onDateRangeSelected(dateRange: DateRange): void {
    this.error = '';
    this.loading = true;
    this.initializeCharts();

    const startStr = this.formatDate(dateRange.start);
    const endStr = this.formatDate(dateRange.end);

    // Fetch data from backend with auto-pull enabled
    this.backendApi.getTop5TimeseriesAuto(startStr, endStr, true).subscribe({
      next: (response: TimeseriesResponse) => {
        this.loading = false;
        this.dates = response.dates;
        this.keywords = response.keywords;

        // Update chart data
        this.updateChartData(response);

        // Fetch LLM explanations for all charts simultaneously
        this.fetchAllLLMExplanations(response);
      },
      error: (err) => {
        this.loading = false;
        this.error = '無法載入資料，請確認後端服務是否正常運行';
        console.error('Backend API error:', err);
      }
    });
  }

  private updateChartData(response: TimeseriesResponse): void {
    // Chart 0: Comparison chart with all 5 keywords
    this.charts[0].title = 'Top 5 關鍵字曝光比較';
    this.charts[0].data = response.series;

    // Charts 1-5: Individual keyword charts
    response.series.forEach((series, index) => {
      if (index < 5) {
        this.charts[index + 1].title = `${series.name} - 曝光趨勢`;
        this.charts[index + 1].data = series.data;
      }
    });
  }

  private fetchAllLLMExplanations(response: TimeseriesResponse): void {
    // Mark all charts as loading explanations
    this.charts.forEach(chart => chart.loading = true);

    const period = response.period;
    const daysDiff = Math.floor(
      (new Date(period.end).getTime() - new Date(period.start).getTime()) / (1000 * 60 * 60 * 24)
    ) + 1;

    // Prepare LLM requests for each chart
    const llmRequests = this.charts.map((chart, index) => {
      const request: TrendRequest = {
        period: {
          start: period.start,
          end: period.end,
          days: daysDiff
        },
        top_keywords: index === 0 ? response.keywords : [response.keywords[index - 1]],
        dates: response.dates,
        series: index === 0 ? response.series : [response.series[index - 1]],
        output_lang: 'zh-tw',
        short_mid_long_base_days: 7,
        mode: 'no-external',
        use_cache: true
      };

      return this.llmApi.summarizeTrend(request);
    });

    // Execute all LLM requests in parallel (synchronously from UI perspective)
    forkJoin(llmRequests).subscribe({
      next: (responses) => {
        responses.forEach((response, index) => {
          this.charts[index].loading = false;

          // Format the LLM explanation
          let explanation = '';

          if (response.provider_outputs && response.provider_outputs.length > 0) {
            const output = response.provider_outputs[0];

            explanation = `${output.summary}\n\n`;

            if (output.actions_short && output.actions_short.length > 0) {
              explanation += `📊 短期建議：\n`;
              output.actions_short.forEach(action => {
                explanation += `• ${action}\n`;
              });
              explanation += '\n';
            }

            if (output.actions_mid && output.actions_mid.length > 0) {
              explanation += `📈 中期建議：\n`;
              output.actions_mid.forEach(action => {
                explanation += `• ${action}\n`;
              });
              explanation += '\n';
            }

            if (output.actions_long && output.actions_long.length > 0) {
              explanation += `🎯 長期建議：\n`;
              output.actions_long.forEach(action => {
                explanation += `• ${action}\n`;
              });
            }

            explanation += `\n信心分數: ${(output.confidence * 100).toFixed(0)}%`;
          } else {
            explanation = '無法生成趨勢分析';
          }

          this.charts[index].explanation = explanation;
        });
      },
      error: (err) => {
        console.error('LLM API error:', err);
        this.charts.forEach(chart => {
          chart.loading = false;
          chart.explanation = '❌ LLM 服務暫時無法使用，請稍後再試';
        });
      }
    });
  }

  private formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }
}
