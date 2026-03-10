import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://ldzztrnghaaonparyggz.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'sb_publishable_BTPKB2cbCifXpkENl43thw_dxio3DkO';

if (!import.meta.env.VITE_SUPABASE_URL) {
  console.warn('Supabase URL missing from environment, using production fallback.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

export async function signInWithGoogle() {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin + '/dashboard',
    },
  });
  if (error) console.error("Login failed:", error.message);
}
