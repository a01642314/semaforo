/*
  Semaforo ESP32 — secuencia rojo (20s) -> verde (15s) -> amarillo (5s)
  Rojo     -> GPIO 2 (pedido)
  Amarillo -> GPIO 4 (libre elección)
  Verde    -> GPIO 5 (libre elección)

  En cada cambio de luz y cada segundo manda la señal al servidor:
    POST http://<IP_DE_TU_PC>:8000/api/update
    Body: {"luz":"rojo","restante":19,"duracion":20}

  La página web hace GET /api/status cada 500 ms y muestra
  la luz activa + cuenta regresiva.

  Librerías: WiFi + HTTPClient (incluidas en el core de ESP32).
*/

#include <WiFi.h>
#include <HTTPClient.h>

// ---- CONFIGURA ESTO ----
const char* WIFI_SSID = "TU_WIFI";
const char* WIFI_PASS = "TU_PASSWORD";
const char* SERVER_URL = "http://192.168.1.50:8000/api/update"; // IP de tu PC

// ---- Pines y duraciones (segundos) ----
const int PIN_ROJO = 2;        // pedido
const int PIN_AMARILLO = 4;
const int PIN_VERDE = 5;

const int T_ROJO = 20;         // pedido
const int T_AMARILLO = 5;      // pedido
const int T_VERDE = 15;        // pedido

void encenderSolo(int pin) {
  digitalWrite(PIN_ROJO, LOW);
  digitalWrite(PIN_AMARILLO, LOW);
  digitalWrite(PIN_VERDE, LOW);
  digitalWrite(pin, HIGH);
}

void avisarServidor(const char* luz, int restante, int duracion) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  String body = String("{\"luz\":\"") + luz +
                String("\",\"restante\":") + restante +
                String(",\"duracion\":") + duracion + String("}");
  int code = http.POST(body);
  Serial.printf(" -> POST %s restante=%d code=%d\n", luz, restante, code);
  http.end();
}

// Corre una fase: prende el pin, avisa cada segundo para la cuenta regresiva
void fase(const char* nombre, int pin, int segundos) {
  Serial.printf("[%s] ON pin %d durante %ds\n", nombre, pin, segundos);
  encenderSolo(pin);
  for (int queda = segundos; queda > 0; queda--) {
    avisarServidor(nombre, queda, segundos);
    delay(1000);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_ROJO, OUTPUT);
  pinMode(PIN_AMARILLO, OUTPUT);
  pinMode(PIN_VERDE, OUTPUT);

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWiFi OK, IP: " + WiFi.localIP().toString());
}

void loop() {
  fase("rojo", PIN_ROJO, T_ROJO);          // 20 s
  fase("verde", PIN_VERDE, T_VERDE);       // 15 s
  fase("amarillo", PIN_AMARILLO, T_AMARILLO); // 5 s
}
