#include <Servo.h>

// ==============================
// CONFIGURACIÓN
// ==============================

Servo rpmServo;
const int servoPin = 5;

// 6 Analógicos
const int analogPins[6] = {A0, A1, A2, A3, A4, A5};

// 11 Digitales (SIN el 5 porque es servo)
const int digitalPins[] = {2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13};
const int digitalCount = sizeof(digitalPins) / sizeof(digitalPins[0]);

unsigned long lastSend = 0;
const unsigned long interval = 10; // 100Hz

int currentAngle = 0;

// ==============================
// SETUP
// ==============================

void setup() {

  Serial.begin(115200);

  rpmServo.attach(servoPin);
  rpmServo.write(0);

  for (int i = 0; i < digitalCount; i++) {
    pinMode(digitalPins[i], INPUT_PULLUP);
  }
}

// ==============================
// LOOP
// ==============================

void loop() {

  // ==========================
  // RECIBIR ANGULO DEL SERVO
  // ==========================
  if (Serial.available() > 0) {

    int angle = Serial.parseInt();

    // limpiar buffer
    while (Serial.available()) {
      Serial.read();
    }

    angle = constrain(angle, 0, 180);

    if (angle != currentAngle) {
      rpmServo.write(angle);
      currentAngle = angle;
    }
  }

  // ==========================
  // ENVIAR DATOS A PYTHON
  // ==========================
  if (millis() - lastSend >= interval) {

    lastSend = millis();

    // 1️⃣ Analógicos
    for (int i = 0; i < 6; i++) {
      Serial.print(analogRead(analogPins[i]));
      Serial.print(",");
    }

    // 2️⃣ Digitales (invertidos por INPUT_PULLUP)
    for (int i = 0; i < digitalCount; i++) {
      Serial.print(!digitalRead(digitalPins[i]));

      if (i < digitalCount - 1) {
        Serial.print(",");
      }
    }

    Serial.println(); // total 17 valores
  }
}