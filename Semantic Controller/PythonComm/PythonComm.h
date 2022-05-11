#ifndef PythonComm_h
#define PythonComm_h

#include <Arduino.h>
#include <EEPROM.h>

#ifndef __AVR__
	#include "user_interface.h"
#else
	#include <avr/io.h>
	#include <avr/interrupt.h>
#endif


#define NUMBER_CAPABILITIES 1
#define NUMBER_DYNAMIX 1

#ifndef NUMBER_CAPABILITIES
	#error "Please define NUMBER_CAPABILITIES"
#endif

#ifndef NUMBER_DYNAMIX
	#error "Please define NUMBER_DYNAMIX"
#endif


#define MAX_SIZE_DYNAMIX 16
//The maximum length used by the Developer
#define MAX_SIZE_OF_STRING_CALLBACK 32
//The maximum count of Strings in array
#define MAX_STRINGS 2
//maximal size of a string
#define MAX_BYTES 128
//startMarker also is an escape flag
#define startMarker 0x3C
#define endMarker 0x3E

//#define ParameterToString(...) ParameterToString(..., NULL)

String ParameterFromString(String uri, String s);
String ParameterToString(const char* first, ...);

struct MAPPER{
	String uri;
	String (*func)(String s);
};

class PythonComm{
public:
	void registerCaps(...);
	void registerDevice(String dev_uri);
	void run();
	void sendSensorDataCallback();
	void writeEEPROM();
	void loadEEPROM();
	void registerDynamix(...);
	void initializeDynamix(va_list vl);
	void saveDynamix(...);
	/**In a timer this will be set true if it´s time to send stream data;
	this boolean will be checked in every state, then the Callback function is called*/
	volatile bool sendData = false;

	#ifndef __AVR__
	/**needed for ISR for ESP*/
	long timer_wait = 0;
	#endif
private:
	/**Primary Array to save smaller arrays, which can be addressed by 'position'*/
	char message_buffer[MAX_BYTES] = {};
	/**Used to address The saved char arrays*/
	int position[MAX_STRINGS] = {};
	//needed to know if the current state is streaming or not*/
	bool streaming = false;
	/**Borders to define the range within the stream shall publish*/
	float minRange = 0, maxRange = 0;

	/**Streams per second */
	double intern_hz = 0;
	/**The Callback Function pointer */
	MAPPER MapperArray[NUMBER_CAPABILITIES + NUMBER_DYNAMIX*2] = {};
	/** Dynamix URI array*/
	String DynamixArray[NUMBER_DYNAMIX] = {};
	/**The streams which are currently running*/
	int current_stream_callback = -1;
	char current_stream_callback_params[MAX_SIZE_OF_STRING_CALLBACK] = {};
	/**The source of the current stream */
	long current_stream_src = -1;


	void receiveData();
	byte readByte();
	void sendMessageString(String message);
	void check();
	void error(byte errorCode);
	void sendSensorData();
	void manageStream();
	void receiveDataToStore();
	void sendStoredString();
	void deleteStoredString();
	void receiveRange();
	void sendCapabilityURIs();
	void sendDynamixURIs();
	void writeToEEPROM();
	void loadFromEEPROM();
	void setNewHz();
};

extern PythonComm pythonComm;

#endif
