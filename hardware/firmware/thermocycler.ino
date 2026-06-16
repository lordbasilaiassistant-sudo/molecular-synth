/*
 * Molecular Synth v0 - DNA origami folding thermocycler firmware
 * ---------------------------------------------------------------
 * Repurposed parts (see /bom):
 *   - Peltier TEC1-12706 thermoelectric module (CPU/cooler/dehumidifier part)
 *   - BTS7960 / IBT-2 H-bridge motor driver  -> bidirectional Peltier drive (heat AND cool)
 *   - 100k NTC thermistor (3D-printer hot-end part) on the aluminium tube block
 *   - 12 V supply from a repurposed PC/laptop PSU
 *   - Arduino Uno/Nano
 *
 * Function: closed-loop PID tracks a setpoint; the host streams the anneal ramp
 * emitted by the compiler (design.json -> host_ramp.py), so the SAME ramp that the
 * wet-lab protocol prints is what the block executes. Heat 90 C, then slow-cool to
 * 20 C in Mg2+ buffer = standard scaffolded-origami folding (Rothemund 2006; Castro
 * et al., Nat. Methods 2011).
 *
 * Serial protocol @ 115200 (newline-terminated):
 *   SET <tempC>        set target temperature, hold indefinitely
 *   STEP <tempC> <sec> ramp/hold to tempC for <sec> seconds, then report DONE
 *   STATUS             print "T=<meas> SP=<set> OUT=<-255..255>"
 *   STOP               output 0, hold
 * Without a host, RUN_DEFAULT_RAMP=1 executes a built-in 90->20 C ramp on boot.
 */

#include <Arduino.h>

// ---- pins ----
const int PIN_THERM   = A0;   // NTC divider midpoint
const int PIN_PWM     = 9;    // H-bridge enable/PWM
const int PIN_DIR_HOT = 7;    // H-bridge direction A (heat)
const int PIN_DIR_COLD= 8;    // H-bridge direction B (cool)
const int PIN_FAN     = 5;    // heatsink fan (always on while running)

// ---- thermistor (Beta model) ----
const float SERIES_R   = 100000.0;  // divider resistor (ohms)
const float THERM_NOM  = 100000.0;  // thermistor nominal R at 25 C
const float THERM_BETA = 3950.0;
const float TEMP_NOM_K = 298.15;
const float ADC_MAX    = 1023.0;

// ---- PID ----
float Kp = 18.0, Ki = 0.35, Kd = 30.0;
float integ = 0, prevErr = 0;
float setpoint = 25.0;
unsigned long lastPid = 0;
const unsigned long PID_MS = 200;

// ---- safety ----
const float T_MAX = 99.0;     // hard cutoff; DNA/buffer must not boil over
const float T_MIN = 2.0;

// ---- default ramp (used if no host) ----
#define RUN_DEFAULT_RAMP 1
struct Step { float tempC; unsigned long sec; };
Step defaultRamp[] = {
  {90, 300}, {85, 514}, {80, 514}, {75, 514}, {70, 514}, {65, 514},
  {60, 514}, {55, 514}, {50, 514}, {45, 514}, {40, 514}, {35, 514},
  {30, 514}, {25, 514}, {20, 514}
};
const int defaultRampLen = sizeof(defaultRamp) / sizeof(defaultRamp[0]);

float readTempC() {
  // average a few samples
  long acc = 0;
  for (int i = 0; i < 8; i++) acc += analogRead(PIN_THERM);
  float adc = acc / 8.0;
  if (adc <= 0) adc = 0.5;
  float r = SERIES_R * (ADC_MAX / adc - 1.0);   // thermistor on top of divider
  float invT = 1.0 / TEMP_NOM_K + (1.0 / THERM_BETA) * log(r / THERM_NOM);
  return (1.0 / invT) - 273.15;
}

void drive(float out) {  // out in [-255, 255]; + = heat, - = cool
  if (out > 255) out = 255; if (out < -255) out = -255;
  if (out >= 0) {
    digitalWrite(PIN_DIR_HOT, HIGH); digitalWrite(PIN_DIR_COLD, LOW);
    analogWrite(PIN_PWM, (int)out);
  } else {
    digitalWrite(PIN_DIR_HOT, LOW); digitalWrite(PIN_DIR_COLD, HIGH);
    analogWrite(PIN_PWM, (int)(-out));
  }
}

float pidStep(float meas) {
  float err = setpoint - meas;
  integ += err * (PID_MS / 1000.0);
  integ = constrain(integ, -400, 400);
  float deriv = (err - prevErr) / (PID_MS / 1000.0);
  prevErr = err;
  return Kp * err + Ki * integ + Kd * deriv;
}

void serviceControl() {
  unsigned long now = millis();
  if (now - lastPid < PID_MS) return;
  lastPid = now;
  float t = readTempC();
  if (t > T_MAX || t < T_MIN) { drive(0); return; }   // fault -> coast
  drive(pidStep(t));
}

void rampTo(float tempC, unsigned long sec) {
  setpoint = constrain(tempC, T_MIN, T_MAX);
  unsigned long t0 = millis();
  while (millis() - t0 < sec * 1000UL) {
    serviceControl();
    if (Serial.available()) return;   // host can interrupt
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_PWM, OUTPUT); pinMode(PIN_DIR_HOT, OUTPUT);
  pinMode(PIN_DIR_COLD, OUTPUT); pinMode(PIN_FAN, OUTPUT);
  digitalWrite(PIN_FAN, HIGH);
  drive(0);
  Serial.println(F("molsynth-thermocycler ready"));
#if RUN_DEFAULT_RAMP
  if (!Serial.available()) {
    Serial.println(F("RUN default ramp 90->20C"));
    for (int i = 0; i < defaultRampLen; i++) {
      Serial.print(F("STEP ")); Serial.print(defaultRamp[i].tempC);
      Serial.print(F(" ")); Serial.println(defaultRamp[i].sec);
      rampTo(defaultRamp[i].tempC, defaultRamp[i].sec);
    }
    Serial.println(F("DONE default ramp"));
  }
#endif
}

String buf;
void loop() {
  serviceControl();
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      buf.trim();
      if (buf.startsWith("SET ")) {
        setpoint = buf.substring(4).toFloat();
        Serial.print(F("OK SET ")); Serial.println(setpoint);
      } else if (buf.startsWith("STEP ")) {
        int sp = buf.indexOf(' ', 5);
        float tc = buf.substring(5, sp).toFloat();
        unsigned long sec = (unsigned long) buf.substring(sp + 1).toInt();
        rampTo(tc, sec);
        Serial.println(F("DONE"));
      } else if (buf == "STATUS") {
        Serial.print(F("T=")); Serial.print(readTempC());
        Serial.print(F(" SP=")); Serial.println(setpoint);
      } else if (buf == "STOP") {
        drive(0); Serial.println(F("OK STOP"));
      }
      buf = "";
    } else {
      buf += c;
    }
  }
}
