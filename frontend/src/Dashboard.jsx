import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    navigate('/');
  };

  // MOCKS
  const projects = [
    { id: 1, title: 'O Futuro da IA na Saúde', duration: '12 min', date: '28 Mai 2026', agents: ['Ana', 'Carlos'] },
    { id: 2, title: 'Mercado Financeiro Global', duration: '8 min', date: '25 Mai 2026', agents: ['Sofia', 'João'] },
    { id: 3, title: 'Review: Novos Gadgets', duration: '15 min', date: '20 Mai 2026', agents: ['TechBot', 'Ana'] },
    { id: 1, title: 'O Futuro da IA na Saúde', duration: '12 min', date: '28 Mai 2026', agents: ['Ana', 'Carlos'] },
    { id: 2, title: 'Mercado Financeiro Global', duration: '8 min', date: '25 Mai 2026', agents: ['Sofia', 'João'] },
    { id: 3, title: 'Review: Novos Gadgets', duration: '15 min', date: '20 Mai 2026', agents: ['TechBot', 'Ana'] },
  ];

  return (
    <main className="app dashboard-app">
      <nav className="topbar" aria-label="Navegação principal">
        <strong>Podcaster</strong>
        <div className="topbar-actions">
          <span>O Meu Estúdio</span>
          <button onClick={handleLogout} className="logout-btn">Sair</button>
        </div>
      </nav>

      <section className="dashboard-content">
        <header className="dashboard-header">
          <div>
            <p className="eyebrow">Gestão de Projetos</p>
            <h2>Os Meus Podcasts</h2>
          </div>
          <button 
            className="primary-btn" 
            onClick={() => navigate('/novo-podcast')}
          >
            + Novo Podcast
          </button>
        </header>

        <div className="projects-grid">
          {projects.length > 0 ? (
            projects.map((project) => (
              <div key={project.id} className="project-card">
                <div className="project-card-header">
                  <div className="waveform-mini" aria-hidden="true">
                    <i></i><i></i><i></i><i></i>
                  </div>
                  <span className="project-date">{project.date}</span>
                </div>
                <h3>{project.title}</h3>
                <p className="project-details">
                  Agentes: {project.agents.join(' & ')} • {project.duration}
                </p>
                <div className="project-card-actions">
                  <button className="play-btn">▶ Ouvir Episódio</button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <p>Ainda não criou nenhum podcast. Comece a dirigir a sua equipe de IA!</p>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}