#include <PythonComm.h>
#include <Arduino.h>

String calibration = "aaaaaaaaa";

void setup() {
  //Order is important! first Capability URI, then the function pointer of the Cap-implementation
  pythonComm.registerCaps("MeasureHumidityCapability", MeasureHumidityCapability, "MeasureTemperatureCapability", MeasureTemperatureCapability);
  pythonComm.registerDevice("DHT-11 has Dynamix CalibrationPropertyURI");
  
  // Order is important! first the URI, then pointer to the Dynamix-variable, then getter, then setter
  pythonComm.registerDynamix("CalibrationURI", &calibration, getCalibration, setCalibration);
}

void loop() {
  pythonComm.run();
}

String getCalibration(String s){
  return calibration;
}

String setCalibration(String s){
  if(s == NULL)
    return "";
  calibration = s;
  pythonComm.saveDynamix(calibration);
  return calibration;
}

String MeasureHumidityCapability(String s){
  return "83.5";
}

String MeasureTemperatureCapability(String s){
  return "34.5";
}
