import React, { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children: ReactNode;
  requireAdmin?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAdmin = false 
}) => {
  const { user, loading, userTier } = useAuth();
  const location = useLocation();

  // Simple check for founder/admin: replace with your specific logic
  const isAdmin = user?.email === 'nexusbayarea@gmail.com';

  if (loading) {
    return <div className="loading-spinner">Verifying Mercury AI Credentials...</div>;
  }

  if (!user) {
    return <Navigate to="/SignIn" state={{ from: location }} replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
