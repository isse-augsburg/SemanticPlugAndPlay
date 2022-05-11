import socket
import sys
import serial
import serial.tools.list_ports
import subprocess
from threading import Thread


class SemanticController(Thread):
    def __init__(self, ip, ser_port, rx_port, tx_port):
        # Sensor init
        Thread.__init__(self)
        self.running = True
        self.port_get = rx_port
        self.port_send = tx_port
        self.ip = ip
        try:
            self.ser = serial.Serial(
                port=ser_port,
                baudrate=250000,
                timeout=0.005
            )
        except Exception as e:
            print(e)
            print("OS forbids Serial Connectivity. Stupid OS....")
            self.running = False
        if self.running:
            print("[PYTHON]Internetadress: {}".format(ip))
            self.ser.read()
            self.sensorData = 0
            self.checksum_stack = []
            self.name = ser_port + "@" + ip

            # UDP init
            self.sock = socket.socket(socket.AF_INET,  # Internet
                                      socket.SOCK_DGRAM)  # UDP
            self.sock.bind((ip, self.port_get))
            self.sock.settimeout(.001)
            self.format_print("start")

    def format_print(self, string):
        self.sock.sendto(("[{}]".format(self.name) + string).encode("UTF-8"), (self.ip, self.port_send))
        print("[PYTHON]{}".format(string))

    def requestSensor(self):
        self.ser.write(b'<a1>')

    def sendString(self, string):
        checksum = 0
        self.ser.write(b'<b')
        self.ser.write(str(len(string)).encode('UTF-8'))
        self.ser.write(b':')
        for s in string:
            if self.readByte() == b'<':
                self.listen()
            if s == "<" or s == ">":
                self.ser.write("<".encode('UTF-8'))
            checksum += ord(s)
            checksum %= 1481
            self.ser.write(s.encode('UTF-8'))
        self.ser.write(b'>')
        self.checksum_stack += [checksum]

    def requestString(self, pos):
        self.ser.write(b'<c' + str(pos).encode('UTF-8') + b'>')

    def deleteString(self, pos):
        self.ser.write(b'<d' + str(pos).encode('UTF-8') + b'>')
        print(b'<d' + str(pos).encode('UTF-8') + b'>')

    def setRange(self, minRange, maxRange):
        self.ser.write(b'<r' + str(minRange).encode('UTF-8') + b':' + str(maxRange).encode('UTF-8') + b'>')

    def requestRange(self):
        self.ser.write(b'<r>')

    def writeToEEPROM(self):
        self.ser.write(b'<w>')

    def loadFromEEPROM(self):
        self.ser.write(b'<l>')

    def setNewHz(self, newHz):
        self.ser.write(b'<h' + str(newHz).encode('UTF-8') + b'>')

    def readByte(self):
        try:
            a = self.ser.read()
            if a == b'\x00':
                return b''
            else:
                return a
        except:
            self.kill()

    def readByteUntil(self, limiter):
        a = self.readByte()
        s = ""
        while a != limiter:
            if a == b'<':
                self.listen()
            s += a.decode()
            a = self.readByte()
        return s

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
                    self.listen()
                else:
                    a = b
            s += a.decode()
            a = self.readByte()
        return s

    def listen(self):
        byte = self.readByte()
        if byte == b'a':
            s = self.readByteUntil_fromString(b'>')
            # self.sensorData = int(s)
            self.format_print("SensorData: " + s)
        elif byte == b'<':
            self.listen()
            self.listen()
        elif byte == b'b':
            l = self.readByteUntil(b'>').split("@")
            old_checksum = self.checksum_stack.pop()
            if int(old_checksum) != int(l[0]):
                print(old_checksum, l[0])
                self.format_print("ERROR at sending string")
            else:
                self.format_print("Stored String with Checksum: {} at Adress: {}".format(l[0], l[1]))
        elif byte == b'c':
            s = self.readByteUntil_fromString(b'>')
            print(s)
            l = s.split(":")
            self.format_print("String at Adress: {} is '{}'".format(l[1], s.replace(":" + l[1] + ":", "")))
        elif byte == b'd':
            s = self.readByteUntil(b'>')
            self.format_print("deleted String at adress: " + s.split("d")[0])
        elif byte == b'e':
            self.format_print("Error" + self.readByteUntil(b'>'))
        elif byte == b'r':
            s = self.readByteUntil(b'>')
            l = s.split("r")[0].split(":")
            self.format_print("Range goes from {} to {}".format(l[0], l[1]))
        elif byte == b's':
            s = self.readByteUntil(b'>')
            if s == "0":
                self.format_print("Stream disabled...")
            else:
                self.format_print("Stream enabled...")
        elif byte == b'q':
            s = self.readByteUntil(b'>')
            self.format_print(s)
        elif byte == b'w':
            s = self.readByteUntil(b'>')
            self.format_print("Successfully written 'saved' strings to the EEPROM")
        elif byte == b'l':
            s = self.readByteUntil(b'>')
            self.format_print("Successfully loaded strings from the EEPROM")
        elif byte == b'h':
            s = self.readByteUntil(b'>')
            self.format_print("The new Hz is: {}".format(s))
        else:
            s = self.readByteUntil(b'>')
            self.format_print("Unknown command: " + s)

    def execCommand(self, s):
        print("[Python] Command received: " + s)
        try:
            command = s.split(" ")[0]
        except:
            self.format_print("Something went wrong... ")
            command = "help"
        if command == "sensor":
            print(("<a" + s.split(" ")[1] +  ">"))
            self.ser.write(("<a" + s.split(" ")[1] +  ">").encode("UTF-8"))
            #self.requestSensor()

        elif command == "stream":
            self.ser.write(("<s" + s.split(" ")[1] + ">").encode("UTF-8"))
        elif command == "save":
            try:
                self.sendString(s.replace("save ", ""))
            except:
                self.format_print("Command save threw an error.")
        elif command == "get":
            try:
                self.requestString(int(s.split(" ")[1]))
            except:
                self.format_print("Command get threw an error.")
        elif command == "del":
            try:
                self.deleteString(int(s.split(" ")[1]))
            except:
                self.format_print("Command del threw an error.")
        elif command == "range":
            try:
                self.setRange(int(s.split(" ")[1]), int(s.split(" ")[2]))
            except:
                self.requestRange()
        elif command == "hertz":
            try:
                self.ser.write(("<h" + s.split(" ")[1] + ">").encode("UTF-8"))
            except:
                print("Failed write EEPROM")
        elif command == "write":
            try:
                self.writeToEEPROM()
            except:
                print("Failed write EEPROM")
        elif command == "load":
            try:
                self.loadFromEEPROM()
            except:
                print("Failed load EEPROM")
        else:
            self.format_print("No Command: " + s)

    # FTPServer: "semantic.bplaced.net", 21, "semantic", "8E7SfpWSAUT7W6Jb", "example.json"
    def run(self):
        if not self.running:
            return
        data = b''
        print("running")

        self.java_subprocess = subprocess.Popen(
            ["java", "-jar", "PythonJavaBridge.jar", str(self.port_send), str(self.port_get), self.ip, "semantic.bplaced.net", str(21), "semantic", "8E7SfpWSAUT7W6Jb", "./example.json"])
        import sys, os
        pathname = os.path.dirname(sys.argv[0])        
        print('path =', pathname)
        print('full path =', os.path.abspath(pathname)) 
        #needed for Java to startup before Python closes itself
        #while self.running:
            #pass

        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                if not self.running:
                    break
                if data != "" and data != b'':
                    self.execCommand(data.decode())
            except:
                try:
                    b = self.readByte().decode()
                except:
                    break
                if not self.running:
                    break
                if b == "<":
                    self.listen()
        self.format_print("Closing")
        self.java_subprocess.kill()
        self.ser.close()
        self.sock.close()

    def kill(self):
        self.running = False


# ip, ser_port, rx_port, tx_port
#pythonJava = SemanticController(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
#pythonJava.run()
