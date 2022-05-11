# SemanticPlugAndPlay
This Repository is the first step to easily use hardware components in an software enviroment. 
Using semantic-web-technology, hardware can be described and then mapped to processes defined in java (OOD-API).
The Idea is seen in the following figure.
![short_explanation](/uploads/8100b5ce97314744acf83e423ebf3f26/short_explanation.jpg)

# Typical Workflow
## [Arduino](https://gitlab.isse.de/robotik/semanticplugandplay/semanticplugandplay/-/tree/master/Semantic%20Adapter)
- get the Arduino Library PythonComm
- open one ".ino" example and modify it
    - For Implementing one Sensor/Actuator function use 
    ```C++
    String yourFunc(String s)
    ```
    - you should return a result as string
    - the string parameter are the specific arguments you want to use
    - configure pycom.begin()
- flash it onto an Arduino/ESP8226
- If you want to use more than one parameter/return value, you can modify the json-translation
    - default delimiter is ","
## [Protege (Ontology)](https://gitlab.isse.de/robotik/semanticplugandplay/semanticplugandplay/-/tree/master/Ontology)
- open the "Ontology->CommandOntology.owl" and setup your device.
## [Python (Semantic Controller)](https://gitlab.isse.de/robotik/semanticplugandplay/semanticplugandplay/-/blob/master/Semantic%20Controller)
- After this run "Setup->Setup.py" (doesn´t work with Linux subsystem due to different usb mapping)
    - There you can test your implementation using the pycom protocol
        - for the first "String yourFunc(String s)" type "0:yourParameter" and hit the "sensor"-button
        - the "hertz"-button sets the streaming rate, which then can be triggered by
        - hit the "stream" button with "0:yourParameter" in the textfield
    - With "save"-button first type in the URI(aka. deviceName) used in the Ontology
    - Then (optional) save your modified JSON-Translation
    - hit the "write" button to save your "saved" strings onto the EEPROM
## [Java (OOD-API)](https://gitlab.isse.de/robotik/semanticplugandplay/semanticplugandplay/-/blob/master/OOD-API)
- Open OOD-API inside an IDE (preferrably IntelliJ)
    - Get an Idea how it works by looking at HouseAutomationSystem.java
    - For Ease of access you can use the name of your device as requirement in the constructor of an device (.java)

- Start "SemanticController->SerialPortListener.py" then start the MAIN of your java code.
- Pray that it works
