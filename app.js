// Refleja el puerto activo del ESP32 (GET /api/status cada 500 ms).
// Sin señal, simula la misma secuencia local (rojo 20 / verde 15 / amarillo 5).
const DURACIONES = { rojo: 20, verde: 15, amarillo: 5 };
const PINES = { rojo: 2, verde: 5, amarillo: 4 };
const ORDEN = ["rojo", "verde", "amarillo"];

const el = (id) => document.getElementById(id);
const luces = { rojo: el("luz-rojo"), verde: el("luz-verde"), amarillo: el("luz-amarillo") };

let simLuz = "rojo";
let simQueda = DURACIONES.rojo;
let simTick = 0;

function pintar(luz, restante, duracion) {
  Object.entries(luces).forEach(([k, n]) => n.classList.toggle("on", k === luz));
  el("texto-estado").textContent = luz.toUpperCase();
  el("numero").textContent = Math.ceil(restante);
  el("detalle").textContent = `Pin ${PINES[luz]} · ${duracion}s totales`;
}

function setConexion(conectado) {
  el("punto").className = "punto " + (conectado ? "live" : "sim");
  el("nota-fuente").textContent = conectado ? "ESP32 CONECTADO" : "SIMULADO";
}

async function poll() {
  try {
    const r = await fetch("/api/status");
    const d = await r.json();
    if (d.conectado) {
      setConexion(true);
      pintar(d.luz, d.restante, d.duracion);
      simLuz = d.luz; simQueda = d.restante;
      return;
    }
  } catch (e) { /* sin servidor: simulación */ }
  setConexion(false);
  pintar(simLuz, simQueda, DURACIONES[simLuz]);
  simTick += 0.5;
  if (simTick >= 1) {
    simTick = 0;
    simQueda -= 1;
    if (simQueda <= 0) {
      simLuz = ORDEN[(ORDEN.indexOf(simLuz) + 1) % ORDEN.length];
      simQueda = DURACIONES[simLuz];
    }
  }
}

setInterval(poll, 500);
poll();
