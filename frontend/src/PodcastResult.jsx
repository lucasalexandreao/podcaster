import React, { useEffect, useRef, useState } from 'react';
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
  const [directorLog, setDirectorLog] = useState([]);
  const [directorInput, setDirectorInput] = useState('');
  const [directorSending, setDirectorSending] = useState(false);
  const directorEndRef = useRef(null);
  const [speed, setSpeed] = useState(0);
  const pollFailures = useRef(0);
  const MAX_POLL_FAILURES = 4;
  const [audioError, setAudioError] = useState('');

  const SPEEDS = [
    { label: 'Rápido', delay: 0 },
    { label: 'Médio', delay: 5 },
    { label: 'Lento', delay: 10 },
  ];

  const handleSpeedChange = async (delay) => {
    setSpeed(delay);
    await fetchWithAuth(`/api/studio/projects/${id}/speed/`, {
      method: 'PATCH',
      body: JSON.stringify({ delay }),
    });
  };

  useEffect(() => {
    let active = true;
    let intervalId;

    const loadProject = async () => {
      try {
        const response = await fetchWithAuth(`/api/studio/projects/${id}/`);
        const data = await response.json();

        if (!active) return;

        if (response.ok) {
          pollFailures.current = 0;
          setError('');
          setProject(data);
          setSpeed((prev) => (prev === data.line_delay ? prev : data.line_delay));
          setDrafts((current) => {
            const next = { ...current };
            data.lines.forEach((line) => {
              if (next[line.id] === undefined) {
                next[line.id] = line.text;
              }
            });
            return next;
          });

        } else {
          pollFailures.current += 1;
          if (pollFailures.current >= MAX_POLL_FAILURES) {
            clearInterval(intervalId);
            setError('Sem ligação ao servidor. Recarregue a página para continuar.');
          }
        }
      } catch {
        if (!active) return;
        pollFailures.current += 1;
        if (pollFailures.current >= MAX_POLL_FAILURES) {
          clearInterval(intervalId);
          setError('Sem ligação ao servidor. Recarregue a página para continuar.');
        } else {
          setError('Erro de ligação. A tentar novamente…');
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

  const handleDirectorSend = async () => {
    const text = directorInput.trim();
    if (!text || directorSending) return;
    setDirectorSending(true);
    const timestamp = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    try {
      const response = await fetchWithAuth(`/api/studio/projects/${id}/director/`, {
        method: 'POST',
        body: JSON.stringify({ text }),
      });
      if (response.ok) {
        setDirectorLog((log) => [...log, { text, timestamp }]);
        setDirectorInput('');
        setTimeout(() => directorEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50);
      }
    } finally {
      setDirectorSending(false);
    }
  };

  const handleGenerateAudio = async () => {
    setAudioError('');
    try {
      const response = await fetchWithAuth(`/api/studio/projects/${id}/generate-audio/`, { method: 'POST' });
      if (response.ok) {
        setProject((p) => ({ ...p, audio_status: 'generating' }));
      } else {
        setAudioError('Não foi possível iniciar a geração de áudio.');
      }
    } catch {
      setAudioError('Erro ao conectar com o servidor.');
    }
  };

  const handleDirectorKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleDirectorSend();
    }
  };

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
            <div className="live-generation-row">
              <div className="live-generation" aria-live="polite">
                <i></i>
                <p>Gerando ao vivo...</p>
              </div>
              <div className="speed-picker" role="group" aria-label="Velocidade de geração">
                {SPEEDS.map(({ label, delay }) => (
                  <button
                    key={delay}
                    type="button"
                    className={`speed-btn${speed === delay ? ' speed-btn--active' : ''}`}
                    onClick={() => handleSpeedChange(delay)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </header>

        {error && (
          <div className="poll-error">
            <p className="form-error">{error}</p>
            {pollFailures.current >= MAX_POLL_FAILURES && (
              <button className="poll-error__reload" onClick={() => window.location.reload()}>
                Recarregar
              </button>
            )}
          </div>
        )}
        {isFailed && <p className="form-error">A geração foi interrompida. Pode voltar ao dashboard e tentar criar outro roteiro.</p>}

        {isGenerating && (
          <div className="director-panel">
            <p className="eyebrow" style={{ margin: 0 }}>Cabine do Diretor</p>
            <div className="director-log" aria-live="polite" aria-label="Mensagens enviadas ao elenco">
              {directorLog.length === 0 ? (
                <p className="director-empty">Envie uma instrução e os agentes irão considerá-la na próxima fala.</p>
              ) : (
                directorLog.map((msg, i) => (
                  <div key={i} className="director-message">
                    <span className="director-message__text">{msg.text}</span>
                    <span className="director-message__time">{msg.timestamp}</span>
                  </div>
                ))
              )}
              <div ref={directorEndRef} />
            </div>
            <form
              className="director-form"
              onSubmit={(e) => { e.preventDefault(); handleDirectorSend(); }}
            >
              <textarea
                className="director-input"
                value={directorInput}
                onChange={(e) => setDirectorInput(e.target.value)}
                onKeyDown={handleDirectorKeyDown}
                placeholder="Ex: fale mais sobre o impacto econômico..."
                rows={2}
                disabled={directorSending}
                aria-label="Instrução para os agentes"
              />
              <button
                type="submit"
                className="director-send-btn"
                disabled={!directorInput.trim() || directorSending}
              >
                {directorSending ? '...' : 'Enviar'}
              </button>
            </form>
          </div>
        )}

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
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    {line.used_web_search && (
                      <span className="web-search-badge" title="Esta fala usou pesquisa web">Pesquisado</span>
                    )}
                    <span>{line.speaker_role}</span>
                  </div>
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

        {!isGenerating && !isFailed && (
          <section className="audio-section">
            <p className="eyebrow audio-section__title">Áudio do Episódio</p>
            {audioError && <p className="form-error">{audioError}</p>}
            {project.audio_status === 'pending' && (
              <button className="audio-generate-btn" onClick={handleGenerateAudio}>
                Gerar Áudio do Episódio
              </button>
            )}
            {project.audio_status === 'generating' && (
              <div className="live-generation">
                <i></i>
                <p>Sintetizando falas… isso pode levar alguns minutos.</p>
              </div>
            )}
            {project.audio_status === 'ready' && (
              <div className="audio-ready">
                <audio className="audio-player" controls src={project.audio_file} />
                <a className="audio-download-btn" href={project.audio_file} download>
                  Baixar Episódio
                </a>
              </div>
            )}
            {project.audio_status === 'failed' && (
              <>
                <p className="form-error">A síntese de áudio falhou. Verifique as configurações e tente novamente.</p>
                <button className="audio-generate-btn" onClick={handleGenerateAudio}>
                  Tentar Novamente
                </button>
              </>
            )}
          </section>
        )}
      </section>
    </main>
  );
}
