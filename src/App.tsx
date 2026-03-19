import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'sonner';
import { Dashboard } from './pages/Dashboard';
import { AlphaControlRoom } from './pages/AlphaControlRoom';
import { ExperimentNotebook } from './pages/ExperimentNotebook';
import { AdminAnalytics } from './pages/AdminAnalytics';

const basename = import.meta.env.BASE_URL || '/';

function App() {
  return (
    <BrowserRouter basename={basename}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/alpha" element={<AlphaControlRoom />} />
        <Route path="/notebook" element={<ExperimentNotebook />} />
        <Route path="/admin/analytics" element={<AdminAnalytics />} />
      </Routes>
      <Toaster
        position="bottom-right"
        closeButton
        toastOptions={{
          duration: 6000,
          className: 'simhpc-toast',
          style: {
            background: '#0a0a0a',
            color: '#00f2ff',
            border: '1px solid #00f2ff33',
            padding: '20px',
            fontSize: '16px',
            fontWeight: 500,
            minWidth: '350px',
            borderRadius: '8px',
            boxShadow: '0 0 15px rgba(0, 242, 255, 0.15)',
          },
          success: {
            duration: 8000,
            iconTheme: { primary: '#00f2ff', secondary: '#0a0a0a' },
          },
          error: {
            duration: 10000,
            style: {
              border: '1px solid #ff4b4b33',
              color: '#ff4b4b',
            },
            iconTheme: { primary: '#ff4b4b', secondary: '#0a0a0a' },
          },
        }}
      />
    </BrowserRouter>
  );
}

export default App;
