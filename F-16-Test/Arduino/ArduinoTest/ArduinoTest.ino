// ==============================
// Arduino: Leer A0-A5 y enviar por Serial
// ==============================

void setup() {
  Serial.begin(115200); // Igual que el Python
  while (!Serial) ;     // Espera a que Serial esté listo (solo necesario en algunos modelos)
}

void loop() {
  int a0 = analogRead(A0); // Joystick X
  int a1 = analogRead(A1); // Joystick Y
  int a2 = analogRead(A2); // Throttle
  int a3 = analogRead(A3); // Timón / Rudder
  int a4 = analogRead(A4); // Otro eje
  int a5 = analogRead(A5); // Otro eje

  // Enviar valores separados por coma
  Serial.print(a0);
  Serial.print(",");
  Serial.print(a1);
  Serial.print(",");
  Serial.print(a2);
  Serial.print(",");
  Serial.print(a3);
  Serial.print(",");
  Serial.print(a4);
  Serial.print(",");
  Serial.println(a5); // println para enviar salto de línea al final

  delay(20); // 50 Hz, ajustable según necesidad
}