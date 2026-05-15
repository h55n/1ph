import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// Test connection to new Supabase
const url = 'https://flwrpsoizcinyrsukpcq.supabase.co';
const key = 'REDACTED_SECRET';
const supabase = createClient(url, key);

const { data, error } = await supabase.from('_prisma_migrations').select('*').limit(1);
console.log('data:', data, 'error:', error?.message);
