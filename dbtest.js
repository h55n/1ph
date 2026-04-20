require('dotenv').config({path: './apps/web/.env.local'});
const { PrismaClient } = require('./packages/db/node_modules/@prisma/client');
const prisma = new PrismaClient();
async function main() {
  const count = await prisma.hackathon.count();
  const runs = await prisma.pipelineRun.findMany({orderBy:{runAt:'desc'}, take:2});
  console.log('Hackathons:', count);
  console.log('Recent Runs:', runs);
}
main().finally(() => prisma.$disconnect());
