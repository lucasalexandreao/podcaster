// Função para fazer requisição ao Django de forma autenticada
export const fetchWithAuth = async (endpoint, options = {}) => {
    const baseURL = 'http://127.0.0.1:8000';
    
    let token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    // Faz a requisição original
    let response = await fetch(`${baseURL}${endpoint}`, { ...options, headers });

    // Se o token estiver expirado
    if (response.status === 401) {
        const refresh = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
        const storage = localStorage.getItem('refresh_token') ? localStorage : sessionStorage;
        
        if (refresh) {
            // Tenta obter um novo token de acesso usando o refresh token
            const refreshResponse = await fetch(`${baseURL}/api/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            });

            if (refreshResponse.ok) {
                const data = await refreshResponse.json();
                
                // Atualiza o token no navegador
                storage.setItem('access_token', data.access);
                
                // Atualiza o cabeçalho e refaz o pedido original
                headers['Authorization'] = `Bearer ${data.access}`;
                response = await fetch(`${baseURL}${endpoint}`, { ...options, headers });
            } else {
                // Se o refresh token também expirou, limpa tudo e redireciona para o login
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = '/';
            }
        }
    }

    return response;
};