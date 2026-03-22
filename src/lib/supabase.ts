import { createClient, type SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

let supabase: SupabaseClient;

if (supabaseUrl && supabaseAnonKey) {
  supabase = createClient(supabaseUrl, supabaseAnonKey);
} else {
  console.warn('Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY — auth features disabled.');
  // Create a dummy client that won't crash the app
  // Using a placeholder URL so createClient doesn't throw
  supabase = createClient('https://placeholder.supabase.co', 'placeholder-key');
}

export { supabase };
export const isSupabaseConfigured = !!(supabaseUrl && supabaseAnonKey);
