// ==============================
// CONFIGURACIÓN GENERAL
// ==============================

#include <Servo.h>

const int analogPins[6] = {A0, A1, A2, A3, A4, A5};

// Quitamos el 5 porque será PWM servo
const int digitalPins[] = {
  2,3,4,6,7,8,9,10,11,12,13
};

const int digitalCount = sizeof(digitalPins) / sizeof(digitalPins[0]);

const int servoPin = 5;
Servo servoPWM5;

unsigned long lastSend = 0;
const unsigned long interval = 10; // 100Hz

int pwmValue = 90; // valor inicial servo

// ==============================
// SETUP
// ==============================

void setup() {
  Serial.begin(115200);

  servoPWM5.attach(servoPin);
  servoPWM5.write(pwmValue);

  for (int i = 0; i < digitalCount; i++) {
    pinMode(digitalPins[i], INPUT_PULLUP);
  }
}

// ==============================
// LOOP PRINCIPAL
// ==============================

void loop() {

  // ==============================
  // 1️⃣ RECIBIR DATOS DESDE PYTHON
  // ==============================

  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    int newValue = input.toInt();

    if (newValue >= 0 && newValue <= 180) {
      pwmValue = newValue;
      servoPWM5.write(pwmValue);
    }
  }

  // ==============================
  // 2️⃣ ENVIAR DATOS AL PC
  // ==============================

  if (millis() - lastSend >= interval) {
    lastSend = millis();

    int analogValues[6];
    for (int i = 0; i < 6; i++) {
      analogValues[i] = analogRead(analogPins[i]);
    }

    int digitalValues[digitalCount];
    for (int i = 0; i < digitalCount; i++) {
      digitalValues[i] = !digitalRead(digitalPins[i]);
    }

    // Enviar todo
    for (int i = 0; i < 6; i++) {
      Serial.print(analogValues[i]);
      Serial.print(",");
    }

    for (int i = 0; i < digitalCount; i++) {
      Serial.print(digitalValues[i]);
      if (i < digitalCount - 1) {
        Serial.print(",");
      }
    }

    Serial.println();
  }
}