import React, { StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Find the root element safely
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Failed to find the root element');
}

// Render the app with improved error handling and lazy loading
createRoot(rootElement).render(
  <StrictMode>
    <Suspense fallback={<div className="loading-screen">Loading...</div>}>
      <App />
    </Suspense>
  </StrictMode>
);
