import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return (
    <main className="app">
      <nav className="topbar" aria-label="Navegacao principal">
        <strong>Podcaster</strong>
        <span>Planejamento e Design</span>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow">Podcasts gerados por IA</p>
          <h1>Crie ideias para podcasts dinamicos com agentes artificiais.</h1>
          <p className="intro">
            Uma plataforma web para dirigir conversas entre agentes de IA,
            moldando tema, personalidade e tom antes da geracao do episodio.
          </p>
          <div className="status-card">
            <span>Status atual</span>
            <strong>Prototipo inicial de interface</strong>
          </div>
        </div>

        <aside className="preview-card" aria-label="Previa visual do produto">
          <div className="preview-header">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div className="waveform" aria-hidden="true">
            <i></i>
            <i></i>
            <i></i>
            <i></i>
            <i></i>
            <i></i>
            <i></i>
            <i></i>
          </div>
          <p>Estudio de criacao em breve</p>
        </aside>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
