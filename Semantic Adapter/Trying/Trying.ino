#include <EEPROM.h>

String arr[2] = {};
void registerT(int count, ...);
void saveT(int count, ...);

char* s = "abc";
char* s1 = "edf";

void setup() {
  Serial.begin(250000);
  //registerT(2, &s, &s1);
  for(int i = 0; i < 1024; i++){
    EEPROM[i] = 0;
  }
  Serial.print("done");
}

void loop() {
  
  
  char a = Serial.read();
  if(a == 'a'){
    registerT(2, &s, &s1);
  } else if (a == 'b'){
    saveT(2, s, s1);
  } else if( a == 'c'){
    s = "123";
    s1 = "321";
  } else if(a == 'd'){
    Serial.println(s);
    Serial.println(s1);
  }
}

void registerT(int count, ...){
  va_list vl;
  va_start(vl, count);
  char* buffer;
  Serial.println(EEPROM.get(10, buffer));
  Serial.println(buffer);
  va_arg(vl, String) = buffer;
  EEPROM.get(10 + 10, buffer);
  Serial.println(buffer);
  va_arg(vl, String) = buffer;
  va_end(vl);
}

void saveT(int count, ...){
  va_list vl;
  va_start(vl, count);
  EEPROM.put(10, va_arg(vl, char*));
  EEPROM.put(10 + 10, va_arg(vl, char*));
  va_end(vl);
  
}
