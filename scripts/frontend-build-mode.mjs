const VALID_MODES = new Set(['production', 'preprod'])

export function resolveFrontendBuildMode(environment = process.env, requestedMode) {
  if (requestedMode) {
    if (!VALID_MODES.has(requestedMode)) {
      throw new Error(`Unsupported frontend build mode: ${requestedMode}`)
    }
    return requestedMode
  }

  return environment.WORKERS_CI_BRANCH === 'dev' ? 'preprod' : 'production'
}
