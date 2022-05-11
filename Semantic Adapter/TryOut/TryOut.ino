void setup() {
  Serial.begin(250000);
  Serial.print("BEGIN");
}

void loop() {
  
  if(Serial.read() == '<'){
    Serial.println("running!");
  }
}
