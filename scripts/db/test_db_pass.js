const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres.flwrpsoizcinyrsukpcq:hackatho13579@aws-0-ap-south-1.pooler.supabase.com:6543/postgres'
    }
  }
});
p.$connect()
  .then(() => console.log('CONNECTED! Password is correct.'))
  .catch(e => console.log('FAILED:', e.message))
  .finally(() => p.$disconnect());
