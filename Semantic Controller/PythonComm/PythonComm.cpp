#include "PythonComm.h"


/*Preinstantiate  */
PythonComm pythonComm;

String ParameterFromString(String uri, String s) {

  int first = 0, second = 0;
  int i = 0;
  first = s.indexOf(':');
  second = s.indexOf(':', first+1);

  if(first == -1 || second == -1)
    return "";
  if(s.substring(0, first).equals(uri)){
    return s.substring(first+1, second);
  }
  return ParameterFromString(uri, s.substring(second+1));
}

String ParameterToString(const char* first, ...){
	String s = "";
	s.reserve(256);
	va_list vl;
	va_start(vl, first);
	const char* str = first;
	while(str != NULL){
		s+= str;
		s+= ':';
		str = va_arg( vl, const char* );
	}
	va_end(vl);
	return s;
}

#ifdef __AVR__
ISR(TIMER1_COMPA_vect)	{
	TCNT1 = 0;
	/*ISR for Arduino, waits the ticks written in OCR1A
	sets sendData to signalize that the timer has been turned on*/
	pythonComm.sendData = true;
}
#else
void ICACHE_RAM_ATTR onTimerISR(){
    /*sets sendData to signalize that the timer has been turned on*/
	pythonComm.sendData = true;
	/*Timer needs to be rewritten*/
    timer1_write(pythonComm.timer_wait);
}
#endif

/**
Helper function to safely read Bytes

*/
byte PythonComm::readByte(){
	if(sendData && streaming){
			pythonComm.sendSensorDataCallback();
	}
	//Need to be there to garantuee safe communication
	while(!Serial.available()){
		if(sendData && streaming){
			pythonComm.sendSensorDataCallback();
		}
	}
	byte b = Serial.read();
	//Probably another Statement, or is it ?
	if(b == startMarker){
		//Need to be there to garantuee safe communication
		while(!Serial.available()){
			if(sendData && streaming){
				pythonComm.sendSensorDataCallback();
			}
		}
		byte b2 = Serial.peek();
		//is something escaped?
		if(b2 == startMarker || b2 == endMarker){
			//Empty Serial buffer
			Serial.read();
			return b2;
		} else {
			receiveData();
			return readByte();
		}
	}
	return b;
}

/**
Configures timers and begins serial communication.

@param ... varargs of callback functions
*/
void PythonComm::registerCaps(...){
	Serial.begin(230400);
  #ifndef __AVR__
  EEPROM.begin(1024);
  #endif
	va_list vl;
	va_start(vl, NUMBER_CAPABILITIES);
	//MapperArray = (MAPPER*) realloc(MapperArray, NUMBER_CAPABILITIES * sizeof(MAPPER));
	for(int i = 0; i < NUMBER_CAPABILITIES; i++){
		MapperArray[i].uri = va_arg(vl, const char*);
		MapperArray[i].func = va_arg(vl, String (*)(String s));
		//Serial.println(MapperArray[i].uri);
	}
	va_end(vl);
	while(!Serial){}; //waits for arduino to be ready
}

/**
TO BE DELETED

 */
void PythonComm::registerDevice(String dev_uri){
	for(int i = 0; i < dev_uri.length(); i++){
		message_buffer[i] = dev_uri.charAt(i);
	}
	position[0] = dev_uri.length();
	writeEEPROM();
}

