# 1ph — Every hackathon. One place.

The cleanest hackathon directory on the internet. Built with a self-running AI pipeline that finds, enriches, and categorizes hackathons so you don't have to.

![1ph Logo](https://1ph.vercel.app/og-default.png)

## Why 1ph?

- **Zero Noise:** No ads, no sponsored bloat, no clutter. Just pure data.
- **AI-Enriched:** Our pipeline uses Mistral AI to extract real deadlines, prize pools, and descriptions from stub listings.
- **Global + Local:** Seamlessly switch between global prestige events and India-specific hackathons.
- **Fast:** Built with Next.js 14 and SSG for near-instant load times.
- **Open Source:** Made with ❤️ by hssn.

## Features

- **Status Tracking:** Instantly see what's Open, Closing Soon, or recently Closed.
- **Deep Filtering:** Filter by theme (AI, Web3, Fintech, etc.), mode (Online/Offline), entry fee, and team size.
- **Prestige Tiers:** Events are categorized by prestige so you can find the ones that matter.
- **Personalized:** Save hackathons to your bookmarks and track them.

---

## Technical Details

For developers looking to clone or contribute to the project.

### Structure

- `apps/web`: Next.js frontend (Vercel)
- `pipeline`: Python enrichment engine (GitHub Actions)
- `packages/db`: Shared Prisma schema and database client
- `scripts`: Utility scripts for database and deployment

### Quick Start

1. **Clone & Install:**
   ```bash
   npm install
   ```

2. **Frontend Setup:**
   ```bash
   cp .env.example apps/web/.env.local
   npm run dev
   ```

3. **Pipeline Setup:**
   ```bash
   cd pipeline && pip install -r requirements.txt
   python run.py
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Made with ❤️ by [hssn](https://github.com/h55n)
