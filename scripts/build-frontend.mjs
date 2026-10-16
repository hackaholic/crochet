import { loadEnv } from 'vite'
import { spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { resolveFrontendBuildMode } from './frontend-build-mode.mjs'

import { writeRoutingPolicy } from './routing-policy.mjs'
import { writeSeoResources, resourcePolicy } from './seo-resources.mjs'
import { prerender } from './prerender.mjs'

import fs from 'node:fs'

const mode = resolveFrontendBuildMode(process.env, process.argv[2])
const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const localVite = path.join(
  repositoryRoot,
  'node_modules',
  '.bin',
  process.platform === 'win32' ? 'vite.cmd' : 'vite',
)
const useLocal = fs.existsSync(localVite)
const executable = useLocal ? localVite : (process.platform === 'win32' ? 'npx.cmd' : 'npx')
const buildArgs = useLocal ? ['build', '--mode', mode] : ['vite', 'build', '--mode', mode]

const buildEnv = { ...loadEnv(mode, repositoryRoot, ''), ...process.env }
resourcePolicy(mode, buildEnv)
console.log(`[sulocraft] Building frontend in ${mode} mode`)

const result = spawnSync(executable, buildArgs, {
  cwd: repositoryRoot,
  env: process.env,
  stdio: 'inherit',
})

if (result.error) {
  throw result.error
}

if (result.status !== 0) {
  process.exit(result.status ?? 1)
}

const publicPolicy = await writeRoutingPolicy(repositoryRoot, mode, buildEnv)
if (buildEnv.VITE_LAUNCH_MODE !== 'coming-soon') {
  const server = spawnSync(executable, [...(useLocal ? [] : ['vite']), 'build', '--mode', mode, '--ssr', 'src/entry-server.tsx', '--outDir', '.seo-render'], { cwd: repositoryRoot, env: process.env, stdio: 'inherit' })
  if (server.error) throw server.error
  if (server.status !== 0) process.exit(server.status ?? 1)
  await prerender({ repositoryRoot, baseUrl: buildEnv.SEO_API_BASE_URL || buildEnv.VITE_API_BASE_URL, policy: publicPolicy })
}

await writeSeoResources({ repositoryRoot, mode, environment: buildEnv })
const budget = spawnSync(process.execPath, [path.join(repositoryRoot, 'scripts/performance/budgets.mjs'), path.join(repositoryRoot, 'dist')], { cwd: repositoryRoot, env: buildEnv, stdio: 'inherit' })
if (budget.error) throw budget.error
if (budget.status !== 0) process.exit(budget.status ?? 1)
process.exit(0)

