void setup() {
  Serial.begin(250000);
}


String parse(String uri, String s) {
  int first = 0, second = 0;
  int i = 0;
  first = s.indexOf(':');
  second = s.indexOf(':', first+1);

  if(first == -1 || second == -1)
    return "";
  if(s.substring(0, first).equals(uri)){
    return s.substring(first, second);
  } 
  return parse(uri, s.substring(second+1));
}

void loop() {
  String y = parse("uri2", "uri:12.52:pas:ssdfasdf:uri2:asda:");
  Serial.print("Result: ");
  Serial.println(y);
  delay(2000);
}
