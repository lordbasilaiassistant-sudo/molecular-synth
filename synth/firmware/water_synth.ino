/*
 * Water Synth firmware — atmospheric water generation, buildable today.
 * --------------------------------------------------------------------
 * "A glass of drinkable water on demand": a Peltier cold plate condenses water out of
 * humid air (AWG), it drips through an activated-carbon filter, a UV-C LED sterilises
 * it, a Peltier serving-plate sets temperature, and a peristaltic pump dispenses it.
 * Reuses the molecular rig's Peltier/Arduino/PSU. Cheap, orderable parts (see ../README).
 *
 * HONEST SCOPE: harvests + treats water from air/reservoir. It does NOT make matter from
 * energy (E=mc^2 makes that a north-star, not a build). This delivers the *experience* —
 * water appears on demand — and it is genuinely humanity-useful (clean water from air).
 *
 * Serial @115200 (the request-compiler emits exactly these):
 *   HARVEST <ml>  run condenser+fan until ~<ml> condensed (time/level based)
 *   FILTER        passive carbon stage (ack only)
 *   UV <s>        run the UV-C LED for <s> seconds (sterilise)
 *   TEMP <c>      set serving-plate temperature
 *   DISPENSE <ml> run the pump to pour ~<ml>
 *   DONE          everything off, report READY
 */

#include <Arduino.h>

const int PIN_COND = 3;    // MOSFET: condenser Peltier (cooling) ON/OFF
const int PIN_FAN  = 5;    // MOSFET: fan over the cold plate
const int PIN_UV   = 6;    // MOSFET: UV-C LED  (NEVER expose skin/eyes to UV-C)
const int PIN_PUMP = 7;    // MOSFET: peristaltic dispense pump
const int PIN_TPWM = 9, PIN_THOT = 10, PIN_TCOLD = 11;  // H-bridge: serving-temp plate
const int PIN_THERM = A0;  // NTC on the serving plate
const int PIN_LEVEL = A1;  // optional collected-water level/float sensor

const float HARVEST_ML_PER_MIN = 25.0;   // small-Peltier condensation rate (calibrate!)
const float PUMP_ML_PER_S = 2.2;
const float SERIES_R = 100000.0, THERM_NOM = 100000.0, BETA = 3950.0, T0K = 298.15;
const float TOL = 2.0, T_MAX = 95.0;
float target_c = 22.0;

float readTempC() {
  long acc = 0; for (int i = 0; i < 8; i++) acc += analogRead(PIN_THERM);
  float adc = acc / 8.0; if (adc <= 0) adc = 0.5;
  float r = SERIES_R * (1023.0 / adc - 1.0);
  float invT = 1.0 / T0K + (1.0 / BETA) * log(r / THERM_NOM);
  return 1.0 / invT - 273.15;
}
void servePlate(int out) {
  if (out > 255) out = 255; if (out < -255) out = -255;
  if (out >= 0) { digitalWrite(PIN_THOT, HIGH); digitalWrite(PIN_TCOLD, LOW); analogWrite(PIN_TPWM, out); }
  else { digitalWrite(PIN_THOT, LOW); digitalWrite(PIN_TCOLD, HIGH); analogWrite(PIN_TPWM, -out); }
}
void serviceTemp() {
  float t = readTempC();
  if (t > T_MAX) { servePlate(0); return; }
  float e = target_c - t;
  servePlate(e > TOL ? 220 : (e < -TOL ? -220 : 0));
}

void harvest(int ml) {
  digitalWrite(PIN_COND, HIGH); digitalWrite(PIN_FAN, HIGH);
  unsigned long ms = (unsigned long)(ml / HARVEST_ML_PER_MIN * 60000.0);
  unsigned long t0 = millis();
  while (millis() - t0 < ms) {
    serviceTemp();
    // optional early stop when the level sensor says we have enough
    if (analogRead(PIN_LEVEL) > 900) break;
  }
  digitalWrite(PIN_COND, LOW);    // keep fan a moment to clear, then off
  delay(500); digitalWrite(PIN_FAN, LOW);
}
void uv(int sec) { digitalWrite(PIN_UV, HIGH); unsigned long t0 = millis();
  while (millis() - t0 < (unsigned long)sec * 1000UL) serviceTemp();
  digitalWrite(PIN_UV, LOW); }
void dispense(int ml) { digitalWrite(PIN_PUMP, HIGH);
  unsigned long ms = (unsigned long)(ml / PUMP_ML_PER_S * 1000.0); unsigned long t0 = millis();
  while (millis() - t0 < ms) serviceTemp();
  digitalWrite(PIN_PUMP, LOW); }

void setup() {
  Serial.begin(115200);
  int outs[] = {PIN_COND, PIN_FAN, PIN_UV, PIN_PUMP, PIN_TPWM, PIN_THOT, PIN_TCOLD};
  for (int p : outs) { pinMode(p, OUTPUT); digitalWrite(p, LOW); }
  Serial.println(F("watersynth ready"));
}

String buf;
void handle(String c) {
  c.trim();
  if (c.startsWith("HARVEST ")) { harvest(c.substring(8).toInt()); Serial.println(F("OK")); }
  else if (c == "FILTER") { Serial.println(F("OK")); }
  else if (c.startsWith("UV ")) { uv(c.substring(3).toInt()); Serial.println(F("OK")); }
  else if (c.startsWith("TEMP ")) { target_c = c.substring(5).toFloat(); Serial.println(F("OK")); }
  else if (c.startsWith("DISPENSE ")) { dispense(c.substring(9).toInt()); Serial.println(F("OK")); }
  else if (c == "DONE") {
    digitalWrite(PIN_COND, LOW); digitalWrite(PIN_FAN, LOW); digitalWrite(PIN_UV, LOW);
    digitalWrite(PIN_PUMP, LOW); servePlate(0); Serial.println(F("READY"));
  }
}
void loop() {
  serviceTemp();
  while (Serial.available()) { char ch = Serial.read(); if (ch == '\n') { handle(buf); buf = ""; } else buf += ch; }
}
