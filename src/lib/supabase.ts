// Re-export the auto-generated Supabase client
// This file exists for backward compatibility with imports using '@/lib/supabase'
import { supabase } from '@/integrations/supabase/client';

export { supabase };

// Supabase is always configured when Lovable Cloud is enabled
export const isSupabaseConfigured = true;
