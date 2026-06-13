import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { fetchWithAuth } from './api';

export default function PodcastResult() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [drafts, setDrafts] = useState({});
  const [savingLine, setSavingLine] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    let intervalId;

    const loadProject = async () => {
      try {
        const response = await fetchWithAuth(`/api/studio/projects/${id}/`);
        const data = await response.json();

        if (!active) return;

        if (response.ok) {
          setProject(data);
          setDrafts((current) => {
            const next = { ...current };
            data.lines.forEach((line) => {
              if (next[line.id] === undefined) {
                next[line.id] = line.text;
              }
            });
            return next;
          });

          if (data.status !== 'generating' && intervalId) {
            clearInterval(intervalId);
          }
        } else {
          setError('Não foi possível carregar este roteiro.');
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

    loadProject();
    intervalId = setInterval(loadProject, 2000);

    return () => {
      active = false;
      clearInterval(intervalId);
    };
  }, [id]);

  const handleDraftChange = (lineId, value) => {
    setDrafts((current) => ({ ...current, [lineId]: value }));
  };

  const handleSaveLine = async (lineId) => {
    setSavingLine(lineId);
    setError('');

    try {
      const response = await fetchWithAuth(`/api/studio/projects/${id}/lines/${lineId}/`, {
        method: 'PATCH',
        body: JSON.stringify({ text: drafts[lineId] }),
      });
      const data = await response.json();

      if (!response.ok) {
        setError(data.text?.[0] || 'Não foi possível salvar esta fala.');
        return;
      }

      setProject((current) => ({
        ...current,
        lines: current.lines.map((line) => (line.id === lineId ? data : line)),
      }));
      setDrafts((current) => ({ ...current, [lineId]: data.text }));
    } catch (err) {
      setError('Erro ao conectar com o servidor.');
    } finally {
      setSavingLine(null);
    }
  };

  if (loading) {
    return (
      <main className="app result-app">
        <nav className="topbar"><strong>Podcaster</strong></nav>
        <section className="result-container"><p>A carregar roteiro...</p></section>
      </main>
    );
  }

  if (error && !project) {
    return (
      <main className="app result-app">
        <nav className="topbar">
          <strong>Podcaster</strong>
          <button onClick={() => navigate('/dashboard')} className="logout-btn">Voltar</button>
        </nav>
        <section className="result-container"><p className="form-error">{error}</p></section>
      </main>
    );
  }

  const isGenerating = project.status === 'generating';
  const isFailed = project.status === 'failed';

  return (
    <main className="app result-app">
      <nav className="topbar">
        <strong>Podcaster</strong>
        <div className="topbar-actions">
          <button onClick={() => navigate('/dashboard')} className="logout-btn" style={{borderColor: 'rgba(255,248,238,0.3)', color: '#fff8ee'}}>
            Voltar ao Dashboard
          </button>
        </div>
      </nav>

      <section className="result-container">
        <header className="result-header">
          <p className="eyebrow">Roteiro Persistido</p>
          <h2>{project.topic}</h2>
          <div className="result-meta">
            <span>{project.target_duration} min alvo</span>
            <span>{project.lines.length} falas editáveis</span>
            <span>{isGenerating ? 'Gerando roteiro...' : isFailed ? 'Geração falhou' : 'Roteiro concluído'}</span>
          </div>
          {isGenerating && (
            <div className="live-generation" aria-live="polite">
              <i></i>
              <p>Recebendo novas falas do backend a cada poucos segundos.</p>
            </div>
          )}
        </header>

        {error && <p className="form-error">{error}</p>}
        {isFailed && <p className="form-error">A geração foi interrompida. Pode voltar ao dashboard e tentar criar outro roteiro.</p>}

        <div className="chat-script" aria-label="Roteiro em formato de chat">
          {project.lines.length === 0 && isGenerating ? (
            <div className="empty-state live-empty-state">
              <p>A primeira fala ainda está sendo preparada...</p>
            </div>
          ) : project.lines.map((line) => {
            const isAgentTwo = line.speaker_key === 'agent2';
            const changed = drafts[line.id] !== line.text;

            return (
              <article key={line.id} className={`chat-line ${isAgentTwo ? 'chat-line--right' : ''}`}>
                <div className="speaker-badge">
                  <strong>{line.speaker_name}</strong>
                  <span>{line.speaker_role}</span>
                </div>
                <textarea
                  value={drafts[line.id] || ''}
                  onChange={(event) => handleDraftChange(line.id, event.target.value)}
                  rows={4}
                  aria-label={`Fala de ${line.speaker_name}`}
                />
                <button
                  type="button"
                  className="save-line-btn"
                  disabled={!changed || savingLine === line.id}
                  onClick={() => handleSaveLine(line.id)}
                >
                  {savingLine === line.id ? 'Salvando...' : changed ? 'Salvar fala' : 'Salvo'}
                </button>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}
