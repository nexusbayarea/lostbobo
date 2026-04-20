import React, { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { PLATFORM_CONTRACT } from '../../lib/contract';

interface ProtectedRouteProps {
  children: ReactNode;
  requireAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAdmin = false 
}) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  const isAdmin = user?.email && PLATFORM_CONTRACT.AUTH.ADMIN_EMAILS.includes(user.email);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background text-muted-foreground animate-pulse">
        Verifying Mercury AI Credentials...
      </div>
    );
  }

  if (!user) {
    return <Navigate to={PLATFORM_CONTRACT.AUTH.ROUTES.SIGN_IN} state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to={PLATFORM_CONTRACT.AUTH.ROUTES.DASHBOARD} replace />;
  }

  return <>{children}</>;
};
