
#define printName(f) _printName(f, #f)

void setup() {
  Serial.begin(250000);

}

void loop() {
  Serial.print(printName(HelloWorld));
}

String* HelloWorld(){
}

String _printName(void func(), const String& funcName){
    return funcName;
}
