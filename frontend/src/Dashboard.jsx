import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchWithAuth } from './api';

export default function Dashboard() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    const loadProjects = async () => {
      try {
        const response = await fetchWithAuth('/api/studio/projects/');
        const data = await response.json();

        if (!active) return;

        if (response.ok) {
          setProjects(data);
        } else {
          setError('Não foi possível carregar os seus podcasts.');
        }
      } catch (err) {
        if (active) {
          setError('Erro ao conectar com o servidor.');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadProjects();

    return () => {
      active = false;
    };
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    navigate('/');
  };

  const formatDate = (value) => new Intl.DateTimeFormat('pt-PT', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(value));

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
          {loading ? (
            <div className="empty-state">
              <p>A carregar podcasts...</p>
            </div>
          ) : error ? (
            <div className="empty-state">
              <p>{error}</p>
            </div>
          ) : projects.length > 0 ? (
            projects.map((project) => (
              <div key={project.id} className="project-card">
                <div className="project-card-header">
                  <div className="waveform-mini" aria-hidden="true">
                    <i></i><i></i><i></i><i></i>
                  </div>
                  <span className="project-date">{formatDate(project.created_at)}</span>
                </div>
                <h3>{project.topic}</h3>
                <p className="project-details">
                  Agentes: {project.agents.join(' & ')} • {project.target_duration} min • {project.line_count} falas
                </p>
                <div className="project-card-actions">
                  <button className="play-btn" onClick={() => navigate(`/podcast/${project.id}`)}>Abrir Roteiro</button>
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
