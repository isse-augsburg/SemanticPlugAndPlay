import serial
import serial.tools.list_ports
import json
from threading import Thread
from time import sleep


import Observer
from Observable import Observable


class Adapter(Thread, Observable):

    def __init__(self, ser_port):
        # Sensor init
        Thread.__init__(self)
        self.running = True
        self.observers = []
        self.translations = {}
        self.port = ser_port
        #neeced for serial to start
        sleep(.5)
        self.dev_name = ["Unkown Device"]
        try:
            self.ser = serial.Serial(
                port=ser_port,
                baudrate=250000,
                timeout=0.005
            )
        except Exception as e:
            #print(e)
            self.format_print("OS forbids Serial Connectivity or Device doesn´t implement PythonComm, aborting...")
            self.running = False
            return
        if self.running:
            #empty Serial Puffer
            self.ser.read()
            self.sensorData = 0

    def attach(self, observer: Observer) -> None:
        self.observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def notify(self, string: str) -> None:
        for observer in self.observers:
            observer.update(self, string)

    def format_print(self, string):
        print("[{} on {}] {}".format(self.dev_name, self.port, string))
        #self.notify(string)

    def readByte(self):
        try:
            a = self.ser.read()
            while a == b'\x00':
                a = self.ser.read()
            return a
        except:
            self.kill()

    #Reads Bytes until limiter.
    #Doesn´t react to Escapes.
    def readByteUntil(self, limiter):
        a = self.readByte()
        s = ""
        while a != limiter:
            if a == b'<':
                self.listen()
            s += a.decode()
            a = self.readByte()
        return s

    #needed to rudimentairy communication, before listen
    #does react to escapes
    def readByteUntilOutsideListen(self, limiter):
        a = self.readByte()
        s = ""
        while a != limiter:
            if a == b'<':
                b = self.readByte()
                if b == b'<' or b == b'>':
                    s += b.decode()
            else:
                s += a.decode()
            a = self.readByte()
        return s

    # Reads Bytes until limiter.
    # Does react to Escapes.
    def readByteUntil_fromString(self, limiter):
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
            s += a.decode()
            a = self.readByte()
        return s

    def listen(self, firstByte=None):
        if firstByte != None:
            byte = firstByte
        else:
            byte = self.readByte()
        while byte == b'':
            byte = self.readByte()
        #print("new Byte: " + byte.decode())
        if byte == b'<':
            self.listen()
            self.listen()
        if byte != b'a':
            if byte == b's':
                help_str = self.readByteUntil_fromString(b'>')
                if help_str == "0":
                    self.format_print("Stream deactivated.")
                else:
                    for t in self.translations:
                        if help_str[0] == str(self.translations[t]["callback_number"]):
                            self.format_print("Will now Stream {} with following parameter: {}".format(t, str(help_str[2:].split(","))))
            elif byte == b'h':
                self.format_print("New Stream Rate in Hz: " + self.readByteUntil_fromString(b'>'))
            else:
                self.format_print("Not a CapCommand: byte:{}, rest: {}".format(byte.decode(), self.readByteUntil_fromString(b'>')))
            return

        help_str = self.readByteUntil_fromString(b'>')

        callback_nr = int(help_str.split(":")[0])
        help_str = help_str.replace(str(callback_nr) + ":", "")

        for vals in self.translations:
            if self.translations[vals]["callback_number"] is callback_nr:
                param_values = help_str.split(",")
                param_names = self.translations[vals]["receive"].replace(" ", "").split(",")
                param_names_replace = self.translations[vals]["answer"].split("(")[1].replace(")", "").replace(" ", "").split(",")

                #for debugging
                #self.format_print("vals: " + str(param_values))
                #self.format_print("names: " + str(param_names))
                #self.format_print("replace: " + str(param_names_replace))

                send = self.translations[vals]["answer"].split("(")[0] + "("
                for p, rep_str in enumerate(param_names_replace):
                    for l, string in enumerate(param_names):
                        #self.format_print(rep_str + "   " + string)
                        if rep_str == string:
                            send += param_values[l] + ","
                            #self.format_print("send: " + send)
                send = send[:-1]
                send += ")"
                self.notify(send)

    def execCommand(self, s):
        self.format_print("Command to be worked on: " + s)
        try:
            #get the command without params to compare with the translation Table
            command = s.split("(")[0]
        except:
            command = "help"

        for tran in self.translations.keys():
            if command == tran.split("(")[0]:
                #get Parameter. One time the exact values from the command, then the parameter names parsed from the translation
                #get rid of " "
                param_values = s.split("(")[1].split(")!")[0].replace(")", "").replace(" ,", ",").replace(", ", ",").split(",")
                param_names = tran.split("(")[1].replace(")", "").replace(" ", "").split(",")
                #self.format_print("param names: " + str(param_names))
                #self.format_print("param vals: " + str(param_values))
                # See if the command implies a stream open. try because maybe this can´t be split
                try:
                    streaming = s.split(")")[-1][0] == '!'
                except:
                    streaming = False

                # Escape the flags
                to_send = self.translations[tran]["send"].replace("<", "<<").replace(">", "<>")
                # Replace Params with the given values form command.
                for p in range(len(param_names)):
                    #self.format_print("replace: " + str(param_names[p]) + str(param_values[p]))
                    to_send = to_send.replace(str(param_names[p]), str(param_values[p]))

                #self.format_print("tosend: " + to_send)
                if streaming:
                    #self.format_print("Streaming: " + str(streaming))
                    #self.format_print("Hz: " + s.split(")!")[-1])
                    hertz = float(s.split(")!")[-1])
                    if hertz > 0.0:
                        self.ser.write("<h{}>".format(hertz).encode("UTF-8"))
                        self.ser.write(
                            ("<s" + str(self.translations[tran]["callback_number"]) + ":" + to_send + ">").encode(
                                "UTF-8"))
                    else:
                        self.ser.write("<s>".encode("UTF-8"))

                else:
                    self.ser.write(("<a" + str(self.translations[tran]["callback_number"]) + ":" + to_send + ">").encode("UTF-8"))

    def getEEPROMdata(self, string_location: int):
        # needed because it takes time to load from eeprom...
        while self.readByte() == b'':
            self.ser.write(b'<l>')
            pass
        b = self.readByteUntilOutsideListen(b'>')
        self.ser.write(("<c" + str(string_location) + ">").encode("UTF-8"))
        while self.readByte() != b'c':
            pass
        s = self.readByteUntilOutsideListen(b'>')
        string = s.replace(":"+ str(string_location) + ":", "")
        return string

    # FTPServer: "semantic.bplaced.net", 21, "semantic", "8E7SfpWSAUT7W6Jb", "example.json"
    def run(self):
        if not self.running:
            return
        data = b''
        try:
            rdf_path = self.getEEPROMdata(0).replace(" ", "")
            self.dev_name = rdf_path.split(",")
        except:
            rdf_path = ""

        self.format_print("Device Name: " + rdf_path)

        try:
            json_trans = self.getEEPROMdata(1)
        except:
            json_trans = ""

        # The json trans is normally saved on the EEPROM on virt. Address 1.
        # But it doesnt have to be there, it can be generated by RDF-Data otherwise.
        if json_trans is not "":
            self.format_print("json translation available.")
            self.translations = json.loads(json_trans.replace("'", "\""))
            self.notify("rdf translation_avaiable " + rdf_path)
        else:
            self.format_print("json translation not available, generating it from RDF...")
            self.notify("rdf translation_not_avaiable " + rdf_path)

            # Wait until [SerialPortListener] gets translation from [sparql_endpoint] via SerialPortListener
            while not self.translations:
                pass

        self.format_print("Working with Translations: " + str(self.translations))
        self.format_print("Configuration done, running..")
        while self.running:
            try:
                b = self.readByte().decode()

            except:
                break
            if not self.running:
                break
            if b == "<":
                self.listen()
        self.format_print("Closing")
        self.ser.close()

    def kill(self):
        self.running = False