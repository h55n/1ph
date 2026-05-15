// migrate_data.mjs — Migrate data from old Supabase to new Supabase via REST API
// No DB password required — uses service role keys

const OLD_URL = 'https://ddgyulnvbdiczmzggkmx.supabase.co';
const OLD_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRkZ3l1bG52YmRpY3ptemdna214Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjUzOTYxMCwiZXhwIjoyMDkyMTE1NjEwfQ.chTMoD2vsOTBpi_7ahY89SP_8xe1rfaJ-mlfh3BieBE';

const NEW_URL = 'https://flwrpsoizcinyrsukpcq.supabase.co';
const NEW_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZsd3Jwc29pemNpbnlyc3VrcGNxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODQyNDUyMCwiZXhwIjoyMDk0MDAwNTIwfQ.PcHtYDjmUbYGPcHeEq2fyxLw9OfNURIJ341zWs9v5mA';

function headers(key) {
  return {
    'apikey': key,
    'Authorization': `Bearer ${key}`,
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal',
  };
}

async function fetchAll(baseUrl, key, table, selectFields = '*', extraParams = '') {
  const allRecords = [];
  let offset = 0;
  const limit = 1000;
  
  while (true) {
    const url = `${baseUrl}/rest/v1/${table}?select=${selectFields}&limit=${limit}&offset=${offset}${extraParams}`;
    const res = await fetch(url, { headers: headers(key) });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Fetch failed for ${table}: ${res.status} ${text}`);
    }
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) break;
    allRecords.push(...data);
    if (data.length < limit) break;
    offset += limit;
  }
  return allRecords;
}

async function insertBatch(baseUrl, key, table, records) {
  if (records.length === 0) return;
  
  const BATCH_SIZE = 500;
  for (let i = 0; i < records.length; i += BATCH_SIZE) {
    const batch = records.slice(i, i + BATCH_SIZE);
    const url = `${baseUrl}/rest/v1/${table}`;
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        ...headers(key),
        'Prefer': 'resolution=merge-duplicates',
      },
      body: JSON.stringify(batch),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Insert failed for ${table} batch ${i}: ${res.status} ${text}`);
    }
    console.log(`  Inserted batch ${Math.floor(i/BATCH_SIZE)+1} of ${table} (${batch.length} records)`);
  }
}

async function migrate() {
  console.log('=== Data Migration: Old Supabase → New Supabase ===\n');

  // 1. Migrate Hackathons (most important)
  console.log('Fetching Hackathons from old DB...');
  const hackathons = await fetchAll(OLD_URL, OLD_KEY, 'Hackathon');
  console.log(`Found ${hackathons.length} hackathons`);
  
  if (hackathons.length > 0) {
    console.log('Inserting Hackathons into new DB...');
    await insertBatch(NEW_URL, NEW_KEY, 'Hackathon', hackathons);
    console.log(`✓ ${hackathons.length} hackathons migrated\n`);
  }

  // 2. Migrate Users (if any)
  console.log('Fetching Users from old DB...');
  const users = await fetchAll(OLD_URL, OLD_KEY, 'User');
  console.log(`Found ${users.length} users`);
  
  if (users.length > 0) {
    console.log('Inserting Users into new DB...');
    await insertBatch(NEW_URL, NEW_KEY, 'User', users);
    console.log(`✓ ${users.length} users migrated\n`);
  }

  // 3. Migrate Accounts
  console.log('Fetching Accounts...');
  const accounts = await fetchAll(OLD_URL, OLD_KEY, 'Account');
  console.log(`Found ${accounts.length} accounts`);
  if (accounts.length > 0) {
    await insertBatch(NEW_URL, NEW_KEY, 'Account', accounts);
    console.log(`✓ ${accounts.length} accounts migrated\n`);
  }

  // 4. Migrate Sessions
  console.log('Fetching Sessions...');
  const sessions = await fetchAll(OLD_URL, OLD_KEY, 'Session');
  console.log(`Found ${sessions.length} sessions`);
  if (sessions.length > 0) {
    await insertBatch(NEW_URL, NEW_KEY, 'Session', sessions);
    console.log(`✓ ${sessions.length} sessions migrated\n`);
  }

  // 5. Migrate Bookmarks
  console.log('Fetching Bookmarks...');
  const bookmarks = await fetchAll(OLD_URL, OLD_KEY, 'Bookmark');
  console.log(`Found ${bookmarks.length} bookmarks`);
  if (bookmarks.length > 0) {
    await insertBatch(NEW_URL, NEW_KEY, 'Bookmark', bookmarks);
    console.log(`✓ ${bookmarks.length} bookmarks migrated\n`);
  }

  // 6. Migrate OrganizerSubmissions
  console.log('Fetching OrganizerSubmissions...');
  const submissions = await fetchAll(OLD_URL, OLD_KEY, 'OrganizerSubmission');
  console.log(`Found ${submissions.length} organizer submissions`);
  if (submissions.length > 0) {
    await insertBatch(NEW_URL, NEW_KEY, 'OrganizerSubmission', submissions);
    console.log(`✓ ${submissions.length} organizer submissions migrated\n`);
  }

  // 7. Migrate PipelineRuns
  console.log('Fetching PipelineRuns...');
  const pipelineRuns = await fetchAll(OLD_URL, OLD_KEY, 'PipelineRun');
  console.log(`Found ${pipelineRuns.length} pipeline runs`);
  if (pipelineRuns.length > 0) {
    await insertBatch(NEW_URL, NEW_KEY, 'PipelineRun', pipelineRuns);
    console.log(`✓ ${pipelineRuns.length} pipeline runs migrated\n`);
  }

  // Verify
  console.log('\n=== Verification ===');
  const newHackathons = await fetchAll(NEW_URL, NEW_KEY, 'Hackathon', 'id');
  console.log(`New DB Hackathon count: ${newHackathons.length}`);
  const newUsers = await fetchAll(NEW_URL, NEW_KEY, 'User', 'id');
  console.log(`New DB User count: ${newUsers.length}`);
  
  console.log('\n✅ Migration complete!');
}

migrate().catch(err => {
  console.error('Migration failed:', err.message);
  process.exit(1);
});
