import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/hooks/useTheme';
import { Navigation } from '@/components/Navigation';
import { Hero } from '@/sections/Hero';
import { Stack } from '@/sections/Stack';
import { ValueDifferentiator } from '@/sections/ValueDifferentiator';
import { WhoItsFor } from '@/sections/WhoItsFor';
import { Pricing } from '@/sections/Pricing';
import { Footer } from '@/sections/Footer';
import { SignUp } from '@/pages/SignUp';
import { SignIn } from '@/pages/SignIn';
import { Terms } from '@/pages/Terms';
import { Privacy } from '@/pages/Privacy';
import { Dashboard } from '@/pages/Dashboard';

function HomePage() {
  return (
    <>
      <Navigation />
      <main>
        <Hero />
        <Stack />
        <ValueDifferentiator />
        <WhoItsFor />
        <Pricing />
      </main>
      <Footer />
    </>
  );
}

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/signin" element={<SignIn />} />
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
