import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate();

  // Estados do formulário
  const [isLoginView, setIsLoginView] = useState(true); // Controla se estamos no Login ou Cadastro
  const [isForgotView, setIsForgotView] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState(''); // Apenas para o cadastro
  const [rememberMe, setRememberMe] = useState(false); // Para o "Manter conectado"
  
  // Estados de feedback
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  // Função que lida tanto com Login quanto Cadastro
  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (!isLoginView && password !== confirmPassword) {
      setError('As senhas não coincidem!');
      setLoading(false);
      return;
    }

    try {
      if (isLoginView) {
        // ======================= LÓGICA DE LOGIN =======================
        const response = await fetch('http://127.0.0.1:8000/api/login/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: email, password: password }),
        });

        const data = await response.json();

        if (response.ok) {
          // Lógica do Manter Conectado
          const storage = rememberMe ? localStorage : sessionStorage;
          storage.setItem('access_token', data.access);
          storage.setItem('refresh_token', data.refresh);
          
          navigate('/dashboard');
          // redireciona para o Dashboard 
        } else {
          setError('E-mail ou senha incorretos.');
        }

      } else {
        // ======================= LÓGICA DE CADASTRO =======================
        const response = await fetch('http://127.0.0.1:8000/api/register/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email, password: password }),
        });

        if (response.status === 201) {
          setSuccess('Conta criada com sucesso! Faça login para continuar.');
          setIsLoginView(true); // Volta para a tela de login
          setPassword(''); 
          setConfirmPassword('');
        } else {
          const data = await response.json();
          setError(data.email ? data.email[0] : 'Erro ao criar conta. Tente novamente.');
        }
      }
    } catch (err) {
      setError('Erro ao conectar com o servidor. Verifique se o backend está rodando.');
    } finally {
      setLoading(false);
    }
  };

  // Função para alternar entre as telas limpando os erros
  const toggleView = (event) => {
    event.preventDefault();
    setIsLoginView(!isLoginView);
    setIsForgotView(false);
    setError('');
    setSuccess('');
    setPassword('');
    setConfirmPassword('');
  };

  // Função para envio do e-mail de recuperação de senha
  const handleForgotPassword = async (event) => {
    event.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/password-reset/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email }),
      });

      if (response.ok) {
        setSuccess('Se o e-mail existir, receberá um link de recuperação em breve.');
      } else {
        setError('Ocorreu um erro ao processar o pedido.');
      }
    } catch (err) {
      setError('Erro ao conectar com o servidor.');
    } finally {
      setLoading(false);
    }
  };


  return (
    <main className="app">
      <nav className="topbar" aria-label="Navegacao principal">
        <strong>Podcaster</strong>
        <span>Acesso ao estúdio</span>
      </nav>

      <section className="hero">
        <div className="hero-content">
          <p className="eyebrow">{isLoginView ? 'Bem-vindo de volta' : 'Comece agora'}</p>
          <h1>{isLoginView ? 'Entre para continuar sua produção de podcasts.' : 'Crie seu estúdio de IA e dirija conversas.'}</h1>
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
              <p className="login-kicker">
                {isForgotView ? 'Recuperação' : (isLoginView ? 'Login do produtor' : 'Novo produtor')}
              </p>
              <h2>
                {isForgotView ? 'Recuperar senha' : (isLoginView ? 'Entrar na plataforma' : 'Criar nova conta')}
              </h2>
            </div>
            <span className="login-badge">Seguro</span>
          </div>

          { isForgotView ? (
            <form className="login-form" onSubmit={handleForgotPassword}>
              <p style={{ color: 'rgba(255,248,238,0.7)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                Introduza o seu e-mail e enviaremos um link para redefinir a sua senha.
              </p>
              
              <label>
                <span>E-mail</span>
                <input 
                  type="email" 
                  placeholder="voce@estudio.com" 
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </label>

              {error && <p style={{ color: '#ff6f61', fontSize: '0.9rem', margin: '0' }}>{error}</p>}
              {success && <p style={{ color: '#4ade80', fontSize: '0.9rem', margin: '0' }}>{success}</p>}

              <button type="submit" disabled={loading}>
                {loading ? 'A enviar...' : 'Enviar link de recuperação'}
              </button>
              
              <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                <a href="#" onClick={(e) => { e.preventDefault(); setIsForgotView(false); }} style={{ color: '#ffb86b', textDecoration: 'none', fontSize: '0.9rem' }}>
                  Voltar ao Login
                </a>
              </div>
            </form>
          ) : (
          <form className="login-form" onSubmit={handleSubmit}>
            <label>
              <span>E-mail</span>
              <input 
                type="email" 
                placeholder="voce@estudio.com" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>

            <label>
              <span>Senha</span>
              <input 
                type="password" 
                placeholder={isLoginView ? "Digite sua senha" : "Crie uma senha forte"} 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>

            {!isLoginView && (
              <label>
                <span>Confirmar Senha</span>
                <input 
                  type="password" 
                  placeholder="Repita sua senha" 
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </label>
            )}

            {isLoginView && (
              <div className="login-options">
                <label className="checkbox">
                  <input 
                    type="checkbox" 
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <span>Manter conectado</span>
                </label>

                <a href="#" onClick={(event) => { event.preventDefault(); setIsForgotView(true); }}>
                  Esqueci a senha
                </a>
              </div>
            )}

            {error && <p style={{ color: '#ff6f61', fontSize: '0.9rem', margin: '0' }}>{error}</p>}
            {success && <p style={{ color: '#4ade80', fontSize: '0.9rem', margin: '0' }}>{success}</p>}

            <button type="submit" disabled={loading}>
              {loading ? 'Processando...' : (isLoginView ? 'Entrar' : 'Criar Conta')}
            </button>
          </form>
        )}

          <div className="login-footer">
            <p>{isLoginView ? 'Primeira vez por aqui?' : 'Já possui um estúdio?'}</p>
            <a href="#" onClick={toggleView}>
              {isLoginView ? 'Criar conta' : 'Fazer login'}
            </a>
          </div>
        </aside>
      </section>
    </main>
  );
}

