import socket
import serial
import serial.tools.list_ports
from SemanticController import SemanticController
from threading import Thread

udp_port = 1500
port_begin = 1400
port_end = 2000
list_of_SemanticController = []
ser_ports_already_running = []
udp_ports_already_running = []
python_java_already_running = []

sock = socket.socket(socket.AF_INET,  # Internet
                                      socket.SOCK_DGRAM)  # UDP
sock.bind((socket.gethostname(), udp_port))
sock.settimeout(.001)

while True:
    port_list = []
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        port_list += [p.__str__().split(" ")[0]]
    for i, p in enumerate(port_list):
        #print(i, ": ", p)
        # Begins a Connection, if something is or was plugged in. only if it isn´t already open AKA in the python lists
        if ("COM" in p or "USB" in p or "usb" in p) and port_begin + 2 <= port_end and p not in ser_ports_already_running:
            print("Opening Connection... \nSerial-Port={} \nRxPort={} \nTxPort={}".format(p, port_begin,
                                                                                          port_begin + 1))
            #r_comm = RudimentaryCommunication(p)

            #print("http_uri= " + r_comm.getHTTPURI())
            sc = SemanticController(socket.gethostbyname(socket.gethostname()), p, port_begin, port_begin+1)
            #subprocess.Popen(["python", "SemanticController.py", socket.gethostbyname(socket.gethostname()), p, str(port_begin),
            #                 str(port_begin + 1)])
            sc.start()
            list_of_SemanticController += [sc]
            port_begin += 2
            ser_ports_already_running += [p]


    '''
    continue
    # look for devices in the network
    for i in range(2001, 2050, 1):
        if i not in udp_ports_already_running:
            # print(i)
            # print(udp_ports_already_running)
            sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
            sock.settimeout(.01)
            sock.bind((socket.gethostname(), i))
            try:
                data, address = sock.recvfrom(1024)
                print(data, address)
                if data == b'OrangePi::start':
                    sock.sendto("SensorPythonJava::start".encode("UTF-8"), (address))
                    data, address_check = sock.recvfrom(1024)
                    while data == b'OrangePi::start' or address_check != address:
                        data, address_check = sock.recv(1024)
                    server, port, user, password, fileLocation = data.decode().split(" ")
                    sock.shutdown(0)
                    sock.close()
                    print("Opening Connection... \nIP-Adress={} \nUDPPort={}".format(address[0], i))

                    java_subprocess = subprocess.Popen(
                        ["java", "-jar", "PythonJavaBridge.jar", str(i), str(i), str(address[0]), str(address[0]),
                         server, str(port), user, password, fileLocation])

                    udp_ports_already_running += [i]

            except Exception as e:
                # print("EXCEPTION OCCURED: ")
                # print(e)
                sock.close()
    '''

    # Check if an USB was removed. then kills the Process and removes from the list
    for i, opened_coms in enumerate(ser_ports_already_running):
        if opened_coms not in port_list:
            ser_ports_already_running.remove(opened_coms)

    # Check if an UDP was removed. then kills the Process and removes from the list
    for i, opened_ports in enumerate(udp_ports_already_running):
        # @TODO here a sufficient condition
        if False:
            udp_ports_already_running.remove(opened_ports)





