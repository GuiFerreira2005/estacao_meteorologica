function dentro(v, faixa) {
  if (!faixa) return true;
  const [min, max] = faixa;
  return (min == null || v >= min) && (max == null || v <= max);
}

function descrever(s, v, faixa) {
  const [min, max] = faixa;
  return v < min ? "abaixo de " + min + " " + s.un : "acima de " + max + " " + s.un;
}

function avaliar(s, v) {
  if (v == null) return { nivel: "atencao", texto: "sem leitura do sensor" };
  if (!s.ideal && !s.limite) return { nivel: "", texto: "" };
  if (!dentro(v, s.limite)) return { nivel: "critico", texto: descrever(s, v, s.limite) };
  if (!dentro(v, s.ideal)) return { nivel: "atencao", texto: descrever(s, v, s.ideal) };
  return { nivel: "ok", texto: "" };
}
