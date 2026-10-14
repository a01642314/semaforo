# Semaforo ESP32

Página web que muestra en vivo el status de un ESP32 conectado en secuencia de semáforo, con cuenta regresiva para el cambio de luz. Diseño basado en el frame de Figma (caja `STATUS` + semáforo vertical).

## Archivos

| Archivo | Descripción |
|---|---|
| `index.html` / `styles.css` / `app.js` | Página web (réplica del diseño Figma) |
| `server.py` | Servidor simple (solo librería estándar, sin `pip`) |
| `semaforo_esp32/semaforo_esp32.ino` | Código Arduino para la ESP32 |

## Pines y tiempos

| Luz | Pin | Duración |
|---|---|---|
| Rojo | GPIO 2 | 20 s |
| Verde | GPIO 5 | 15 s |
| Amarillo | GPIO 4 | 5 s |

Secuencia: rojo → verde → amarillo → rojo…

## Uso

1. Corre el servidor:
   ```bash
   python3 server.py   # http://localhost:8000
   ```
2. En `semaforo_esp32.ino` configura `WIFI_SSID`, `WIFI_PASS` y `SERVER_URL` (IP de tu PC, ej. `http://192.168.1.50:8000/api/update`).
3. En Arduino IDE instala el core ESP32, selecciona `ESP32 Dev Module` y el puerto, luego sube el sketch.
4. Abre `http://localhost:8000`: la página hace `GET /api/status` cada 500 ms y refleja la luz activa + cuenta regresiva. Sin señal del ESP32, simula la secuencia local.

## API

- `GET /api/status` → `{ luz, restante, duracion, pines, duraciones, conectado }`
- `POST /api/update` ← ESP32, body `{ "luz": "rojo|amarillo|verde", "restante": 19, "duracion": 20 }`
