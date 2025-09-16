document.addEventListener('DOMContentLoaded', async () => {
    // URL da API atualizada
    const apiBaseUrl = 'https://igrejapresbiterianadeigarape.onrender.com';

    async function fetchData(endpoint) {
        try {
            const response = await fetch(`${apiBaseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error(`Erro ao buscar dados do endpoint: ${endpoint}`);
            }
            return await response.json();
        } catch (error) {
            console.error(error);
            return [];
        }
    }

    async function loadDashboard() {
        const solicitacoes = await fetchData('/admin/solicitacoes');
        const usuarios = await fetchData('/users/');

        const statusData = solicitacoes.reduce((acc, current) => {
            acc[current.status] = (acc[current.status] || 0) + 1;
            return acc;
        }, {});
        const statusLabels = Object.keys(statusData);
        const statusValues = Object.values(statusData);
        const statusColors = statusLabels.map(label => {
            if (label === 'concluido') return '#2ecc71';
            if (label === 'andamento') return '#F1C40F';
            if (label === 'pendente') return '#95A5A6';
            return '#34495e';
        });

        const userTypeData = usuarios.reduce((acc, current) => {
            acc[current.tipo_usuario] = (acc[current.tipo_usuario] || 0) + 1;
            return acc;
        }, {});
        const userTypeLabels = Object.keys(userTypeData);
        const userTypeValues = Object.values(userTypeData);
        const userTypeColors = userTypeLabels.map(label => {
            if (label === 'doador') return '#3498db';
            if (label === 'beneficiario') return '#e74c3c';
            if (label === 'oracao') return '#9b59b6';
            return '#bdc3c7';
        });

        const solicitacoesCtx = document.getElementById('solicitacoesChart').getContext('2d');
        new Chart(solicitacoesCtx, {
            type: 'pie',
            data: {
                labels: statusLabels,
                datasets: [{
                    label: '# de Solicitações',
                    data: statusValues,
                    backgroundColor: statusColors,
                    hoverOffset: 4
                }]
            }
        });

        const usuariosCtx = document.getElementById('usuariosChart').getContext('2d');
        new Chart(usuariosCtx, {
            type: 'bar',
            data: {
                labels: userTypeLabels,
                datasets: [{
                    label: '# de Usuários',
                    data: userTypeValues,
                    backgroundColor: userTypeColors
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    loadDashboard();
});