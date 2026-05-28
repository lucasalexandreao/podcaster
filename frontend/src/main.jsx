import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return (
    <main className="app">
      <nav className="topbar" aria-label="Navegacao principal">
        <strong>Podcaster</strong>
        <span>Acesso ao estúdio</span>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow">Bem-vindo de volta</p>
          <h1>Entre para continuar sua producao de podcasts.</h1>
          <p className="intro">
            Acesse seu estúdio, acompanhe roteiros, ajuste vozes e siga do
            planejamento à gravação em uma única interface.
          </p>

          <div className="status-grid" aria-label="Destaques da plataforma">
            <div className="status-card">
              <span>Fluxo</span>
              <strong>Do briefing ao episódio final</strong>
            </div>
            <div className="status-card">
              <span>Equipe IA</span>
              <strong>Agentes alinhados ao seu tom</strong>
            </div>
          </div>
        </div>

        <aside className="login-card" aria-label="Formulario de login">
          <div className="login-card__header">
            <div>
              <p className="login-kicker">Login do produtor</p>
              <h2>Entrar na plataforma</h2>
            </div>
            <span className="login-badge">Seguro</span>
          </div>

          <form className="login-form">
            <label>
              <span>E-mail</span>
              <input type="email" name="email" placeholder="voce@estudio.com" />
            </label>

            <label>
              <span>Senha</span>
              <input type="password" name="password" placeholder="Digite sua senha" />
            </label>

            <div className="login-options">
              <label className="checkbox">
                <input type="checkbox" name="remember" />
                <span>Manter conectado</span>
              </label>

              <a href="#" onClick={(event) => event.preventDefault()}>
                Esqueci a senha
              </a>
            </div>

            <button type="submit">Entrar</button>
          </form>

          <div className="login-footer">
            <p>Primeira vez por aqui?</p>
            <a href="#" onClick={(event) => event.preventDefault()}>
              Criar conta
            </a>
          </div>
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
