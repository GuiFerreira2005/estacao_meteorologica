const CONFIG = {
  URL_BASE: "",
  INTERVALO_MS: 16000,
  MAX_PONTOS: 100
};
// ideal  [min, max]: dentro dela o valor está normal
// limite [min, max]: fora do ideal mas dentro do limite = Atenção; fora = Crítico
// null = sem limite naquele lado; sem faixa = sem alerta
const SENSORES = [
  { id: "temp_dht", sensor: "DHT22", nome: "Temperatura", un: "°C", casas: 1, cor: "#e4572e",
    ideal: [20, 28], limite: [10, 35] }, // Valores de exemplo adicionados
  { id: "umidade", sensor: "DHT22", nome: "Umidade", un: "%", casas: 1, cor: "#2e86e4",
    ideal: [40, 60], limite: [30, 80] }, // Valores de exemplo adicionados
  { id: "pressao", sensor: "BMP280", nome: "Pressão", un: "hPa", casas: 1, cor: "#7b4fd1",
    ideal: null, limite: null },
  { id: "gas", sensor: "MQ-135", nome: "Qualidade do ar", un: "ppm", casas: 0, cor: "#2f9e44",
    ideal: [null, 700], limite: [null, 1000] },
  { id: "luz", sensor: "LDR", nome: "Luminosidade", un: "%", casas: 0, cor: "#b8a000",
    ideal: null, limite: null }
];

async function getAtual() {
  if (CONFIG.USAR_MOCK) return _novaLeitura();
  const r = await fetch(CONFIG.URL_BASE + "/api/atual");
  if (!r.ok) throw new Error("Erro " + r.status);
  const data = await r.json();
  
  // Inverte e converte o LDR para % apenas no Frontend
  if (data.luz != null) {
    data.luz = Number((((4095 - data.luz) / 4095) * 100).toFixed(0));
  }
  return data;
}

async function getHistorico() {
  if (CONFIG.USAR_MOCK) {
    const agora = Date.now();
    return Array.from({ length: 60 }, (_, i) => _novaLeitura(new Date(agora - (60 - i) * 60000)));
  }
  const r = await fetch(CONFIG.URL_BASE + "/api/historico");
  if (!r.ok) throw new Error("Erro " + r.status);
  const data = await r.json();
  
  // Aplica a mesma regra para todo o histórico do gráfico
  data.forEach(d => {
    if (d.luz != null) {
      d.luz = Number((((4095 - d.luz) / 4095) * 100).toFixed(0));
    }
  });
  return data;
}


