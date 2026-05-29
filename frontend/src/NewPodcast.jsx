import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function NewPodcast() {
  const navigate = useNavigate();
  
  // Estados para as configurações globais
  const [topic, setTopic] = useState('');
  const [duration, setDuration] = useState(5); // Duração em minutos

  // Estados para os agentes 
  const [agent1, setAgent1] = useState({ voice: 'Voz A (Feminina Suave)', tone: 'Descontraído', traits: [] });
  const [agent2, setAgent2] = useState({ voice: 'Voz C (Masculino Grave)', tone: 'Provocativo', traits: [] });

  const availableVoices = ['Voz A (Feminina Suave)', 'Voz B (Feminina Dinâmica)', 'Voz C (Masculino Grave)', 'Voz D (Masculino Jovem)'];
  const availableTones = ['Neutro', 'Descontraído', 'Formal', 'Provocativo', 'Empático', 'Didático', 'Melancólico'];
  const availableTraits = ['Sarcástico', 'Profissional', 'Entusiasta', 'Casual', 'Sincero', 'Humorístico', 'Cético'];

  // Função para selecionar/deselecionar personalidade
  const toggleTrait = (agentNum, trait) => {
    const updateAgent = agentNum === 1 ? setAgent1 : setAgent2;
    const currentAgent = agentNum === 1 ? agent1 : agent2;

    if (currentAgent.traits.includes(trait)) {
      updateAgent({ ...currentAgent, traits: currentAgent.traits.filter(t => t !== trait) });
    } else if (currentAgent.traits.length < 3) {
      // Limita a 3 traços por agente
      updateAgent({ ...currentAgent, traits: [...currentAgent.traits, trait] });
    }
  };

  const handleGenerate = (e) => {
    e.preventDefault();
    if (!topic.trim()) {
      alert("Por favor, defina um tema para o podcast.");
      return;
    }
    
    alert("Gerar áudio clicado! Dados prontos para enviar ao backend.");
    console.log("Dados do Podcast:", { topic, duration, agent1, agent2 });
  };

  return (
    <main className="app config-app">
      <nav className="topbar">
        <strong>Podcaster</strong>
        <div className="topbar-actions">
          <button onClick={() => navigate('/dashboard')} className="logout-btn" style={{borderColor: 'rgba(255,248,238,0.3)', color: '#fff8ee'}}>
            Voltar ao Dashboard
          </button>
        </div>
      </nav>

      <div className="config-container">
        <header className="config-header">
          <p className="eyebrow">Novo Episódio</p>
          <h2>Configuração do Podcast</h2>
        </header>

        <form onSubmit={handleGenerate} className="config-form">
          {/* SECÇÃO GERAL */}
          <section className="config-section">
            <h3>1. O que vão discutir?</h3>
            <label className="config-label">
              <span>Tópico ou Prompt Base</span>
              <textarea 
                placeholder="Ex: A evolução da inteligência artificial nos próximos 10 anos..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                rows="3"
              />
            </label>
            
            <label className="config-label">
              <span>Duração Alvo: {duration} minutos</span>
              <input 
                type="range" 
                min="2" max="15" 
                value={duration} 
                onChange={(e) => setDuration(e.target.value)} 
                className="duration-slider"
              />
            </label>
          </section>

          {/* SECÇÃO DOS AGENTES */}
          <section className="config-section">
            <h3>2. Configure os Agentes</h3>
            <div className="agents-grid">
              
              {/* AGENTE 1 */}
              <div className="agent-card">
                <div className="agent-header">
                  <div className="agent-avatar">A1</div>
                  <h4>Agente 1 (Anfitrião)</h4>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                  <label className="config-label" style={{ marginBottom: 0 }}>
                    <span>Voz</span>
                    <select value={agent1.voice} onChange={(e) => setAgent1({...agent1, voice: e.target.value})}>
                      {availableVoices.map(v => <option key={v} value={v}>{v}</option>)}
                    </select>
                  </label>

                  <label className="config-label" style={{ marginBottom: 0 }}>
                    <span>Tom do Discurso</span>
                    <select value={agent1.tone} onChange={(e) => setAgent1({...agent1, tone: e.target.value})}>
                      {availableTones.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </label>
                </div>

                <div className="config-label">
                  <span>Traços de Personalidade (Máx 3)</span>
                  <div className="traits-container">
                    {availableTraits.map(trait => (
                      <button 
                        key={trait} type="button"
                        className={`trait-pill ${agent1.traits.includes(trait) ? 'active' : ''}`}
                        onClick={() => toggleTrait(1, trait)}
                      >
                        {trait}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* AGENTE 2 */}
              <div className="agent-card">
                <div className="agent-header">
                  <div className="agent-avatar agent2-color">A2</div>
                  <h4>Agente 2 (Convidado)</h4>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                  <label className="config-label" style={{ marginBottom: 0 }}>
                    <span>Voz</span>
                    <select value={agent2.voice} onChange={(e) => setAgent2({...agent2, voice: e.target.value})}>
                      {availableVoices.map(v => <option key={v} value={v}>{v}</option>)}
                    </select>
                  </label>

                  <label className="config-label" style={{ marginBottom: 0 }}>
                    <span>Tom do Discurso</span>
                    <select value={agent2.tone} onChange={(e) => setAgent2({...agent2, tone: e.target.value})}>
                      {availableTones.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                  </label>
                </div>

                <div className="config-label">
                  <span>Traços de Personalidade (Máx 3)</span>
                  <div className="traits-container">
                    {availableTraits.map(trait => (
                      <button 
                        key={trait} type="button"
                        className={`trait-pill ${agent2.traits.includes(trait) ? 'active' : ''}`}
                        onClick={() => toggleTrait(2, trait)}
                      >
                        {trait}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

            </div>
          </section>

          <button type="submit" className="generate-btn">
            Gerar Áudio do Podcast 
          </button>
        </form>
      </div>
    </main>
  );
}