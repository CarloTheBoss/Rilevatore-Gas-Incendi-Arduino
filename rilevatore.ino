#include <Time.h>
#include <math.h>
#include "DHT.h"
#include <LiquidCrystal.h>

// Seconds to wait between relevations:
#define INTERVAL_TIME 10

// Gas calibration parameters
#define CALIBRATION_INTERVAL 0.5
#define CALIBRATION_READS 50

// Gas standard usage parameters
#define GAS_READ_INTERVAL 0.05
#define GAS_READS 100

// LCD display:
// Order of pins: RS, E, D4, D5, D6, D7
LiquidCrystal lcd(10, 11, 9, 6, 5, 16);

// Gas to print concentration on lcd
#define GAS_TO_CHECK "CO"

// Check flame value
#define CHECK_FLAME 100

// Alarm stuff
#define ALARM_ON 0
#define ALARM_RED_FREQ 3100
#define ALARM_YELLOW_FREQ 570

// "Health" values:
#define TEMP_GREEN_MAX 25
#define TEMP_YELLOW_MAX 35

int gas_green_max[] = {16, -1, 5000, -1, -1, 1000, 1000}; // -1 = not set
int gas_yellow_max[] = {40, -1, 10000, -1, -1, 1800, 1800};

// Pins:

const int gas_pin = A3;
const int temperature_pin = A0;
const int flame_pin = A1;
const int piezo_pin = 3;
const int green_pin = 7;
const int yellow_pin = 4;
const int red_pin = 2;
const int blue_pin = 8;
const int button_pin = 12;

// Temperature sensor stuff:

#define DHTTYPE DHT11

DHT temperature_sensor(temperature_pin, DHTTYPE);

// Gas sensor stuff:

#define RL_VALUE  (5.0) // load resistance on the board, kilo ohms
#define RO_CLEAN  (9.83) 

float Ro = 10; 
String gas_name[] = {"CO", "Smoke", "CH4", "Alcohol", "H2", "Propane", "LPG"};
float x1[] = {2.30, 2.91, 2.30, 2.70, 3.0, 2.91, 2.91};
float y1[] = {0.71, 0.30, 0.49, 0.30, 0.0, -0.04, -0.04};
float x2[] = {2.70, 3.70, 3.70, 3.70, 3.48, 3.30, 3.0};
float y2[] = {0.61, -0.04, -0.04, -0.04, -0.22, -0.22, -0.09};
float angular_coeff[7], q[7];

float GetAngularCoefficient(float x1, float y1, float x2, float y2) { return (y1-y2) / (x1 - x2); }
float GetQ(float m, float x1, float y1) { return (y1 - m*x1); }
float GetResistance(int n) { return ( (float)RL_VALUE * (1023 - n)/n ); }

void GasCalibration() {
  digitalWrite(blue_pin, HIGH);
  Serial.println("Calibrating gas sensor...");
  lcd.print("Calibrating...");
  
  Ro =0;
  for(int i=0;i<CALIBRATION_READS;i++) {
    Ro += GetResistance( analogRead(gas_pin) );
    delay(CALIBRATION_INTERVAL * 1000);
  }
  Ro /= CALIBRATION_READS;
  Ro /= RO_CLEAN;
  Serial.println("Gas sensor calibrated!!!");
  digitalWrite(blue_pin, LOW);
  lcd.print("Done!");
}

float GasRead() {
  float ris=0;
  for(int i=0;i<GAS_READS;i++) {
    ris += GetResistance( analogRead(gas_pin) );
    delay(GAS_READ_INTERVAL * 1000);
  }
  return ris/GAS_READS;
}

void reset() {
  lcd.clear();
  lcd.setCursor(0, 0);
  digitalWrite(green_pin, LOW);
  digitalWrite(yellow_pin, LOW);
  digitalWrite(red_pin, LOW);
  digitalWrite(blue_pin, LOW);
  noTone(piezo_pin);
}

void setup() {
  Serial.begin(9600);
  
  lcd.begin(16, 2);
  temperature_sensor.begin();
  pinMode(flame_pin, INPUT);
  pinMode(gas_pin, INPUT);
  pinMode(piezo_pin, OUTPUT);
  pinMode(green_pin, OUTPUT);
  pinMode(yellow_pin, OUTPUT);
  pinMode(red_pin, OUTPUT);
  pinMode(blue_pin, OUTPUT);
  pinMode(button_pin, INPUT);
  
  reset();
  
  GasCalibration();
  for(int i=0;i<7;i++) {
    angular_coeff[i] = GetAngularCoefficient(x1[i], y1[i], x2[i], y2[i]);
    q[i] = GetQ(angular_coeff[i], x1[i], y1[i]);
  }
  
}

void loop() {
  reset();
  
  // Button calibration
    if(digitalRead(button_pin)==HIGH) GasCalibration();
  
  bool safe_place = true, not_so_safe = false, get_out_now = false;
  
  digitalWrite(blue_pin, HIGH);
  lcd.clear();
  lcd.setCursor(0, 0);
  
  // Temperature:
    float h = temperature_sensor.readHumidity();
    float t = temperature_sensor.readTemperature();
  
    if (isnan(t) || isnan(h)) Serial.println("Failed to read temperature");
    else 
    {
        Serial.print("Humidity: "); 
        Serial.print(h);
        Serial.print(" %\t");
        Serial.print("Temperature: "); 
        Serial.print(t);
        Serial.println(" *C");
        
        lcd.print("Temp: ");
        lcd.print(t);
        lcd.print(" *C");
        
        if(t > TEMP_GREEN_MAX && t <= TEMP_YELLOW_MAX) not_so_safe=true;
        else if(t > TEMP_YELLOW_MAX) get_out_now = true;
    }
    delay(10);
    
  // Gas:
    lcd.setCursor(1, 1);
    float Rs = GasRead();
    float y = log10(Rs / Ro);
    for(int i=0;i<7;i++) {
      Serial.print(gas_name[i]);
      Serial.print(" : ");
      float ppm = pow(10, (y - q[i]) / angular_coeff[i]);
      Serial.print(ppm);
      Serial.println(" ppm");
      if(gas_name[i] == GAS_TO_CHECK) {
        lcd.print(GAS_TO_CHECK);
        lcd.print(": ");
        lcd.print(ppm);
        lcd.print(" ppm");
      }
      
      if(gas_green_max[i]==-1) continue;
      if(ppm > gas_green_max[i] && ppm <= gas_yellow_max[i]) not_so_safe = true;
      else if(ppm > gas_yellow_max[i]) get_out_now = true;
    }
    delay(10);
  
  // Flame:
    int flame_value = analogRead(flame_pin);
    if(flame_value <= CHECK_FLAME) {
      get_out_now = true;
      Serial.print("Flame: ");
    }
    else Serial.print("No flame: ");
    Serial.println(flame_value);
    
  digitalWrite(blue_pin, LOW);
  
  if(get_out_now) {
    digitalWrite(red_pin, HIGH);
    if(ALARM_ON) tone(piezo_pin, ALARM_RED_FREQ, INTERVAL_TIME*1000);
  }
  else if(not_so_safe) {
    digitalWrite(yellow_pin, HIGH);
    if(ALARM_ON) tone(piezo_pin, ALARM_YELLOW_FREQ, (INTERVAL_TIME / 6.0) * 1000);
  }
  else digitalWrite(green_pin, HIGH);
  
  delay(INTERVAL_TIME * 1000);
}