/**
Registers the dynamic properties.

saves them to EEPROM if there was nothing
*/
void PythonComm::registerDynamix(...){
	va_list vl;
	va_start(vl, NUMBER_DYNAMIX);
	char buffer[MAX_SIZE_DYNAMIX] = {};
	for(int i = 0, map_array = 0; i < NUMBER_DYNAMIX;i++){
		//Fill the DynamixArray
		DynamixArray[i] = va_arg(vl, const char*);
		//Do EEPROM magic -> save to EEPROM if empty, load from EEPROM if there is something
		for(int j = 0; j < MAX_SIZE_DYNAMIX; j++){
			if(EEPROM[MAX_BYTES *sizeof(char) + MAX_STRINGS * sizeof(int) + 2 + i*MAX_SIZE_DYNAMIX + j] == 0 && i == 0 && j == 0){
				initializeDynamix(vl);
				break;
		    }
		    if(EEPROM[MAX_BYTES *sizeof(char) + MAX_STRINGS * sizeof(int) + 2 + i*MAX_SIZE_DYNAMIX + j] != 0)
				buffer[j] = EEPROM[MAX_BYTES *sizeof(char) + MAX_STRINGS * sizeof(int) + 2 + i*MAX_SIZE_DYNAMIX + j];
		    else{
			    buffer[j] = '\0';
				break;
			}
		}
		va_arg(vl, String) = buffer;
		//Add getter and setter to our capabilities
		//Get
		MapperArray[NUMBER_CAPABILITIES+map_array].uri = "Get" + DynamixArray[i];
		MapperArray[NUMBER_CAPABILITIES+map_array++].func = va_arg(vl, String (*)(String s));
		//Set
		MapperArray[NUMBER_CAPABILITIES+map_array].uri = "Set" + DynamixArray[i];
		MapperArray[NUMBER_CAPABILITIES+map_array++].func = va_arg(vl, String (*)(String s));
	}

	va_end(vl);
}

/**
Saves the dynamic properties. gets called from outside to persist changed data.
*/
void PythonComm::saveDynamix(...){
  va_list vl;
  va_start(vl, NUMBER_DYNAMIX);
  initializeDynamix(vl);
}

/**
This is a helper function, to get called if the dynamic properties arent inside the EEPROM
*/
void PythonComm::initializeDynamix(va_list vl){
  char buffer[MAX_SIZE_DYNAMIX] = {};
  for(int i = 0; i < NUMBER_DYNAMIX;i++){
	  va_arg(vl, String).toCharArray(buffer, MAX_SIZE_DYNAMIX);
	  //strcpy(buffer, va_arg(vl, const char*));
	  //buffer = va_arg(vl, char*);
	  //Serial.println(buffer);
	  //Serial.println("BUFFER: " + String(buffer) + "Size: " + String(sizeof(buffer)));
	  for(int j = 0; j < MAX_SIZE_DYNAMIX;j++){
      #ifdef __AVR__
		  if(buffer[j] == 0){
		  EEPROM.update(MAX_BYTES *sizeof(char) + MAX_STRINGS * sizeof(int) + 2 + i*MAX_SIZE_DYNAMIX + j, '\0');
			  break;
		  }
		  EEPROM.update(MAX_BYTES *sizeof(char) + MAX_STRINGS * sizeof(int) + 2 + i*MAX_SIZE_DYNAMIX + j, buffer[j]);
      #else
      if(buffer[j] == 0){
		  EEPROM.put(MAX_BYTES *sizeof(char) + MAX_STRINGS * sizeof(int) + 2 + i*MAX_SIZE_DYNAMIX + j, '\0');
			  break;
		  }
		  EEPROM.put(MAX_BYTES *sizeof(char) + MAX_STRINGS * sizeof(int) + 2 + i*MAX_SIZE_DYNAMIX + j, buffer[j]);
      EEPROM.commit();
      #endif
	  }
  }
  #ifndef __AVR__
	if (!EEPROM.commit()){
	  return;
	}
  #endif
  va_end(vl);
}

/**
This function gets called inside the 'loop'.
if streaming is enabled and the timer has expired (=sendData)
the previous set Callback function (see @setCallbacks) gets called.

If there is a the beginning of an statement (@startMarker) PythonComm wait´s for
another byte to determine the Type of the statement see @receiveData
*/
void PythonComm::run(){

	if(sendData && streaming){
		pythonComm.sendSensorDataCallback();
	}
	if(Serial.read() == startMarker){
		receiveData();
	}
}

