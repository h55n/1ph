const { Client } = require('pg');

async function testConnection(host, user, port) {
  const client = new Client({
    host,
    port,
    user,
    password: 'FbXwVCKJ7k4Y6GyG',
    database: 'postgres',
    ssl: { rejectUnauthorized: false }
  });
  try {
    await client.connect();
    console.log(`SUCCESS: ${host}:${port} with user ${user}`);
    await client.end();
  } catch (err) {
    console.log(`FAILED: ${host}:${port} with user ${user} - ${err.message}`);
  }
}

async function run() {
  const regions = ['ap-south-1', 'us-east-1', 'eu-central-1', 'ap-southeast-1'];
  for (const region of regions) {
    const host = `aws-0-${region}.pooler.supabase.com`;
    // Try old format
    await testConnection(host, 'postgres.flwrpsoizcinyrsukpcq', 6543);
    // Try new format
    await testConnection(host, 'postgres', 6543);
  }
}

run();
