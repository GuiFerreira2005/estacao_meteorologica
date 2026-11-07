const URL_MAPA = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";

const LATITUDE = -23.515905;
const LONGITUDE = -46.689696;

let mapa, marcador;

function iniciarMapa(lat = LATITUDE, lng = LONGITUDE) {
  mapa = L.map("mapa").setView([lat, lng], 13);
  L.tileLayer(URL_MAPA, {
    maxZoom: 19,
  }).addTo(mapa);
  marcador = L.marker([lat, lng]).addTo(mapa);}


function moverMarcador(lat, lng) {
  marcador.setLatLng([lat, lng]);
  mapa.panTo([lat, lng]);
}

