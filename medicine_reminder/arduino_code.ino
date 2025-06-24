#include <Arduino.h>

const int irPins[] = {2, 3, 4};
const int ledPins[] = {5, 6, 7};
const int buzzerPin = 8;

unsigned long startMillis;
int reminderHours[3], reminderMinutes[3];
bool activeReminder[3] = {false, false, false};
bool taken[3] = {false, false, false};

void setup() {
  Serial.begin(9600);
  while (!Serial);

  for (int i = 0; i < 3; i++) {
    pinMode(irPins[i], INPUT);
    pinMode(ledPins[i], OUTPUT);
  }
  pinMode(buzzerPin, OUTPUT);

  Serial.println("Enter current time (HH MM):");
  while (Serial.available() == 0);
  int currHour = Serial.parseInt();
  int currMin = Serial.parseInt();
  startMillis = millis() - ((currHour * 60UL + currMin) * 60000UL);

  for (int i = 0; i < 3; i++) {
    Serial.print("Enter reminder ");
    Serial.print(i + 1);
    Serial.println(" time (HH MM):");
    while (Serial.available() == 0);
    delay(200); // Small delay to allow full input
    reminderHours[i] = Serial.parseInt();
    reminderMinutes[i] = Serial.parseInt();
    Serial.print("Reminder ");
    Serial.print(i + 1);
    Serial.print(" set at ");
    Serial.print(reminderHours[i]);
    Serial.print(":");
    Serial.println(reminderMinutes[i]);
  }

  Serial.println("System initialized ✅");
}

void loop() {
  unsigned long elapsedMillis = millis() - startMillis;
  int currMin = (elapsedMillis / 60000UL) % 60;
  int currHour = (elapsedMillis / 3600000UL) % 24;
  int currTotal = currHour * 60 + currMin;

  for (int i = 0; i < 3; i++) {
    int remTotal = reminderHours[i] * 60 + reminderMinutes[i];

    // Activate reminder window
    if (!taken[i] && currTotal >= remTotal - 5 && currTotal <= remTotal + 5) {
      if (!activeReminder[i]) {
        activeReminder[i] = true;
        Serial.print("🔔 Reminder ");
        Serial.print(i + 1);
        Serial.println(" ACTIVE!");
      }
    }

    if (activeReminder[i]) {
      digitalWrite(ledPins[i], HIGH);
      tone(buzzerPin, 1000);

      // Only check for IR sensor when it's time
      if (digitalRead(irPins[i]) == HIGH) {
        activeReminder[i] = false;
        taken[i] = true;
        digitalWrite(ledPins[i], LOW);
        noTone(buzzerPin);
        Serial.print("✅ Pill taken for Reminder ");
        Serial.println(i + 1);
      }

      // Auto stop after 10 minutes past reminder
      if (currTotal > remTotal + 5) {
        activeReminder[i] = false;
        digitalWrite(ledPins[i], LOW);
        noTone(buzzerPin);
        Serial.print("⌛ Time expired for Reminder ");
        Serial.println(i + 1);
      }
    }
  }

  delay(1000);
}