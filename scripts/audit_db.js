const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient();

async function main() {
  const sources = await p.hackathon.groupBy({ 
    by: ['source'], 
    _count: { id: true }, 
    orderBy: { _count: { id: 'desc' } } 
  });
  const total = await p.hackathon.count();
  const closed = await p.hackathon.count({ where: { status: 'CLOSED' } });
  const open = await p.hackathon.count({ where: { status: 'OPEN' } });
  const upcoming = await p.hackathon.count({ where: { status: 'UPCOMING' } });
  const closing = await p.hackathon.count({ where: { status: 'CLOSING_SOON' } });
  const noPrize = await p.hackathon.count({ where: { prizePool: null } });

  // Sample 5 records to check data quality
  const sample = await p.hackathon.findMany({
    take: 5,
    orderBy: { createdAt: 'desc' },
    select: { title: true, source: true, prizePool: true, prizeDescription: true, registrationClose: true, eventStart: true, status: true, description: true }
  });

  console.log('=== SOURCE DISTRIBUTION ===');
  sources.forEach(s => console.log(`  ${s.source}: ${s._count.id} records`));
  console.log(`\n=== STATUS BREAKDOWN ===`);
  console.log(`  Total: ${total} | Open: ${open} | Closing Soon: ${closing} | Upcoming: ${upcoming} | Closed: ${closed}`);
  console.log(`\n=== DATA QUALITY ===`);
  console.log(`  No Prize Pool: ${noPrize}/${total} (${Math.round(noPrize/total*100)}%)`);
  console.log(`\n=== RECENT 5 SAMPLES ===`);
  sample.forEach(h => console.log(JSON.stringify({ title: h.title.slice(0, 50), source: h.source, prize: h.prizePool, prizeDesc: h.prizeDescription, regClose: h.registrationClose, eventStart: h.eventStart, status: h.status, descLen: (h.description || '').length })));
}

main().catch(console.error).finally(() => p.$disconnect());
