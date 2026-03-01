// ==============================
// CONFIGURACIÓN GENERAL
// ==============================

const int analogPins[6] = {A0, A1, A2, A3, A4, A5};

const int digitalPins[] = {
  2,3,4,5,6,7,8,9,10,11,12,13
};

const int digitalCount = sizeof(digitalPins) / sizeof(digitalPins[0]);

unsigned long lastSend = 0;
const unsigned long interval = 10; // 10ms = 100Hz

// ==============================
// SETUP
// ==============================

void setup() {
  Serial.begin(115200);

  // Configurar digitales como INPUT_PULLUP
  for (int i = 0; i < digitalCount; i++) {
    pinMode(digitalPins[i], INPUT_PULLUP);
  }
}

// ==============================
// LOOP PRINCIPAL
// ==============================

void loop() {

  if (millis() - lastSend >= interval) {
    lastSend = millis();

    // 1 Leer analógicos
    int analogValues[6];
    for (int i = 0; i < 6; i++) {
      analogValues[i] = analogRead(analogPins[i]);
    }

    // 2 Leer digitales
    int digitalValues[digitalCount];
    for (int i = 0; i < digitalCount; i++) {
      digitalValues[i] = !digitalRead(digitalPins[i]); 
      // invertido por INPUT_PULLUP
    }

    // 3 Enviar todo en una línea

    // Analógicos
    for (int i = 0; i < 6; i++) {
      Serial.print(analogValues[i]);
      Serial.print(",");
    }

    // Digitales
    for (int i = 0; i < digitalCount; i++) {
      Serial.print(digitalValues[i]);
      if (i < digitalCount - 1) {
        Serial.print(",");
      }
    }

    Serial.println();
  }
}