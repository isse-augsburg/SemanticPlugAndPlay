#include <PythonComm.h>
#include <Arduino.h>

#define ELECTROMAGNET_PIN 2
String magnet_status = "off";
String weight = "0.00100000";

void setup() {
  pythonComm.init(115200);
  //Order is important! first Capability URI, then the function pointer of the Cap-implementation
  pythonComm.registerCaps("turnMagnetOn", turnMagnetOn, "turnMagnetOff", turnMagnetOff);
  pythonComm.registerDevice("OpenSmart_Electromagnet");
  pinMode(ELECTROMAGNET_PIN, OUTPUT);
  
  // Order is important! first the URI, then pointer to the Dynamix-variable, then getter, then setter
  pythonComm.registerDynamix("MagnetStatus", &magnet_status, getMagnetStatus, setMagnetStatus, "Weight", &weight, getWeight, setWeight);
  if(magnet_status == "on"){
    digitalWrite(ELECTROMAGNET_PIN, HIGH);
  }
}

void loop() {
  pythonComm.run();
}

String turnMagnetOn(String s){
  digitalWrite(ELECTROMAGNET_PIN, HIGH);
  setMagnetStatus("MagnetStatus:on:");
  return ParameterToString("MagnetStatus", magnet_status.c_str(), NULL);
}

String turnMagnetOff(String s) {
  digitalWrite(ELECTROMAGNET_PIN, LOW);
  setMagnetStatus("MagnetStatus:off:");
  return ParameterToString("MagnetStatus", magnet_status.c_str(), NULL);
}

String setMagnetStatus(String s){
  String status = ParameterFromString("MagnetStatus", s);
  if(NULL == status)
    return "";
  
  if(status == "off"){
    turnMagnetOff("");
  } else if (status == "on") {
    turnMagnetOn("");
  } else {
    return "";
  }
  magnet_status = status;
  pythonComm.saveDynamix(magnet_status, weight);
  return ParameterToString("MagnetStatus", magnet_status.c_str(), NULL);
}

String getMagnetStatus(String s) {
  return ParameterToString("MagnetStatus", magnet_status.c_str(), NULL);
}

String setWeight(String s){
  weight = ParameterFromString("SimpleDoubleParameter", s);
  pythonComm.saveDynamix(magnet_status, weight);
  return getWeight("");
}

String getWeight(String s){
  return ParameterToString("SimpleDoubleParameter", weight.c_str(), NULL);
}
