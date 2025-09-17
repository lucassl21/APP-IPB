document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-redefinir-senha');
    const messageArea = document.getElementById('message-area');
    const apiBaseUrl = 'https://app-ipb.onrender.com';

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const token = document.getElementById('token').value;
        const novaSenha = document.getElementById('nova-senha').value;

        messageArea.style.display = 'none';
        messageArea.textContent = '';
        messageArea.className = 'notification mt-4';

        try {
            const response = await fetch(`${apiBaseUrl}/users/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, nova_senha: novaSenha })
            });

            const result = await response.json();

            if (response.ok) {
                messageArea.textContent = 'Senha redefinida com sucesso! Redirecionando para o login...';
                messageArea.classList.add('is-success');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else {
                messageArea.textContent = result.detail || 'Ocorreu um erro ao redefinir a senha. Verifique o código.';
                messageArea.classList.add('is-danger');
            }
        } catch (error) {
            console.error('Erro de conexão:', error);
            messageArea.textContent = 'Erro ao conectar com o servidor. Verifique sua conexão.';
            messageArea.classList.add('is-danger');
        }

        messageArea.style.display = 'block';
    });
});