/*
 * ESP32 Load Monitoring Example
 * 
 * This code monitors a DC motor and vibration sensor, using RGB LED and buzzer for alerts.
 * Hardware components:
 * - ESP32 microcontroller
 * - DC motor
 * - Vibration sensor
 * - RGB LED for status indication
 * - Buzzer for alerts
 */

 #include <WiFi.h>
 #include <HTTPClient.h>
 #include <ArduinoJson.h>
 
 // WiFi credentials
 const char* ssid = "YourWiFiSSID";
 const char* password = "YourWiFiPassword";
 
 // API endpoint
 const char* apiEndpoint = "http://your-server-address:8000/api/readings";
 
 // Pin definitions
 #define MOTOR_VOLTAGE_PIN 34    // Analog pin for motor voltage
 #define MOTOR_CURRENT_PIN 35    // Analog pin for motor current
 #define VIB_VOLTAGE_PIN 32      // Analog pin for vibration sensor voltage
 #define VIB_CURRENT_PIN 33      // Analog pin for vibration sensor current
 #define RED_LED_PIN 25          // RGB LED pins
 #define GREEN_LED_PIN 26
 #define BLUE_LED_PIN 27
 #define BUZZER_PIN 13           // Buzzer pin
 
 // Threshold for alerts
 #define LOAD_THRESHOLD 3.0      // Threshold in Amperes for combined current
 
 // Device ID
 const char* deviceId = "ESP32_001";
 
 // Function declarations
 float readMotorCurrent();
 float readMotorVoltage();
 float readVibCurrent();
 float readVibVoltage();
 void setRGBLed(float totalCurrent);
 void sendDataToAPI(float motorCurrent, float motorVoltage, float vibCurrent, float vibVoltage);
 
 void setup() {
   // Initialize Serial communication
   Serial.begin(115200);
   
   // Initialize pins
   pinMode(RED_LED_PIN, OUTPUT);
   pinMode(GREEN_LED_PIN, OUTPUT);
   pinMode(BLUE_LED_PIN, OUTPUT);
   pinMode(BUZZER_PIN, OUTPUT);
   
   // Connect to WiFi
   WiFi.begin(ssid, password);
   Serial.print("Connecting to WiFi");
   
   while (WiFi.status() != WL_CONNECTED) {
     delay(500);
     Serial.print(".");
   }
   
   Serial.println();
   Serial.print("Connected to WiFi, IP address: ");
   Serial.println(WiFi.localIP());
   
   delay(2000);
 }
 
 void loop() {
   // Read sensor values
   float motorCurrent = readMotorCurrent();
   float motorVoltage = readMotorVoltage();
   float vibCurrent = readVibCurrent();
   float vibVoltage = readVibVoltage();
   float totalCurrent = motorCurrent + vibCurrent;
   
   // Set RGB LED and control buzzer based on total current
   setRGBLed(totalCurrent);
   
   // If threshold exceeded, activate buzzer
   if (totalCurrent > LOAD_THRESHOLD) {
     digitalWrite(BUZZER_PIN, HIGH);
     delay(100);
     digitalWrite(BUZZER_PIN, LOW);
   }
   
   // Send data to API
   sendDataToAPI(motorCurrent, motorVoltage, vibCurrent, vibVoltage);
   
   // Wait before next reading
   delay(5000);  // Send data every 5 seconds
 }
 
 float readMotorCurrent() {
   int sensorValue = analogRead(MOTOR_CURRENT_PIN);
   float current = sensorValue * (5.0 / 4095.0) * 0.5;  // Example conversion, adjust based on your sensor
   return abs(current);
 }
 
 float readMotorVoltage() {
   int sensorValue = analogRead(MOTOR_VOLTAGE_PIN);
   float voltage = sensorValue * (5.0 / 4095.0) * 5.0;  // Example conversion, adjust based on your setup
   return voltage;
 }
 
 float readVibCurrent() {
   int sensorValue = analogRead(VIB_CURRENT_PIN);
   float current = sensorValue * (5.0 / 4095.0) * 0.5;  // Example conversion, adjust based on your sensor
   return abs(current);
 }
 
 float readVibVoltage() {
   int sensorValue = analogRead(VIB_VOLTAGE_PIN);
   float voltage = sensorValue * (5.0 / 4095.0) * 5.0;  // Example conversion, adjust based on your setup
   return voltage;
 }
 
 void setRGBLed(float totalCurrent) {
   if (totalCurrent > LOAD_THRESHOLD) {
     // Red - threshold exceeded
     digitalWrite(RED_LED_PIN, HIGH);
     digitalWrite(GREEN_LED_PIN, LOW);
     digitalWrite(BLUE_LED_PIN, LOW);
   } else {
     // Green - normal
     digitalWrite(RED_LED_PIN, LOW);
     digitalWrite(GREEN_LED_PIN, HIGH);
     digitalWrite(BLUE_LED_PIN, LOW);
   }
 }
 
 void sendDataToAPI(float motorCurrent, float motorVoltage, float vibCurrent, float vibVoltage) {
   if (WiFi.status() != WL_CONNECTED) {
     Serial.println("WiFi not connected");
     return;
   }
   
   HTTPClient http;
   
   // Prepare JSON data
   DynamicJsonDocument doc(200);
   doc["motor_current"] = motorCurrent;
   doc["motor_voltage"] = motorVoltage;
   doc["vib_current"] = vibCurrent;
   doc["vib_voltage"] = vibVoltage;
   doc["total_power"] = (motorCurrent * motorVoltage) + (vibCurrent * vibVoltage);
   doc["device_id"] = deviceId;
   
   String jsonData;
   serializeJson(doc, jsonData);
   
   // Configure request
   http.begin(apiEndpoint);
   http.addHeader("Content-Type", "application/json");
   
   // Send POST request
   int httpResponseCode = http.POST(jsonData);
   
   if (httpResponseCode > 0) {
     String response = http.getString();
     Serial.println("HTTP Response code: " + String(httpResponseCode));
     Serial.println("Response: " + response);
   } else {
     Serial.println("Error on sending POST: " + String(httpResponseCode));
   }
   
   http.end();
 }