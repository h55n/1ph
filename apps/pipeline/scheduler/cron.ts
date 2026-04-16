// apps/pipeline/scheduler/cron.ts
import express from 'express'
import { Queue, Worker } from 'bullmq'
import IORedis from 'ioredis'
import 'dotenv/config'

import { MLHConnector } from '../connectors/mlh'
import { DoraHacksConnector } from '../connectors/dorahacks'
import { HackerEarthConnector } from '../connectors/hackerearth'
import { DevfolioConnector } from '../connectors/devfolio'
import { StartupIndiaConnector } from '../connectors/startup-india'
import { Hack2SkillConnector } from '../connectors/hack2skill'
import { ToplangConnector } from '../connectors/toplang'
import { HackerRankConnector } from '../connectors/hackerrank'
import { DevpostConnector } from '../connectors/devpost'
import { UnstopConnector } from '../connectors/unstop'
import { runConnector } from '../orchestrator'
import { runStatusSweep } from '../status-sweep/index'

const connection = new IORedis(process.env.REDIS_URL ?? 'redis://localhost:6379', {
  maxRetriesPerRequest: null,
})

const queue = new Queue('pipeline', { connection })

// Register all connectors — order matters:
// Easy REST/Cheerio sources first, high-block-risk Puppeteer scrapers last (R1)
const CONNECTORS = [
  new MLHConnector(),          // Axios + Cheerio — simplest
  new DoraHacksConnector(),    // REST API
  new HackerEarthConnector(),  // REST API
  new DevfolioConnector(),     // REST (GraphQL-style)
  new StartupIndiaConnector(), // Axios + Cheerio
  new Hack2SkillConnector(),   // Axios + Cheerio
  new ToplangConnector(),      // Axios + Cheerio
  new HackerRankConnector(),   // Puppeteer
  // High block risk — always last (R1 mitigation)
  new DevpostConnector(),      // Puppeteer ⚠️
  new UnstopConnector(),       // Puppeteer ⚠️
]

// Worker processes jobs
new Worker(
  'pipeline',
  async job => {
    const connector = CONNECTORS.find(c => c.source === job.data.source)
    if (!connector) {
      console.error(`No connector found for source: ${job.data.source}`)
      return
    }
    await runConnector(connector)

    // After all connectors done, run status sweep
    if (job.data.source === CONNECTORS[CONNECTORS.length - 1].source) {
      console.log('[STATUS SWEEP] Running...')
      const sweep = await runStatusSweep()
      console.log('[STATUS SWEEP] Done:', sweep)
    }
  },
  {
    connection,
    concurrency: 3,
    limiter: { max: 3, duration: 1000 },
  }
)

// Express server — receives webhook trigger from GitHub Actions
const app = express()
app.use(express.json())

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', connectors: CONNECTORS.map(c => c.source) })
})

app.post('/trigger', async (req, res) => {
  // Verify webhook secret
  const authHeader = req.headers.authorization ?? ''
  const token = authHeader.replace('Bearer ', '')
  if (token !== process.env.PIPELINE_WEBHOOK_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' })
  }

  console.log('[TRIGGER] Queueing all connectors...')

  // Enqueue one job per connector with 10s spacing
  for (let i = 0; i < CONNECTORS.length; i++) {
    await queue.add(
      'run',
      { source: CONNECTORS[i].source },
      { delay: i * 10000, attempts: 3, backoff: { type: 'exponential', delay: 30000 } }
    )
  }

  res.json({ queued: true, sources: CONNECTORS.map(c => c.source) })
})

const PORT = process.env.PORT ?? 3001
app.listen(PORT, () => {
  console.log(`[PIPELINE] Server running on port ${PORT}`)
  console.log(`[PIPELINE] Connectors: ${CONNECTORS.map(c => c.source).join(', ')}`)
})
