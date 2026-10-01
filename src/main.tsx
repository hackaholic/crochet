import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router'
import App from './App'
import { CatalogueProvider } from './components/CatalogueProvider'
import { CartProvider } from './components/CartProvider'
import { WishlistProvider } from './components/WishlistProvider'
import ComingSoonPage from './pages/ComingSoonPage'
import './index.css'

const rootElement = document.getElementById('root')!
const appContent = (
  <React.StrictMode>
    {import.meta.env.VITE_LAUNCH_MODE === 'coming-soon' ? (
      <ComingSoonPage />
    ) : (
      <BrowserRouter>
        <CatalogueProvider>
          <CartProvider>
            <WishlistProvider>
              <App />
            </WishlistProvider>
          </CartProvider>
        </CatalogueProvider>
      </BrowserRouter>
    )}
  </React.StrictMode>
)

if (rootElement.hasChildNodes()) {
  ReactDOM.hydrateRoot(rootElement, appContent)
} else {
  ReactDOM.createRoot(rootElement).render(appContent)
}

