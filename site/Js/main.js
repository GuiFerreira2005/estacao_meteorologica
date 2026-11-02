const el = id => document.getElementById(id);

function montarTela() {
  // Cards (iguais ao que você já tinha)
  el("cards").innerHTML = SENSORES.map(s =>
    `<div class="card" id="c-${s.id}"><small>${s.sensor}</small><span>${s.nome}</span>` +
    `<strong id="v-${s.id}">--</strong><em id="s-${s.id}" class="estado"></em></div>`).join("");

  // Menu: uma opção para cada sensor da lista SENSORES (api.js)
  el("seletor").innerHTML = SENSORES.map(s =>
    `<option value="${s.id}">${s.nome} (${s.sensor})</option>`).join("");

  // Quando a pessoa escolhe outra opção, o gráfico troca de sensor
  el("seletor").addEventListener("change", e => trocarSensor(e.target.value));

  // Um único gráfico
  criarGrafico("grafico");
}
const ROTULO = { critico: "Crítico", atencao: "Atenção", ok: "Normal" };

function atualizarCards(l) {
  const avisos = [];
  SENSORES.forEach(s => {
    const v = l[s.id];
    const valor = v == null ? "--" : Number(v).toFixed(s.casas) + " " + s.un;
    const a = avaliar(s, v);
    el("v-" + s.id).textContent = valor;
    el("c-" + s.id).className = "card " + a.nivel;
    el("s-" + s.id).textContent = !a.nivel ? "" : a.nivel === "ok" ? "Normal" : ROTULO[a.nivel] + ": " + a.texto;
    if (a.nivel === "atencao" || a.nivel === "critico") {
      const msg = v == null ? `${s.nome} (${s.sensor}): ${a.texto}` : `${s.nome} (${s.sensor}): ${valor}, ${a.texto}`;
      avisos.push({ nivel: a.nivel, msg });
    }
  });
  avisos.sort((x, y) => (x.nivel === "critico" ? 0 : 1) - (y.nivel === "critico" ? 0 : 1));
  const box = el("avisos");
  box.hidden = avisos.length === 0;
  box.innerHTML = avisos.map(a => `<div class="aviso ${a.nivel}"><b>${ROTULO[a.nivel]}:</b> ${a.msg}</div>`).join("");
}
function definirStatus(ok, ts) {
  const s = el("status");
  s.textContent = ok ? "ao vivo, última leitura " + formatarHora(ts) : "sem conexão com a API";
  s.className = "status " + (ok ? "ok" : "erro");
}

async function ciclo() {
  try {
    const l = await getAtual();
    atualizarCards(l);
    adicionarPonto(l);
    definirStatus(true, l.timestamp);
  } catch (erro) {
    console.error(erro);
    definirStatus(false);
  }
}
async function iniciar() {
  montarTela();
  iniciarMapa();

  try { carregarHistorico(await getHistorico()); }
  catch (erro) { console.error(erro); definirStatus(false); }

  await ciclo();
  setInterval(ciclo, CONFIG.INTERVALO_MS);
}

document.addEventListener("DOMContentLoaded", iniciar);
