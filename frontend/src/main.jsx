import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return (
    <main className="app">
      <section className="card">
        <p className="eyebrow">React + Vite</p>
        <h1>Basic React App</h1>
        <p>Edit <code>src/main.jsx</code> and save to reload.</p>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
