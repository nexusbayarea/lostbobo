import { createClient } from '@supabase/supabase-js';

/**
 * SimHPC Supabase Client
 * * Note: We use 'VITE_' prefix here because Vite only exposes variables 
 * prefixed with VITE_ to your client-side code.
 * * In Infisical/Vercel, ensure these are mapped:
 * SB_URL -> VITE_SB_URL
 * SB_PUB_KEY -> VITE_SB_PUB_KEY
 */

const supabaseUrl = import.meta.env.VITE_SB_URL;
const supabaseKey = import.meta.env.VITE_SB_PUB_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error(
    "Supabase configuration missing. Ensure VITE_SB_URL and VITE_SB_PUB_KEY are set in Infisical/Vercel."
  );
}

export const supabase = createClient(supabaseUrl || '', supabaseKey || '');

export async function signInWithGoogle() {
  const { error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: window.location.origin + '/dashboard',
    },
  });
  if (error) console.error("Login failed:", error.message);
}