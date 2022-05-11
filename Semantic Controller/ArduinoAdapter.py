import sys
import time

import serial
import serial
import serial.tools.list_ports
import json
from time import sleep
from AbstractAdapter import AbstractAdapter


class ArduinoAdapter(AbstractAdapter):

    def __init__(self, ser_port):
        # Sensor init
        AbstractAdapter.__init__(self)
        self.port = ser_port
        # neeced for serial to start
        self.ser = None
        self.srcCounter = 0
        self.srcMap = dict()

    def readByte(self):
        try:
            a = self.ser.read()
            while a == b'\x00':
                print(a.decode())
                a = self.ser.read()
            #if a != b'':
                #self.format_print(a)
            return a
        except:
            self.kill()

    # Reads Bytes until limiter.
    # Does react to Escapes.
    def readByteUntilEscaping(self, limiter):
        a = self.readByte()
        s = ""
        while a != limiter:
            if a == b'<':
                b = self.readByte()
                if b.decode() != "<" and b.decode() != ">":
                    self.listen(b)
                    a = b''
                else:
                    a = b
            try:
                s += a.decode()
            except:
                pass
            a = self.readByte()
        return s

    def listen(self, firstByte=None):
        #self.format_print("Invoke listen")
        if firstByte != None:
            byte = firstByte
        else:
            byte = self.readByte()
        if byte == b'<':
            self.listen()
            self.listen()
        elif byte == b'a':
            src = self.readByteUntilEscaping(b':')
            uri_cap = self.readByteUntilEscaping(b':')
            params = self.readByteUntilEscaping(b'>')[:-1].split(":")
            #self.format_print("URICAP: " + uri_cap)
            #self.format_print("PARAMS: " + str(params))
            ret = {}
            try:
                ret["src"] = self.srcMap[int(src)]
            except:
                self.format_print(f"{self.srcMap}  vs  {src}")
                ret["src"] = str(src)
            ret["type"] = "response"
            ret["capability"] = uri_cap
            param_list = dict()
            i = 0
            try:
                while i < len(params):
                    param_list[params[i]] = params[i + 1]
                    i += 2
            except:
                raise Exception("Device is falsely built! Use always ParameterToString!")
            ret["parameters"] = param_list
            #self.format_print(f"Notifying: {ret}")
            self.notify(json.dumps(ret))
        elif byte == b'c':
            h = self.readByteUntilEscaping(b':')
            h = self.readByteUntilEscaping(b':')
            storedData = self.readByteUntilEscaping(b'>')
            if (h == "0"):
                self.graph = storedData
                self.dev_name = storedData
            self.format_print("Received String {} at Adress {}".format(storedData, h))
        elif byte == b't':
            h = self.readByteUntilEscaping(b':')
            h = self.readByteUntilEscaping(b'>')
            self.cap_uris = h.split(",")
            self.sub_caps = {cap: [] for cap in self.cap_uris}
            self.format_print("Received Cap URIS: " + str(self.cap_uris))
        elif byte == b'k':
            h = self.readByteUntilEscaping(b':')
            h = self.readByteUntilEscaping(b'>')
            self.dynamix = h.split(",")
            self.format_print("Received Dynamix URIS: " + str(self.dynamix))
        elif byte == b'h':
            self.format_print("New Stream Rate in Hz: " + self.readByteUntilEscaping(b'>'))
        elif byte == b'e':
            self.format_print("Some Error has occured: " + self.readByteUntilEscaping(b'>'))
        elif byte == b'l':
            self.format_print("Loading EEPROM...")
            self.readByteUntilEscaping(b'>')
        else:
            pass
            #self.format_print("Not defined: " + byte.decode() + self.readByteUntilEscaping(b'>'))

    def execute_command_implementation(self, trigger_command: dict) -> None:
        #self.format_print("Working on command {}".format(trigger_command))
        newSrc = self.srcCounter
        self.srcCounter += 1
        self.srcMap[newSrc] = trigger_command["src"]

        s = ""
        for p in trigger_command["parameters"]:
            s += str(p) + ":" + str(trigger_command["parameters"][p])

        if trigger_command.get("streaming") > 0.0:
            self.ser.write(
                "<s{}:{}:{}>".format(newSrc, trigger_command["capability"], s).encode("UTF-8"))
            self.ser.write(("<h{}>".format(trigger_command["streaming"]).encode("UTF-8")))
        elif trigger_command.get("streaming") < 0.0:
            self.ser.write(("<s>".encode("UTF-8")))
        elif int(trigger_command.get("streaming")) == 0:
            self.ser.write(
                "<a{}:{}:{}>".format(newSrc, trigger_command["capability"], s).encode("UTF-8"))
            # self.format_print("COMMAND: " + "<a{}:{}:{}>".format(newSrc, trigger_command["capability"], s))

    def transmit_subcapability_response(self, command: dict):
        pass

    def setup_implementation(self) -> bool:
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=115200,
                timeout=0.005
            )
        except Exception as e:
            sys.stderr.write(f"OS forbids Serial Connectivity (Port: {self.port}) or Device doesn't implement "
                             f"PythonComm, aborting. Errorcode: {e}")
            return False
        sleep(.5)
        self.ser.read()
        sleep(2)
        # Load from EEPROM //NO LONGER NEEDED
        # self.ser.write(b'<l>')
        # Get all Capability URIs
        self.ser.write(b'<t>')
        # Get all Dynamix
        self.ser.write(b'<k>')
        # Get device URI
        self.ser.write(b'<c0>')
        # Wait till it´s filled (look @listen())
        while self.cap_uris is None or self.graph is None or self.dynamix is None:
            b = ""
            try:
                b = self.readByte().decode()
            except:
                pass
            if b == "<":
                self.listen()
        return True

    def loop(self):
        try:
            b = self.readByte().decode()
        except:
            return
        if b == "<":
            self.listen()

    def kill_implementation(self):
        self.running = False
        self.format_print("Closing")
        self.ser.close()