/**
Determines the Type of the Statement being received
*/
void PythonComm::receiveData(){
	if(sendData && streaming){
		pythonComm.sendSensorDataCallback();
	}
	check();
	byte inByte = Serial.read();
	switch(inByte){
		//Request Sensor Data. for example <a1>, <a3>
		case 'a':
			sendSensorData();
			break;
		//Store the following string into @message_buffer and @position. for example <b3:hey>
		case 'b':
			//Expects further Data
			receiveDataToStore();
			break;
		//send stored Data. for example <c0>
		case 'c':
			sendStoredString();
			break;
		//delete stored Data. for example <d0>
		case 'd':
			//use with Care!!
			deleteStoredString();
			break;
		//send current range or set range. for example <r>, <r10.00:423.43>
		case 'r':
			receiveRange();
			break;
		case 't':
			sendCapabilityURIs();
			break;
		case 'k':
			sendDynamixURIs();
			break;
		//opens/closes the stream. for example <s>
		case 's':
			manageStream();
			break;
		//Write saved strings from @message_buffer and @position to eeprom. for example <w>
		case 'w':
			writeToEEPROM();
			break;
		//load written strings from eeprom into @message_buffer and @position. for example <l>
		case 'l':
			loadFromEEPROM();
			break;
		//set new hz for streaming
		case 'h':
			setNewHz();
			break;
		//Statements are recursive. for example <<a>a>, <b3<a1>:h<a2>ey> are valid statements
		case startMarker:
			//new statement.
			receiveData();
			//"old" statement
			receiveData();
			break;
		//any statement that has an invalid typeByte. for example <y>
		default:
			Serial.write(char(startMarker));
			Serial.write(char('x'));
			Serial.write(char(':'));
			if(inByte == startMarker || inByte == endMarker)
				Serial.write(startMarker);
			if(inByte != '\0' && inByte != '\n')
				Serial.write(char(inByte));
			Serial.write(char(endMarker));
			break;
	}
}

/**
Utility function for sending Strings byte by byte into the serial puffer.
Needed because builtin Serial.print(String s); doesn´t work as expected
when used with another Serial communicater other than Arduino IDE

@param message string that gets send
*/
void PythonComm::sendMessageString(String message){
	for(int i = 0; i < sizeof(message);i++){
		Serial.write(message.charAt(i));
	}
}

/**Blocks until something is beeing transmitted over serial*/
void PythonComm::check(){
	while(!Serial.available());
}

/**
Reports to the Communication Partner which Statement was sent wrongly, or which funtion had an error.
For example if <aa> is sent, then PythonComm answers with <e:a>

@param errorCode the type-byte of the statement that failed
*/
void PythonComm::error(byte errorCode){
	Serial.write(char(startMarker));
	sendMessageString("e:");
	Serial.write(char(errorCode));
	Serial.write(char(endMarker));

}

/**
Type-Byte 'a'
Calls the Callback funtions given to @setCallbacks depending which string follows the type-byte.
For example <a:Echo:params> calls the first function called "Echo" with params(as string) as parameter;
*/
void PythonComm::sendSensorData(){
	String string;
	string.reserve(MAX_SIZE_OF_STRING_CALLBACK);

	//read the source
	byte b = readByte();
	while(b != ':'){
		if(sendData && streaming){
			sendSensorDataCallback();
		}

		if(b == endMarker || b > '9' || b < '0' ){
			error('a');
			return;
		} else {
			string += (char)b;
		}

		b = readByte();
	}
	int src = string.toInt();
	string = "";

	//read the specifier string
	b = readByte();
	while(b != ':'){
		if(b == endMarker){
			error('a');
			return;
		} else {
			string += (char)b;
		}

		b = readByte();
	}
	//get the index of the @MapperArray
	int switcher = -1;
	for(int i = 0; i < NUMBER_CAPABILITIES + NUMBER_DYNAMIX*2; i++){
		if(MapperArray[i].uri==string){
			switcher = i;
			break;
		}
	}
	if(switcher < 0){
		error('a');
		return;
	}

	//read the parameter string
	string = "";
	int a = 0;
	while(a < MAX_SIZE_OF_STRING_CALLBACK){
		char rb = readByte();
		if(rb == endMarker){
			break;
		}

		string+=rb;;
		a++;
	}
	Serial.write((char)startMarker);
	Serial.write((char)'a');
	Serial.print(src);
	Serial.write((char)':');
	Serial.print(MapperArray[switcher].uri);
	Serial.write((char)':');
	string = MapperArray[switcher].func(string);
	//Escape the start-and-endMarker
	int i = 0;
	char ch = string.charAt(i++);
	while(ch != 0){
		if(ch == startMarker ||ch == endMarker)
			Serial.write((char)startMarker);
		Serial.write(ch);
		ch = string.charAt(i++);
	}
	Serial.write((char)endMarker);
}

