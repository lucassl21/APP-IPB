document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-cadastro');
    const messageArea = document.getElementById('message-area');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const cpf = document.getElementById('cpf').value;
        const senha = document.getElementById('senha').value;

        messageArea.style.display = 'none';
        messageArea.textContent = '';
        messageArea.className = 'message';

        try {
            // ALERTA: MUDAR ESTA URL DEPOIS DE PUBLICAR SUA API NO RENDER
            const response = await fetch('http://127.0.0.1:8000/users/register-first-stage', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, cpf, senha })
            });

            const result = await response.json();

            if (response.ok) {
                messageArea.textContent = 'Primeira etapa concluída! Prossiga para o cadastro completo.';
                messageArea.classList.add('success');
            } else {
                messageArea.textContent = result.detail || 'Ocorreu um erro no cadastro.';
                messageArea.classList.add('error');
            }
        } catch (error) {
            console.error('Erro de conexão:', error);
            messageArea.textContent = 'Erro ao conectar com o servidor. Verifique se o Uvicorn está rodando.';
            messageArea.classList.add('error');
        }

        messageArea.style.display = 'block';
    });
});