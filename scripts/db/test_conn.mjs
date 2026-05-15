import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

// Test connection to new Supabase
const url = 'https://flwrpsoizcinyrsukpcq.supabase.co';
const key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZsd3Jwc29pemNpbnlyc3VrcGNxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODQyNDUyMCwiZXhwIjoyMDk0MDAwNTIwfQ.PcHtYDjmUbYGPcHeEq2fyxLw9OfNURIJ341zWs9v5mA';
const supabase = createClient(url, key);

const { data, error } = await supabase.from('_prisma_migrations').select('*').limit(1);
console.log('data:', data, 'error:', error?.message);
