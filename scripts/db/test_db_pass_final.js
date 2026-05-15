const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:FbXwVCKJ7k4Y6GyG@db.flwrpsoizcinyrsukpcq.supabase.co:6543/postgres?pgbouncer=true'
    }
  }
});
p.$connect()
  .then(async () => {
    console.log('CONNECTED! Pooler works.');
    const count = await p.hackathon.count();
    console.log(`Hackathons count: ${count}`);
  })
  .catch(e => console.log('FAILED 6543:', e.message))
  .finally(() => p.$disconnect());

const p2 = new PrismaClient({
  datasources: {
    db: {
      url: 'postgresql://postgres:FbXwVCKJ7k4Y6GyG@db.flwrpsoizcinyrsukpcq.supabase.co:5432/postgres'
    }
  }
});
p2.$connect()
  .then(() => console.log('CONNECTED! Direct 5432 works.'))
  .catch(e => console.log('FAILED 5432:', e.message))
  .finally(() => p2.$disconnect());
