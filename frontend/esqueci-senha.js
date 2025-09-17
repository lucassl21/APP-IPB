document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-esqueci-senha');
    const messageArea = document.getElementById('message-area');
    const apiBaseUrl = 'https://app-ipb.onrender.com';

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;

        messageArea.style.display = 'none';
        messageArea.textContent = '';
        messageArea.className = 'notification mt-4';

        try {
            const response = await fetch(`${apiBaseUrl}/users/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const result = await response.json();

            if (response.ok) {
                messageArea.textContent = result.message;
                messageArea.classList.add('is-success');
            } else {
                messageArea.textContent = result.detail || 'Ocorreu um erro. Por favor, tente novamente.';
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