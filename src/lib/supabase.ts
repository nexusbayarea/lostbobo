import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Fallback to a dummy URL if missing to prevent createClient from throwing
// during initialization, but log a warning in development.
const safeUrl = supabaseUrl || 'https://placeholder-url.supabase.co';
const safeKey = supabaseAnonKey || 'placeholder-key';

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials are missing. Auth features will not work.');
}

export const supabase = createClient(safeUrl, safeKey);

export async function signInWithGoogle() {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin + '/dashboard',
    },
  });
  if (error) console.error("Login failed:", error.message);
}
