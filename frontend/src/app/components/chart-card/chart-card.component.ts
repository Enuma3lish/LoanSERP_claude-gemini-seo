import { Component, Input, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NgxEchartsModule } from 'ngx-echarts';
import { EChartsOption } from 'echarts';
import { SanitizeHtmlPipe } from '../../pipes/sanitize-html.pipe';

@Component({
  selector: 'app-chart-card',
  standalone: true,
  imports: [CommonModule, NgxEchartsModule, SanitizeHtmlPipe],
  templateUrl: './chart-card.component.html',
  styleUrls: ['./chart-card.component.css']
})
export class ChartCardComponent implements OnInit, OnChanges {
  @Input() title: string = '';
  @Input() chartData: any;
  @Input() dates: string[] = [];
  @Input() llmExplanation: string = '';
  @Input() isLoading: boolean = false;
  @Input() chartType: 'line' | 'bar' = 'line';

  chartOption: EChartsOption = {};

  ngOnInit(): void {
    this.updateChart();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['chartData'] || changes['dates']) {
      this.updateChart();
    }
  }

  private updateChart(): void {
    console.log('ChartCard updateChart called for:', this.title);
    console.log('  chartData:', this.chartData);
    console.log('  dates:', this.dates);

    if (!this.chartData || !this.dates || this.dates.length === 0) {
      console.warn('ChartCard updateChart early return - missing data');
      console.warn('  chartData is null/undefined:', !this.chartData);
      console.warn('  dates is null/undefined:', !this.dates);
      console.warn('  dates.length === 0:', this.dates?.length === 0);
      return;
    }

    // If chartData is a single series (for individual keyword charts)
    const isSingleSeries = Array.isArray(this.chartData);
    const series = isSingleSeries
      ? [{
          name: this.title,
          type: this.chartType,
          data: this.chartData,
          smooth: true,
          itemStyle: {
            color: '#667eea'
          },
          areaStyle: this.chartType === 'line' ? {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
              ]
            }
          } : undefined
        }]
      : this.chartData.map((item: any, index: number) => ({
          name: item.name,
          type: this.chartType,
          data: item.data,
          smooth: true,
          itemStyle: {
            color: this.getColor(index)
          }
        }));

    this.chartOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        }
      },
      legend: {
        data: series.map((s: any) => s.name),
        top: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: this.dates,
        axisLabel: {
          rotate: 45,
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value',
        name: '曝光次數'
      },
      series: series
    };

    console.log('ChartCard chart option created for:', this.title);
    console.log('  Number of series:', series.length);
    console.log('  Series:', series);
  }

  private getColor(index: number): string {
    const colors = [
      '#667eea',
      '#764ba2',
      '#f093fb',
      '#4facfe',
      '#43e97b',
      '#fa709a'
    ];
    return colors[index % colors.length];
  }
}