/**
Helper function that calls the stream-callback function
*/
void PythonComm::sendSensorDataCallback(){

	if(streaming){
		sendData = false;
		Serial.write((char)startMarker);
		Serial.write((char)'a');
		Serial.print(current_stream_src);
		Serial.write((char)':');
		Serial.print(MapperArray[current_stream_callback].uri);
		Serial.write((char)':');
		String string;
		string.reserve(MAX_SIZE_OF_STRING_CALLBACK);
		string = MapperArray[current_stream_callback].func(current_stream_callback_params);
		//Escape the start-and-endMarker
		int i = 0;
		char ch = string.charAt(i++);
		while(ch != 0){
			if(ch == startMarker ||ch == endMarker)
				Serial.write((char)startMarker);
			Serial.write(ch);
			ch = string.charAt(i++);
		}
		Serial.write((char)endMarker);

		//Serial.print("<a"+ String(current_stream_src) +":" + MapperArray[current_stream_callback].uri + ":" + MapperArray[current_stream_callback].func(current_stream_callback_params) + ">");
	}
}

/**
Type-Byte 'b'
Expects first the length of the string, then ':' and then the string. If the string contains a @startMarker or @endMarker,
then @startMarker is used to escape them, this doesn´t account for the length of the string. If the length provided is wrong, error
gets called.
*/
void PythonComm::receiveDataToStore(){
	//init local variables
	int length = 0, checksum = 0;
	check();
	//No length provided, send error
	if(Serial.peek() < '0' || Serial.peek() > '9'){
		//check for new Statement
		if(Serial.peek() == startMarker){
			Serial.read();
			receiveData();
		//if there is no @startMarker and no number, the statement is invalid
		} else {
			error('b');
			return;
		}
	}
	//arduino.h allows this utility function
	length = Serial.parseInt();
	check();
	//check for new Statement
	if(Serial.peek() == startMarker){
		Serial.read();
		receiveData();
	}
	//checks if : is there
	if(Serial.read() != ':'){
		error('b');
		return;
	}
	if(sendData && streaming){
			sendSensorDataCallback();
	}
	check();
	//"Allocating" Space inside the array,
	//gets saved into the first space it fits
	//pos is the byte offset from which on the message will be written inside the array
	int ret_position = 0, pos = 0;
	for(int i = 0; i < MAX_STRINGS; i++){
		if(position[i] == 0){
			for(int j = 0; j < i; j++){
				pos += position[j];
			}
			if(pos + length > MAX_BYTES){
				//Serial.println("Too many");
				error('b');
				return;
			}
			position[i] = length + 1;
			ret_position = i;
			break;
		}
	}

	//parses data and calculates Checksum.
	int a = 0;
	for(a; a < length;a++){
		if(sendData && streaming){
			sendSensorDataCallback();
		}
		check();
		char rb = char(Serial.read());
		//If it´s an startMarker we just want to make sure if it´s used as an Flag
		//or if it´s a new beginning for a statement
		if(rb == startMarker){
			check();
			rb = char(Serial.peek());
			//new statement
			if(rb != startMarker && rb != endMarker){
				receiveData();
			}
			check();
			//read the new byte
			rb = Serial.read();
			message_buffer[pos+a] = rb;
			checksum += rb;
			continue;
		} else if(rb == endMarker){
			break;
		}
		if(sendData && streaming){
			sendSensorDataCallback();
		}
		message_buffer[pos+a] = rb;
		//The checksum is created by summarize the bytes and modulo the sum with 1481
		checksum += rb;
		checksum %= 1481;
	}
	//add binary 0 to end part-array
	message_buffer[pos+a] = '\0';
	//Some Data went missing
	if(a != length){
		//There was a Problem, the given Length was not correct
		position[ret_position] = 0;
		error('b');
		return ;
	}
	check();
	if(Serial.peek() == startMarker){
		//empty < from Puffer
		Serial.read();
		//execute new statement
		receiveData();
	}
	check();
	if(Serial.read() != endMarker){// || message == ""){
		position[ret_position] = 0;
		error('b');
		return;
	}

	//Respond with Type-byte and Checksum and address
	Serial.write(char(startMarker));

	if(sendData && streaming){
		sendSensorDataCallback();
	}
	Serial.write(char('b'));

	sendMessageString(String(checksum));

	Serial.write(char('@'));

	if(sendData && streaming){
		sendSensorDataCallback();
	}
	sendMessageString(String(ret_position));

	Serial.write(char(endMarker));
}

