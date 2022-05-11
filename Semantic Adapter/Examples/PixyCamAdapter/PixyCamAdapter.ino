#include <PythonComm.h>
#include <Arduino.h>
#include <SPI.h>  
#include <Pixy.h>

// This is the main Pixy object 
Pixy pixy;

String weight = "0.00100000";

void setup() {
  pythonComm.init(115200);
  pythonComm.registerDevice("PixyCamR1");
  //Order is important! first Capability URI, then the function pointer of the Cap-implementation
  pythonComm.registerCaps("PixyCamDetectObject", PixyCamDetectObject);
    
  pythonComm.registerDynamix("Weight", &weight, getWeight, setWeight);
  pixy.init();
}

void loop() {
  pythonComm.run();
}

String PixyCamDetectObject(String s){
  static int i = 0;
  int signature = ParameterFromString("PixyCamSignatureNumber",s).toInt();
  uint16_t blocks = pixy.getBlocks();
  for (int j=0; j<blocks; j++)
  {
    if(pixy.blocks[j].signature == signature){
      return ParameterToString("PixyCamSignatureNumber", String(signature).c_str(), "PixyCamXPosition", String(pixy.blocks[j].x).c_str(), "PixyCamYPosition", String(pixy.blocks[j].y).c_str(), "PixyCamWidth", String(pixy.blocks[j].width).c_str(), "PixyCamHeight", String(pixy.blocks[j].height).c_str(), NULL);
    }
  }
  return ParameterToString("PixyCamSignatureNumber", String(signature).c_str(), "PixyCamXPosition", "-1"/*String(random(-30, 5)).c_str()*/, "PixyCamYPosition", "-1", "PixyCamWidth", "-1", "PixyCamHeight", "-1", NULL);
}

String setWeight(String s){
  weight = ParameterFromString("SimpleDoubleParameter", s);
  pythonComm.saveDynamix(weight);
  return getWeight("");
}

String getWeight(String s){
  return ParameterToString("SimpleDoubleParameter", weight, NULL);
}
