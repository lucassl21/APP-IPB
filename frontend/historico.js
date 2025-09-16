document.addEventListener('DOMContentLoaded', async () => {
    // ALERTA: MUDAR ESTA URL DEPOIS DE PUBLICAR SUA API NO RENDER
    const apiBaseUrl = 'http://127.0.0.1:8000';
    const cpfUsuario = '12345678900'; // Substitua pelo CPF do usuário logado

    try {
        const response = await fetch(`${apiBaseUrl}/users/historico/${cpfUsuario}`);
        const historico = await response.json();

        const tabela = document.getElementById('historico-tabela');
        if (historico.length === 0) {
            tabela.innerHTML = '<tr><td colspan="4" class="has-text-centered">Nenhuma solicitação encontrada.</td></tr>';
            return;
        }

        historico.forEach(solicitacao => {
            const row = document.createElement('tr');
            const tipo = document.createElement('td');
            const descricao = document.createElement('td');
            const data = document.createElement('td');
            const status = document.createElement('td');
            
            // Formatação da data
            const dataFormatada = new Date(solicitacao.data_solicitacao).toLocaleDateString('pt-BR', {
                day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            // Cria o círculo de status com a cor correta
            const statusSpan = document.createElement('span');
            statusSpan.className = `status-circle status-${solicitacao.status}`;

            tipo.textContent = solicitacao.tipo_solicitacao;
            descricao.textContent = solicitacao.descricao;
            data.textContent = dataFormatada;
            status.appendChild(statusSpan);
            status.appendChild(document.createTextNode(solicitacao.status));

            row.appendChild(tipo);
            row.appendChild(descricao);
            row.appendChild(data);
            row.appendChild(status);
            tabela.appendChild(row);
        });

    } catch (error) {
        console.error('Erro ao buscar histórico:', error);
        const tabela = document.getElementById('historico-tabela');
        tabela.innerHTML = '<tr><td colspan="4" class="has-text-centered">Erro ao carregar o histórico.</td></tr>';
    }
});