/**
Type-Byte 's'
Expects a number interpretated as index for a callback, which then
gets repeadetly called, according to intern_hz
*/
void PythonComm::manageStream(){
	//read the source
	byte b = readByte();
	if(b == endMarker){
		streaming = false;
		Serial.print(F("<s0>"));
		return;
	}
	String string;
	string.reserve(MAX_SIZE_OF_STRING_CALLBACK);
	while(b != ':'){
		if(sendData && streaming){
			sendSensorDataCallback();
		}

		if(b == endMarker || b > '9' || b < '0' ){
			error('s');
			return;
		} else {
			string += (char)b;
		}

		b = readByte();
	}
	current_stream_src = string.toInt();
	string = "";

	//read the specifier string (uri)
	b = readByte();
	while(b != ':'){
		if(sendData && streaming){
			sendSensorDataCallback();
		}

		if(b == endMarker){
			error('s');
			return;
		} else {
			string += (char)b;
		}

		b = readByte();
	}
	//get the index of the @MapperArray
	int switcher = -1;
	for(int i = 0; i < NUMBER_CAPABILITIES + NUMBER_DYNAMIX*2; i++){
		if(MapperArray[i].uri==string){
			switcher = i;
			break;
		}
	}
	if(switcher < 0){
		error('s');
		return;
	}

	//read the parameter string
	int a = 0;
	while(a < MAX_SIZE_OF_STRING_CALLBACK){
		if(sendData && streaming){
			sendSensorDataCallback();
		}

		char rb = readByte();
		if(rb == endMarker){
			break;
		}

		current_stream_callback_params[a]=rb;
		a++;
	}

	current_stream_callback_params[a]='\0';
	streaming = true;
	current_stream_callback = switcher;
	Serial.print("<s"+ String(current_stream_src) + ":" + MapperArray[switcher].uri + ":"+ String(current_stream_callback_params) + ">");
}

/**
Type-Byte 'c'
Expects a number interpretated as Adress. Sends the stored string back
*/
void PythonComm::sendStoredString(){
	int number = 0;
	check();
	//No Number provided, send error
	if(Serial.peek() < '0' || Serial.peek() > '9'){
		//New Statement
		if(Serial.peek() == startMarker){
			Serial.read();
			receiveData();
		} else {
			error('c');
			return;
		}
	}
	number = Serial.parseInt();

	//Makes sure arduino doesn´t write it´s ram onto the serial port...
	if(readByte() != endMarker || number > MAX_STRINGS){
		error('c');
		return;
	}
	//calculates total position inside the array
	int pos = 0;
	for(int i = 0; i < number; i++){
		pos += position[i];
	}

	Serial.write((char)startMarker);
	Serial.print("c:"+String(number)+":");

	for(int i = 0; i < position[number];i++){

		//if there is a @startMarker in the message, there will be another @startMarker to escape the
		//previous @startMarker or @endMarker
		if((message_buffer+pos)[i] == startMarker || (message_buffer+pos)[i] == endMarker)
			Serial.write(startMarker);
		Serial.write((message_buffer+pos)[i]);

	}
	Serial.write(char(endMarker));
}

