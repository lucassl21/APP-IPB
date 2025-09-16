document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-login');
    const messageArea = document.getElementById('message-area');
    const apiBaseUrl = 'https://app-ipb.onrender.com';

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const senha = document.getElementById('senha').value;

        messageArea.style.display = 'none';
        messageArea.textContent = '';
        messageArea.className = 'notification mt-4';

        try {
            const response = await fetch(`${apiBaseUrl}/users/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, senha })
            });

            const result = await response.json();

            if (response.ok) {
                // Se o login foi bem-sucedido, salva o CPF no localStorage
                // e redireciona para a página de histórico
                localStorage.setItem('cpf_usuario', result.cpf_usuario);
                messageArea.textContent = 'Login bem-sucedido!';
                messageArea.classList.add('is-success');
                setTimeout(() => {
                    window.location.href = 'historico.html';
                }, 1500);

            } else {
                messageArea.textContent = result.detail || 'Ocorreu um erro no login.';
                messageArea.classList.add('is-danger');
            }
        } catch (error) {
            console.error('Erro de conexão:', error);
            messageArea.textContent = 'Erro ao conectar com o servidor. Verifique se o backend está online.';
            messageArea.classList.add('is-danger');
        }

        messageArea.style.display = 'block';
    });
});