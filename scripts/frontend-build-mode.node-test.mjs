import assert from 'node:assert/strict'
import test from 'node:test'

import { resolveFrontendBuildMode } from './frontend-build-mode.mjs'

test('Cloudflare dev branch selects the tracked pre-production configuration', () => {
  assert.equal(resolveFrontendBuildMode({ WORKERS_CI_BRANCH: 'dev' }), 'preprod')
})

test('Cloudflare main branch and local builds default to production', () => {
  assert.equal(resolveFrontendBuildMode({ WORKERS_CI_BRANCH: 'main' }), 'production')
  assert.equal(resolveFrontendBuildMode({}), 'production')
})

test('an explicit supported mode overrides branch detection', () => {
  assert.equal(resolveFrontendBuildMode({ WORKERS_CI_BRANCH: 'main' }, 'preprod'), 'preprod')
  assert.throws(
    () => resolveFrontendBuildMode({}, 'preview'),
    /Unsupported frontend build mode: preview/,
  )
})
