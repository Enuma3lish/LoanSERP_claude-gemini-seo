import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DateRange } from '../../models/api.models';

@Component({
  selector: 'app-date-range-picker',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './date-range-picker.component.html',
  styleUrls: ['./date-range-picker.component.css']
})
export class DateRangePickerComponent {
  @Output() dateRangeSelected = new EventEmitter<DateRange>();

  startDate: string = '';
  endDate: string = '';
  errorMessage: string = '';
  maxDate: string = '';
  minDate: string = '';

  constructor() {
    this.initializeDates();
  }

  private initializeDates(): void {
    const today = new Date();
    this.maxDate = this.formatDate(today);

    // Default: last 7 days
    const defaultStart = new Date(today);
    defaultStart.setDate(today.getDate() - 6);

    this.startDate = this.formatDate(defaultStart);
    this.endDate = this.formatDate(today);

    // Min date: 90 days ago from today
    const minDate = new Date(today);
    minDate.setDate(today.getDate() - 90);
    this.minDate = this.formatDate(minDate);
  }

  private formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  validateAndEmit(): void {
    this.errorMessage = '';

    if (!this.startDate || !this.endDate) {
      this.errorMessage = '請選擇開始日期和結束日期';
      return;
    }

    const start = new Date(this.startDate);
    const end = new Date(this.endDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Validate end date is not in the future
    if (end > today) {
      this.errorMessage = '結束日期不能超過今天';
      return;
    }

    // Validate start <= end
    if (start > end) {
      this.errorMessage = '開始日期必須早於或等於結束日期';
      return;
    }

    // Calculate days
    const daysDiff = Math.floor((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;

    // Validate minimum 7 days
    if (daysDiff < 7) {
      this.errorMessage = '日期範圍至少需要 7 天';
      return;
    }

    // Validate maximum 90 days
    if (daysDiff > 90) {
      this.errorMessage = '日期範圍最多 90 天';
      return;
    }

    // Validate start date is within 90 days from today
    const minAllowedDate = new Date(today);
    minAllowedDate.setDate(today.getDate() - 90);
    if (start < minAllowedDate) {
      this.errorMessage = '開始日期不能早於 90 天前';
      return;
    }

    // All validations passed
    this.dateRangeSelected.emit({
      start: start,
      end: end
    });
  }

  onStartDateChange(): void {
    if (this.startDate) {
      const start = new Date(this.startDate);
      const today = new Date();

      // Auto-adjust end date to maintain valid range
      if (!this.endDate) {
        const defaultEnd = new Date(start);
        defaultEnd.setDate(start.getDate() + 6); // Default 7 days
        if (defaultEnd > today) {
          this.endDate = this.formatDate(today);
        } else {
          this.endDate = this.formatDate(defaultEnd);
        }
      }
    }
  }
}
