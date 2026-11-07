// Agora existe UM gráfico só.
let grafico = null;

// Sensor que está escolhido no menu (começa no primeiro da lista)
let sensorAtual = SENSORES[0];

// Guarda todas as leituras recebidas (para poder trocar de sensor sem perder o histórico)
let leituras = [];

// ... (mantenha formatarHora, criarGrafico e desenharGrafico iguais) ...

function trocarSensor(id) {
  sensorAtual = SENSORES.find(s => s.id === id) || SENSORES[0];
  localStorage.setItem("sensorSelecionado", sensorAtual.id); // Grava a escolha no navegador
  desenharGrafico();
}

function formatarHora(ts) {
  return new Date(ts).toLocaleTimeString("pt-BR", { hour: '2-digit', minute: '2-digit' });
}

// Cria o gráfico vazio (chamado uma vez quando a página abre)
function criarGrafico(canvasId) {
  grafico = new Chart(document.getElementById(canvasId), {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "", data: [],
        borderColor: "#000", backgroundColor: "#0002",
        fill: true, tension: 0.3, pointRadius: 0
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false, animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { 
          ticks: { 
            maxTicksLimit: 15,
            maxRotation: 0
          } 
        },
        y: { title: { display: true, text: "" } }
      }
    }
  });
}

// Desenha no gráfico o sensor que está escolhido
function desenharGrafico() {
  const s = sensorAtual;
  const linha = grafico.data.datasets[0];

  grafico.data.labels = leituras.map(l => formatarHora(l.timestamp));
  linha.data = leituras.map(l => l[s.id] ?? null);

  linha.label = s.nome + " (" + s.un + ")";
  linha.borderColor = s.cor;
  linha.backgroundColor = s.cor + "22";
  grafico.options.scales.y.title.text = s.nome + " (" + s.un + ")";

  grafico.update();
}

// Chamada quando você muda a opção no menu
function trocarSensor(id) {
  sensorAtual = SENSORES.find(s => s.id === id) || SENSORES[0];
  desenharGrafico();
}

// Recebe o histórico inteiro (quando a página abre)
function carregarHistorico(dados) {
  leituras = dados.slice(-CONFIG.MAX_PONTOS);
  desenharGrafico();
}

// Recebe uma leitura nova (a cada ciclo)
function adicionarPonto(l) {
  leituras.push(l);
  if (leituras.length > CONFIG.MAX_PONTOS) leituras.shift();
  desenharGrafico();
}
