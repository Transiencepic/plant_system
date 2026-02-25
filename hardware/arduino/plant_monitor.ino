#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define SOIL_PIN A0
#define PUMP_PIN 7  // 水泵控制引脚（接继电器）

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);  // 初始关闭
}

void loop() {
  // ----- 1. 发送传感器数据 -----
  float temp = dht.readTemperature();
  float humi = dht.readHumidity();
  int soil = analogRead(SOIL_PIN);

  Serial.print(temp);
  Serial.print(",");
  Serial.print(humi);
  Serial.print(",");
  Serial.println(soil);

  // ----- 2. 接收树莓派指令 -----
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.startsWith("PUMP:")) {
      // 解析浇水秒数，格式 "PUMP:5"
      int seconds = cmd.substring(5).toInt();
      
      // 开水泵
      digitalWrite(PUMP_PIN, HIGH);
      
      // 延时
      delay(seconds * 1000);
      
      // 关水泵
      digitalWrite(PUMP_PIN, LOW);
      
      // 回复树莓派：浇水完成
      Serial.println("PUMP_DONE");
    }
  }
  
  delay(2000);
}