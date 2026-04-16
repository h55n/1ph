// apps/pipeline/scheduler/run-once.ts
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

const CONNECTORS = [
  new MLHConnector(),
  new DoraHacksConnector(),
  new HackerEarthConnector(),
  new DevfolioConnector(),
  new StartupIndiaConnector(),
  new Hack2SkillConnector(),
  new ToplangConnector(),
  new HackerRankConnector(),
  new DevpostConnector(),
  new UnstopConnector(),
]

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

async function run(): Promise<void> {
  console.log('[PIPELINE] Starting GitHub Actions run...')

  for (let i = 0; i < CONNECTORS.length; i++) {
    await runConnector(CONNECTORS[i])
    if (i < CONNECTORS.length - 1) {
      await sleep(10000)
    }
  }

  console.log('[STATUS SWEEP] Running...')
  const sweep = await runStatusSweep()
  console.log('[STATUS SWEEP] Done:', sweep)
  console.log('[PIPELINE] Completed GitHub Actions run')
}

run().catch(err => {
  console.error('[PIPELINE] Fatal error in one-off run:', err)
  process.exit(1)
})
