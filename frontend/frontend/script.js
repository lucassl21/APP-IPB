document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-cadastro');
    const messageArea = document.getElementById('message-area');

    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Impede o envio do formulário padrão

        // Coleta os dados do formulário
        const email = document.getElementById('email').value;
        const cpf = document.getElementById('cpf').value;
        const senha = document.getElementById('senha').value;

        // Limpa mensagens anteriores
        messageArea.style.display = 'none';
        messageArea.textContent = '';
        messageArea.className = 'message';

        try {
            // Envia os dados para o endpoint do seu backend
            const response = await fetch('http://127.0.0.1:8000/users/register-first-stage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, cpf, senha })
            });

            const result = await response.json();

            // Verifica se a requisição foi bem-sucedida
            if (response.ok) {
                messageArea.textContent = 'Primeira etapa concluída! Prossiga para o cadastro completo.';
                messageArea.classList.add('success');
                // Aqui você pode redirecionar o usuário para a próxima página de cadastro
                // window.location.href = 'cadastro-completo.html?cpf=' + cpf; 
            } else {
                // Lida com erros da API
                messageArea.textContent = result.detail || 'Ocorreu um erro no cadastro.';
                messageArea.classList.add('error');
            }
        } catch (error) {
            // Lida com erros de conexão
            console.error('Erro de conexão:', error);
            messageArea.textContent = 'Erro ao conectar com o servidor. Verifique se o Uvicorn está rodando.';
            messageArea.classList.add('error');
        }

        messageArea.style.display = 'block';
    });
});