/**
 * fix_db_cleanup.js
 * Aggressively cleans up bad data:
 * 1. Removes all 2099 placeholder dates
 * 2. Marks hackathons with past reg dates as CLOSED
 * 3. Removes test/garbage records
 */
const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient();

const STUB_DATE = new Date('2099-12-31T00:00:00Z');
const TODAY = new Date();

async function main() {
  console.log('=== 1ph DB CLEANUP ===\n');

  // Step 1: Find and log 2099 records
  const stub2099 = await p.hackathon.findMany({
    where: { registrationClose: STUB_DATE },
    select: { id: true, title: true, source: true, applyUrl: true }
  });
  console.log(`Found ${stub2099.length} records with 2099 placeholder dates`);

  // Step 2: NULL out 2099 dates (set to null so enrichment can fill them)
  if (stub2099.length > 0) {
    const ids2099 = stub2099.map(h => h.id);
    const cleaned = await p.hackathon.updateMany({
      where: { id: { in: ids2099 } },
      data: {
        registrationClose: null,
        eventStart: null,
        eventEnd: null,
        // Set these to OPEN so they're visible but enrichment will correct them
        status: 'OPEN'
      }
    });
    console.log(`  ✓ Nulled dates for ${cleaned.count} records`);
  }

  // Step 3: Also check for 2099-01-01 eventStart variant
  const stub2099b = await p.hackathon.findMany({
    where: { eventStart: new Date('2099-01-01T00:00:00Z') },
    select: { id: true }
  });
  if (stub2099b.length > 0) {
    await p.hackathon.updateMany({
      where: { id: { in: stub2099b.map(h => h.id) } },
      data: { eventStart: null, eventEnd: null }
    });
    console.log(`  ✓ Also nulled ${stub2099b.length} records with 2099-01-01 eventStart`);
  }

  // Step 4: Mark past hackathons as CLOSED (registrationClose < today, not null)
  // We check registrationClose < 7 days ago to avoid closing very recent ones
  const sevenDaysAgo = new Date(TODAY.getTime() - 7 * 24 * 60 * 60 * 1000);
  const pastHackathons = await p.hackathon.findMany({
    where: {
      registrationClose: { lt: sevenDaysAgo },
      status: { not: 'CLOSED' }
    },
    select: { id: true, title: true, registrationClose: true }
  });
  console.log(`\nFound ${pastHackathons.length} hackathons with past dates not marked CLOSED`);
  
  if (pastHackathons.length > 0) {
    const pastIds = pastHackathons.map(h => h.id);
    const closedResult = await p.hackathon.updateMany({
      where: { id: { in: pastIds } },
      data: { status: 'CLOSED' }
    });
    console.log(`  ✓ Marked ${closedResult.count} hackathons as CLOSED`);
    pastHackathons.slice(0, 5).forEach(h => 
      console.log(`    - ${h.title.slice(0, 50)} | closed: ${h.registrationClose}`)
    );
  }

  // Step 5: Delete test/garbage records
  const garbage = await p.hackathon.deleteMany({
    where: {
      OR: [
        { title: { contains: 'Test Hackathon', mode: 'insensitive' } },
        { title: { contains: 'test test', mode: 'insensitive' } },
      ]
    }
  });
  console.log(`\n  ✓ Deleted ${garbage.count} test/garbage records`);

  // Step 6: Final stats
  const total = await p.hackathon.count();
  const open = await p.hackathon.count({ where: { status: 'OPEN' } });
  const closing = await p.hackathon.count({ where: { status: 'CLOSING_SOON' } });
  const upcoming = await p.hackathon.count({ where: { status: 'UPCOMING' } });
  const closed = await p.hackathon.count({ where: { status: 'CLOSED' } });
  
  console.log(`\n=== FINAL DB STATE ===`);
  console.log(`Total: ${total} | Open: ${open} | Closing Soon: ${closing} | Upcoming: ${upcoming} | Closed: ${closed}`);
  console.log('\nCleanup complete!');
}

main().catch(console.error).finally(() => p.$disconnect());
