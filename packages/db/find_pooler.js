const { PrismaClient } = require('@prisma/client');

async function testConnection(url) {
  const p = new PrismaClient({
    datasources: { db: { url } }
  });
  try {
    await p.$connect();
    console.log(`SUCCESS: ${url}`);
    await p.$disconnect();
    return true;
  } catch (err) {
    console.log(`FAILED: ${url} - ${err.message}`);
    await p.$disconnect();
    return false;
  }
}

async function run() {
  const regions = ['ap-south-1', 'us-east-1', 'us-west-1', 'eu-central-1', 'ap-southeast-1', 'eu-west-1', 'eu-west-2'];
  for (const region of regions) {
    const host = `aws-0-${region}.pooler.supabase.com`;
    // Try old format
    const url1 = `postgresql://postgres.flwrpsoizcinyrsukpcq:FbXwVCKJ7k4Y6GyG@${host}:6543/postgres?pgbouncer=true`;
    if (await testConnection(url1)) return;
    
    // Try new format
    const url2 = `postgresql://postgres:FbXwVCKJ7k4Y6GyG@${host}:6543/postgres?pgbouncer=true`;
    if (await testConnection(url2)) return;
  }
}

run();
