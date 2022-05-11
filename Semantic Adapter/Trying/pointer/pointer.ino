#define PORTA *((char *) 0x100)

void setup() {
  PORTA = 'g';
  char var;
  var = PORTA;
}

void loop() {
  // put your main code here, to run repeatedly:

}
