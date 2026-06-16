/*
 * Drink Synth firmware — the buildable-today synthesizer instance.
 * ---------------------------------------------------------------
 * Cheap, orderable parts (see ../README.md): 5x peristaltic pumps driven by
 * logic-level MOSFETs, a Peltier (TEC1-12706) hot/cold cup plate via a BTS7960
 * H-bridge (reused from the molecular rig), a 100k NTC thermistor on the plate, an
 * optional servo ice-dropper, 12 V from a repurposed PSU, Arduino Uno/Nano.
 *
 * Serial protocol @115200 (the request-compiler emits exactly these):
 *   TEMP <c>        set cup target temperature (heat or chill)
 *   PUMP <id> <ms>  run pump <id> (0..4) for <ms> milliseconds
 *   ICE <g>         dispense ~<g> grams of ice via the servo dropper
 *   WAIT_TEMP       block until the plate is within tolerance of target
 *   DONE            pumps off, report READY
 * Each command replies OK/READY so the host can step through a ticket.
 *
 * SAFETY: food-grade silicone tubing only; keep electronics away from liquid; the
 * Peltier plate can reach ~70 C — insulate. This assembles a drink from stocked
 * ingredients; it does not synthesise matter.
 */

#include <Arduino.h>
#include <Servo.h>

const int PUMP_PINS[5] = {2, 3, 4, 6, 7};   // MOSFET gates, one per ingredient pump
const int PIN_THERM = A0;
const int PIN_PWM = 9, PIN_HOT = 10, PIN_COLD = 11;  // BTS7960 H-bridge to Peltier
const int PIN_SERVO = 5;                     // ice-dropper servo

// thermistor (Beta model, same as the molecular rig)
const float SERIES_R = 100000.0, THERM_NOM = 100000.0, BETA = 3950.0, T0K = 298.15;

Servo iceServo;
float target_c = 25.0;
const float TOL = 2.0;
const float T_MAX = 75.0;     // plate safety cap

float readTempC() {
  long acc = 0; for (int i = 0; i < 8; i++) acc += analogRead(PIN_THERM);
  float adc = acc / 8.0; if (adc <= 0) adc = 0.5;
  float r = SERIES_R * (1023.0 / adc - 1.0);
  float invT = 1.0 / T0K + (1.0 / BETA) * log(r / THERM_NOM);
  return 1.0 / invT - 273.15;
}

void plate(int out) {  // + = heat, - = cool, magnitude 0..255
  if (out > 255) out = 255; if (out < -255) out = -255;
  if (out >= 0) { digitalWrite(PIN_HOT, HIGH); digitalWrite(PIN_COLD, LOW); analogWrite(PIN_PWM, out); }
  else { digitalWrite(PIN_HOT, LOW); digitalWrite(PIN_COLD, HIGH); analogWrite(PIN_PWM, -out); }
}

void serviceTemp() {           // simple bang-bang toward target, with safety cap
  float t = readTempC();
  if (t > T_MAX) { plate(0); return; }
  float err = target_c - t;
  if (err > TOL) plate(220);       // heat
  else if (err < -TOL) plate(-220); // chill
  else plate(0);
}

void runPump(int id, long ms) {
  if (id < 0 || id > 4) return;
  digitalWrite(PUMP_PINS[id], HIGH);
  unsigned long t0 = millis();
  while (millis() - t0 < (unsigned long)ms) serviceTemp();   // keep plate on temp
  digitalWrite(PUMP_PINS[id], LOW);
}

void dropIce(int grams) {
  // sweep the servo a few times; ~one sweep per ~10 g (calibrate to your hopper)
  int sweeps = max(1, grams / 10);
  for (int i = 0; i < sweeps; i++) { iceServo.write(90); delay(400); iceServo.write(0); delay(400); }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 5; i++) { pinMode(PUMP_PINS[i], OUTPUT); digitalWrite(PUMP_PINS[i], LOW); }
  pinMode(PIN_PWM, OUTPUT); pinMode(PIN_HOT, OUTPUT); pinMode(PIN_COLD, OUTPUT);
  iceServo.attach(PIN_SERVO); iceServo.write(0);
  plate(0);
  Serial.println(F("drinksynth ready"));
}

String buf;
void handle(String cmd) {
  cmd.trim();
  if (cmd.startsWith("TEMP ")) { target_c = cmd.substring(5).toFloat(); Serial.println(F("OK")); }
  else if (cmd.startsWith("PUMP ")) {
    int sp = cmd.indexOf(' ', 5);
    int id = cmd.substring(5, sp).toInt();
    long ms = cmd.substring(sp + 1).toInt();
    runPump(id, ms); Serial.println(F("OK"));
  }
  else if (cmd.startsWith("ICE ")) { dropIce(cmd.substring(4).toInt()); Serial.println(F("OK")); }
  else if (cmd == "WAIT_TEMP") {
    unsigned long t0 = millis();
    while (fabs(readTempC() - target_c) > TOL && millis() - t0 < 120000UL) serviceTemp();
    Serial.println(F("OK"));
  }
  else if (cmd == "DONE") { for (int i = 0; i < 5; i++) digitalWrite(PUMP_PINS[i], LOW); plate(0); Serial.println(F("READY")); }
}

void loop() {
  serviceTemp();
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') { handle(buf); buf = ""; }
    else buf += c;
  }
}
