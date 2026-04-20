export const PLATFORM_CONTRACT = {
  NETWORK: {
    PRIMARY_PORT: 8080,
    BACKUP_PORT: 8000,
    GATEWAY_HEALTH_ENDPOINT: '/health',
  },
  AUTH: {
    ADMIN_EMAILS: ['nexusbayarea@gmail.com'],
    ROUTES: {
      SIGN_IN: '/SignIn',
      DASHBOARD: '/dashboard',
      ADMIN: '/admin/analytics',
    }
  }
} as const;
