import { spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { resolveFrontendBuildMode } from './frontend-build-mode.mjs'

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

if (process.env.VITE_LAUNCH_MODE !== 'coming-soon') {
  prerender()
}

process.exit(0)