/**
Type-Byte 'd'
Expects a number interpretated as Addresss. Deletes the stored string.
*/
void PythonComm::deleteStoredString(){
	int number = 0;
	check();
	//No Number provided, send error
	if(Serial.peek() < '0' || Serial.peek() > '9'){
		//New Statement
		if(Serial.peek() == startMarker){
			Serial.read();
			receiveData();
		} else {
			error('c');
			return;
		}
	}
	number = Serial.parseInt();
	//if the string is the last stored, there just need to be adjustment
	if(number == MAX_STRINGS - 1 || position[number] == 0) {
		position[MAX_STRINGS-1] = 0;
	//otherwise all the following strings will be pushed one address before their previous
	} else {
		for(int i = number; i < MAX_STRINGS; i++){
			if(position[i] == 0){
				break;
			}
			int pos1 = 0;
			int pos2 = 0;
			for(int j = 0; j < i; j++){
				pos1 += position[j];
				pos2 += position[j];
			}
			pos2 += position[i];
			position[i] = position[i+1];
			strcpy(message_buffer + pos1, message_buffer + pos2);
		}
	}

	check();
	if(Serial.peek() == startMarker){
		//empty < from Puffer
		Serial.read();
		//execute new statement
		receiveData();
	}

	if(Serial.read() != endMarker){
		error('d');
		return;
	}

	int pos = 0;
	for(int i = 0; i < number; pos++){
		pos += position[i];
	}
	//Sends the input back to verify correctness
	//for debugging purpose
	Serial.write(char(startMarker));

	Serial.write(char('d'));

	sendMessageString(String(number));

	Serial.write(char(endMarker));
}

/**
Type-Byte 'r'
Sets or requests the range. To set the range two floats are required. To request the current range nothing but
the Type-Byte is given.
*/
void PythonComm::receiveRange(){
	int length = 0;
	//min and max are the local ranges to be set to the globals after checks.
	float min = 0, max = 0;
	check();
	if(Serial.peek() < '0' || Serial.peek() > '9'){
		//New Statement
		if(Serial.peek() == startMarker){
			Serial.read();
			receiveData();
		//sends the current range back
		} else if(Serial.peek() == endMarker){
			Serial.write((char)startMarker);
			Serial.write('r');
			Serial.print(String(minRange) + ":" + String(maxRange));
			Serial.write((char)endMarker);
			return;
		} else {
			error('r');
			return;
		}
	}

	min = Serial.parseFloat();

	if(readByte() != ':'){
		error('r');
		return;
	}
	check();
	if(Serial.peek() < '0' || Serial.peek() > '9'){
		//New Statement
		if(Serial.peek() == startMarker){
			Serial.read();
			receiveData();
		} else {
			error('r');
			return;
		}
	}
	max = Serial.parseFloat();

	if(readByte() != '>'){
		error('r');
		return;
	}
	//the max value always has to be greater than the min value.
	if(min > max){
		error('r');
		return;
	}
	minRange = min;
	maxRange = max;
	//send the current range back for verification
	Serial.write((char)startMarker);
	Serial.write('r');
	Serial.print(String(minRange) + ":" + String(maxRange));
	Serial.write((char)endMarker);
}

/**
 Type-Byte 't'
 Transmits current Cap URIs
 */
void PythonComm::sendCapabilityURIs(){
	if(readByte() != endMarker){
		error('t');
		return;
	}
	Serial.write(char(startMarker));
	Serial.write('t');
	Serial.write(':');
	for (int i = 0; i < NUMBER_CAPABILITIES + NUMBER_DYNAMIX*2 -1; i++)
	{
		Serial.print(MapperArray[i].uri + ",");
	}
	Serial.print(MapperArray[NUMBER_CAPABILITIES + NUMBER_DYNAMIX*2 -1].uri);
	Serial.write(char(endMarker));
}

/**
 Type-Byte 'k'
 Transmits current Dynamix URIs
 */
 void PythonComm::sendDynamixURIs(){
	if(readByte() != endMarker){
		error('k');
		return;
	}
	Serial.write(char(startMarker));
	Serial.write('k');
	Serial.write(':');
	if(NUMBER_DYNAMIX){
		for (int i = 0; i < NUMBER_DYNAMIX-1; i++)
		{
			Serial.print(DynamixArray[i] + ",");
		}
		Serial.print(DynamixArray[NUMBER_DYNAMIX-1]);
	}
	Serial.write(char(endMarker));
}



