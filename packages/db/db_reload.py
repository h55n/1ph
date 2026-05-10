import asyncio
from prisma import Prisma

async def main():
    prisma = Prisma()
    await prisma.connect()
    await prisma.execute_raw("NOTIFY pgrst, 'reload schema';")
    print("Schema reloaded.")
    await prisma.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
