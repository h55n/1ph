const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:REDACTED_DB_PASSWORD@db.flwrpsoizcinyrsukpcq.supabase.co:5432/postgres'
    }
  }
});
p.$connect()
  .then(() => console.log('CONNECTED! Password is correct.'))
  .catch(e => console.log('FAILED:', e.message))
  .finally(() => p.$disconnect());
