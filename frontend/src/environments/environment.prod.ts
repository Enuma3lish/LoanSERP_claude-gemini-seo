// Production environment configuration
export const environment = {
  production: true,
  backendUrl: '/api',  // Use relative path in production
  llmBrokerUrl: '/llm/v1',  // Assumes reverse proxy setup
  appName: 'LoanSERP Analytics Dashboard'
};
