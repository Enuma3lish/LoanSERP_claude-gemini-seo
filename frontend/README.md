# LoanSERP Frontend - Angular 18

## Overview

This is an Angular 18 frontend application for the LoanSERP Analytics Dashboard. It visualizes Google Search Console data and provides AI-powered trend analysis using Gemini and Claude LLMs.

## Features

- **Date Range Picker**: Select date ranges (minimum 7 days, maximum 90 days)
- **6 Interactive Charts**:
  1. Comparison chart showing all top 5 keywords
  2-6. Individual trend analysis for each of the top 5 keywords
- **AI-Powered Explanations**: Synchronous LLM-generated trend analysis under each chart
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Data**: Fetches data from Django backend and LLM broker service

## Tech Stack

- **Angular**: 18.x (Standalone Components)
- **ECharts**: 5.5.x (via ngx-echarts)
- **RxJS**: 7.8.x
- **TypeScript**: 5.4.x

## Prerequisites

- Node.js 18+ and npm
- Backend services running:
  - Django backend on `http://localhost:8000`
  - LLM Broker service on `http://localhost:9001`

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start development server
npm start

# The app will be available at http://localhost:4200
```

## Build

```bash
# Production build
npm run build

# Output will be in dist/loanserp-frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── dashboard/          # Main dashboard component
│   │   │   ├── date-range-picker/  # Date selection component
│   │   │   └── chart-card/         # Reusable chart component
│   │   ├── services/
│   │   │   ├── backend-api.service.ts  # Django API integration
│   │   │   └── llm-api.service.ts      # LLM service integration
│   │   ├── models/
│   │   │   └── api.models.ts       # TypeScript interfaces
│   │   ├── pipes/
│   │   │   └── sanitize-html.pipe.ts
│   │   ├── app.component.ts
│   │   ├── app.config.ts
│   │   └── app.routes.ts
│   ├── main.ts
│   ├── index.html
│   └── styles.css
├── angular.json
├── package.json
└── tsconfig.json
```

## API Integration

### Backend API (Django)

- `GET /api/exposure/top5_timeseries?start=YYYY-MM-DD&end=YYYY-MM-DD`
  - Returns top 5 keywords with daily exposure data

### LLM Broker API (FastAPI)

- `POST /v1/summarize/trend`
  - Accepts trend data and returns AI-generated analysis
  - Uses both Gemini and Claude for comprehensive insights

## Features in Detail

### Date Range Picker

- Validates minimum 7 days and maximum 90 days
- Ensures dates are within allowed range (today - 90 days)
- Auto-adjusts dates to maintain valid ranges

### Dashboard

- Displays 6 synchronized charts with loading states
- Fetches all LLM explanations in parallel using `forkJoin`
- Shows real-time loading indicators for both data and AI analysis

### Chart Card

- Reusable component for all chart types
- ECharts integration with customizable options
- Displays AI explanation with formatted text
- Responsive design with smooth animations

## Environment Variables

The API endpoints are currently hardcoded. To make them configurable, you can create an `environment.ts` file:

```typescript
export const environment = {
  production: false,
  backendUrl: 'http://localhost:8000/api',
  llmBrokerUrl: 'http://localhost:9001/v1'
};
```

## Troubleshooting

### CORS Issues

If you encounter CORS errors, ensure:
1. Django backend has `django-cors-headers` installed
2. `CORS_ALLOWED_ORIGINS` includes `http://localhost:4200`

### LLM Service Unavailable

The dashboard will gracefully handle LLM service errors and display a message. Charts will still render with data.

## Future Enhancements

- [ ] Add date presets (Last 7 days, Last 30 days, etc.)
- [ ] Export functionality for charts and data
- [ ] User authentication
- [ ] Customizable chart types (bar, area, line)
- [ ] Historical comparison view
- [ ] Email reports

## License

Proprietary - LoanSERP Project
