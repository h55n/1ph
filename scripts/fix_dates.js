const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const result = await prisma.hackathon.updateMany({
    where: {
      OR: [
        { registrationClose: new Date('2099-12-31T00:00:00Z') },
        { eventStart: new Date('2099-12-31T00:00:00Z') }
      ]
    },
    data: {
      registrationClose: null,
      eventStart: null,
      eventEnd: null
    }
  });
  console.log(`Successfully fixed ${result.count} hackathons with placeholder 2099 dates.`);
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
