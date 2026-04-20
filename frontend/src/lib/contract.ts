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
  },
  SIMULATION_CONFIG: {
    MODEL_TYPES: ['Parametric Sweep', 'Latin Hypercube', 'Sobol GSA'],
    GEOMETRY_TEMPLATES: ['Turbine Blade', 'Heat Sink', 'Pressure Vessel'],
    GEOMETRY_MAP: {
      'Heat Sink': 'https://[id].supabase.co/storage/v1/object/public/sim-templates/heatsink.mesh',
      'Turbine Blade': 'https://[id].supabase.co/storage/v1/object/public/sim-templates/turbine.mesh',
      'Pressure Vessel': 'https://[id].supabase.co/storage/v1/object/public/sim-templates/vessel.mesh'
    },
    SOLVERS: ['MFEM (Structural)', 'SUNDIALS (Thermal)', 'Mercury-Hybrid'],
  }
} as const;