/**
Write to EEPROM
*/
void PythonComm::writeEEPROM(){
	EEPROM.put(0, position);
	EEPROM.put(sizeof(position), message_buffer);
	#ifndef __AVR__
	if (!EEPROM.commit()){
	  return;
	}
	#endif
}

/**
Type-Byte 'w'
Writes the saved strings to the EEPROM of the microcontroller.
*/
void PythonComm::writeToEEPROM(){
	check();
	if(Serial.peek() == startMarker){
		//empty < from Puffer
		Serial.read();
		//execute new statement
		receiveData();
	}
	EEPROM.put(0, position);
	EEPROM.put(sizeof(position), message_buffer);
	#ifndef __AVR__
	if (!EEPROM.commit()){
      error('w');
	  return;
	}
	#endif
	check();
	if(Serial.read() != endMarker){
		error('w');
		return;
	}
	//verifies the statement
	Serial.print("<w>");
}

/**
Load from EEPROM
*/
void PythonComm::loadEEPROM(){
	EEPROM.get(0, position);
	EEPROM.get(sizeof(position), message_buffer);
}

/**
Type-Byte 'l'
loads the strings in the EEPROM of the microcontroller into the @message_buffer.
*/
void PythonComm::loadFromEEPROM(){
	check();
	if(Serial.peek() == startMarker){
		//empty < from Puffer
		Serial.read();
		//execute new statement
		receiveData();
	}
	EEPROM.get(0, position);
	EEPROM.get(sizeof(position), message_buffer);
	check();
	if(Serial.read() != endMarker){
		error('l');
		return;
	}
	//verifies the statement
	Serial.print("<l>");
}

/**
Type-Byte 'h'
Sets the timer to a new timeout regarding the following hz. Or, if no new timeout is given, gives the current hz.
*/
void PythonComm::setNewHz(){
	double newHz;
	check();
	if(Serial.peek() == startMarker){
		//empty < from Puffer
		Serial.read();
		//execute new statement
		receiveData();
	}
	check();
	if(Serial.peek() < '0' || Serial.peek() > '9'){
		//New Statement
		if(Serial.peek() == startMarker){
			Serial.read();
			receiveData();
		} else if(Serial.peek() == endMarker){
			Serial.print(char(startMarker));
			Serial.print("h");
			Serial.print(String(intern_hz));
			Serial.print(char(endMarker));
			return;
		} else {
			error('h');
			return;
		}
	}
	newHz = Serial.parseFloat();

	if(readByte() != endMarker){
		error('h');
		return;
	}

	if(newHz <= 0.0 || newHz >1000.0){
		error('h');
		return;
	}

	intern_hz = newHz;

	// on AVR a hardware timer, on other chips a software timer is used
	#ifndef __AVR__
		noInterrupts();
		double deltaT = (1.0/newHz);
		//ticks = deltaT * cpufreq / prescale
		long ticks = deltaT * 80000000. / 16.;


		timer1_attachInterrupt(onTimerISR);
		timer1_enable(TIM_DIV16, TIM_EDGE, TIM_SINGLE);
		timer1_write(ticks);
		timer_wait = ticks;
		interrupts();
	#else
		//unsigned long ticksproms = 600000/5;
		//long ticks = (1/hz)*1000 * ticksproms;
		double deltaT = (1.0/newHz);
		//ticks = deltaT * cpufreq / prescale
		long ticks = deltaT * 16000000. / 256.;

		//This Code is necessary for the timer
		noInterrupts();           // Alle Interrupts temporär abschalten
		TCCR1A = 0;
		TCCR1B = 0;
		TCNT1 = 0;                // Register mit 0 initialisieren
		OCR1A = ticks;            // Output Compare Register vorbelegen
		TCCR1B |= (1 << CS12);    // 256 als Prescale-Wert spezifizieren
		TIMSK1 |= (1 << OCIE1A);  // Timer Compare Interrupt aktivieren
		interrupts();             // alle Interrupts scharf schalten
	#endif

	//verifies the statement
	Serial.print(char(startMarker));
	Serial.print("h");
	Serial.print(String(intern_hz));
	Serial.print(char(endMarker));
}
