import { spawnSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { resolveFrontendBuildMode } from './frontend-build-mode.mjs'

const mode = resolveFrontendBuildMode(process.env, process.argv[2])
const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const viteExecutable = path.join(
  repositoryRoot,
  'node_modules',
  '.bin',
  process.platform === 'win32' ? 'vite.cmd' : 'vite',
)

console.log(`[sulocraft] Building frontend in ${mode} mode`)

const result = spawnSync(viteExecutable, ['build', '--mode', mode], {
  cwd: repositoryRoot,
  env: process.env,
  stdio: 'inherit',
})

if (result.error) {
  throw result.error
}

process.exit(result.status ?? 1)
