import type { PublicSeoPolicy } from './lib/seo/urlPolicy.mjs'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import StorefrontApplication from './components/StorefrontApplication'
import type { PublicBootstrap } from './lib/seo/bootstrap'
import ComingSoonPage from './pages/ComingSoonPage'
import './index.css'

const rootElement = document.getElementById('root')!
const bootstrapElement = document.getElementById('storefront-bootstrap')
const bootstrap: PublicBootstrap | undefined = bootstrapElement ? JSON.parse(bootstrapElement.textContent || 'null') : undefined
const policyElement = document.getElementById('storefront-policy')
const declaredPolicy: PublicSeoPolicy | undefined = policyElement ? JSON.parse(policyElement.textContent || 'null') : import.meta.env.DEV ? { origin: window.location.origin, indexing: false } : undefined
const policy = declaredPolicy ? {...declaredPolicy, indexing: declaredPolicy.indexing && !window.location.search} : undefined
const appContent = (
  <React.StrictMode>
    {import.meta.env.VITE_LAUNCH_MODE === 'coming-soon' ? (
      <ComingSoonPage />
    ) : (
      <StorefrontApplication policy={policy} bootstrap={bootstrap} router={children => <BrowserRouter>{children}</BrowserRouter>} />
    )}
  </React.StrictMode>
)

if (rootElement.hasChildNodes()) {
  ReactDOM.hydrateRoot(rootElement, appContent)
} else {
  ReactDOM.createRoot(rootElement).render(appContent)
}

