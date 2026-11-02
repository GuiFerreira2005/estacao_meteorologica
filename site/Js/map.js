const URL_MAPA = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}";

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

