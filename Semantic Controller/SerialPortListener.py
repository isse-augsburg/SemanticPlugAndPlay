import signal
import socket
import sys

import serial
import serial.tools.list_ports
import json

from AbstractAdapter import AbstractAdapter
from SPARQL.SPARQL import SPARQL_python_endpoint
from Observable import Observable
from Observer import Observer
from ArduinoAdapter import ArduinoAdapter
from threading import Thread
from time import sleep

from VirtualCapabilities.VirtualCapabilityFactory import VirtualCapabilityFactoryProvider


class NoConnectionException(Exception):
    pass


class ThinServer(Thread, Observable):

    def __init__(self, ip, port):
        Thread.__init__(self)
        self.observers = []
        self.running = True
        self.ip = ip
        self.port = port
        self.sock = None
        self.graph = "THINSERVER"
        # Mutex boolean
        self.sending = False
        print("[Server]Server running on Address: {}".format((self.ip, self.port)))

    def run(self) -> None:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp
            self.socket.bind((self.ip, self.port))
            self.socket.listen(1)
            self.sock, self.addr = self.socket.accept()
            # self.notify("NEW_CONNECTION")
            while self.running:
                try:
                    data = self.sock.recv(512)
                    if data != b'':
                        # print("[Server] received: " + str(data))
                        self.notify(data.decode())
                        #self.notify(data.decode())
                    else:
                        raise ConnectionResetError()
                except ConnectionResetError as _:
                    self.running = False
                    self.sock, self.addr = self.socket.accept()
                    # self.notify("NEW_CONNECTION")
                    self.running = True
                except Exception as e:
                    raise e
        except OSError as e:
            if (e.errno == 98):
                print(f"[Server] couldn't start because port is already used")
                raise KeyboardInterrupt()
            print(f"[Server] stopped: {repr(e)}")
        except Exception as e:
            raise e

    def sendMessage(self, string: str):
        while self.sending:
            pass
        self.sending = True
        try:
            if self.sock is not None:
                #print("[SERVER] Sending msg: " + string)
                self.sock.send(string.encode("UTF-8"))
            sleep(.002)
        except:
            self.running = False
            self.sock, self.addr = self.socket.accept()
            # self.notify("NEW_CONNECTION")
            self.running = True
        self.sending = False

    def kill(self):
        print("[Server] stopping now")
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)

    def detach(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def attach(self, observer: Observer) -> None:
        self.observers.append(observer)

    def notify(self, string: str) -> None:
        for observer in self.observers:
            observer.update(self, string)

    def notifyExternal(self, notifier, string: str):
        for observer in self.observers:
            observer.update(notifier, string)


class SerialPortListener(Observer):
    def __init__(self):
        # port, semanticController
        self.graph = "../Ontology/NewOntology.owl"
        self.list_of_opened_serial_ports = []
        self.list_of_adapter = []
        self.server = ThinServer(socket.gethostbyname("127.0.0.1"), 1500)
        self.server.start()
        self.server.attach(self)
        self.list_of_descriptions = []
        # self.sparql = sparql_endpoint("../SPARQL/CommandOntology.owl")
        self.sparql = SPARQL_python_endpoint(self.graph)
        self.sparql.controller = self
        self.sparql.attach(self)
        # self.sparql = SPARQL_python_endpoint("../Ontology/CommandOntology.owl")
        self.ports_not_to_use = []

    def run(self):

        while True:
            port_list = []
            ports = list(serial.tools.list_ports.comports())
            for p in ports:
                port_list += [p.__str__().split(" ")[0]]
            for i, p in enumerate(port_list):
                # Begins a Connection, if something is or was plugged in. only if it isn´t already open AKA in the python lists
                if (
                        "COM" in p or "USB" in p or "usb" in p) and p not in self.list_of_opened_serial_ports and p not in self.ports_not_to_use:
                    print("[SerialPortListener]trying to open Connection: Serial-Port={}".format(p))
                    sc = ArduinoAdapter(p)
                    sc.attach(self)
                    sc.controller = self
                    sc.start()
                    self.list_of_opened_serial_ports += [p]

            devices_to_remove = []
            # Check if an USB was removed. then kills the Process and removes from the list
            for i, opened_coms in enumerate(self.list_of_opened_serial_ports):
                if opened_coms not in port_list:
                    devices_to_remove += [opened_coms]

            for r_dev in devices_to_remove:
                for adapter in self.list_of_adapter:
                    if adapter.port == r_dev:
                        # remove dev_uris and its cap_urlis from sparql
                        self.sparql.current_devices.pop("commands:" + self.list_of_opened_serial_ports[r_dev].graph)
                        adapter.kill()
                        self.list_of_opened_serial_ports.pop(r_dev)
                        break
                # Calculate new Devices in Sparql
                for device_filled in self.sparql.onNewDeviceConnected():
                    self.server.sendMessage(json.dumps(device_filled))

    def update(self, observable: AbstractAdapter, string: str):
        if string == "" or string == None or string == " ":
            return
        string = string.replace("'", "\"")
        print("[SerialPortListener] UPDATE: " + string + " Source: " + str(observable.port))
        # Check string if json is correct.
        countopen = 0
        countclosed = 0
        for i, c in enumerate(string):
            if c == "{":
                countopen += 1
            elif c == "}":
                countclosed += 1
            if countopen == countclosed:
                #Check the next part
                self.update(observable, string[i + 1:])
                try:
                    # continue with first part
                    d = json.loads(string[:i + 1])
                    self.command_handler(d)
                except Exception as e:
                    print(f"No valid format: \n\nOriginal:{string}\n\nGot {string[:i + 1]}\n\nCause:\n\n{e}")
                    raise e
                # break the loop!
                break

    def command_handler(self, command: dict):
        d = command
        type = d["type"]

        if type == "blueprint":
            device_filled = self.sparql.translate_blueprint(d)
            self.server.sendMessage(json.dumps(device_filled))
        elif type == "trigger":
            # TODO !! Search for
            if "device" in d:
                requested_device = d["device"].replace("commands:", "")
                for adapter in self.list_of_adapter:
                        if requested_device in adapter.graph:
                            if d["capability"] in adapter.cap_uris:
                                adapter.execute_command(d)
            else:
                for adapter in self.list_of_adapter:
                    if d["capability"] in adapter.cap_uris:
                        adapter.execute_command(d)

        elif type == "response" or type == "device":
            if self.server.running and "ood-api" in d["src"]:
                self.server.sendMessage(json.dumps(command))
        elif type == "remdev":
            for bp in self.sparql.all_blueprints:
                if d["dev_req"] is bp["dev_props"]:
                    self.sparql.all_blueprints.remove(bp)
            self.sparql.all_blueprints = []
            d["type"] = "removed"
            self.server.sendMessage(json.dumps(d))
        elif type == "device":
            if self.server.running:
                self.server.sendMessage(json.dumps(command))
        else:
            raise Exception(f"Something went wrong: Command - {command}")

    def on_device_configured(self, configured_device: AbstractAdapter):
        print(f"[SERIALPORTLISTENER] Configured: {configured_device.graph}")
        self.sparql.current_devices["commands:" + configured_device.graph] = ["commands:" + cap for cap in
                                                                       configured_device.cap_uris]
        if configured_device not in self.list_of_adapter:
            self.list_of_adapter += [configured_device]
        # adding observers
        for adapter in self.list_of_adapter:
            for cap in adapter.cap_uris:
                if cap in configured_device.get_sub_caps():
                    adapter.attach(configured_device)

        self.sparql.recalculate_devices(configured_device)


    def start_virtual_capabilities(self, v_devices: dict):
        sys.stderr.write(f"[SerialPortListener] got some devices to start: {v_devices}")
        for v_dev in v_devices.keys():
            if (v_dev.replace("commands:", "") not in [ad.graph for ad in self.list_of_adapter]
                    and self.sparql.isVirtualDevice(v_dev)):
                git_address = self.sparql.get_git_repository(v_dev)
                print(f"[SerialPortListener] Starting {v_dev} from {git_address} in mode ethernet")
                adapter = VirtualCapabilityFactoryProvider().getVirtualCapability(v_dev.replace("commands:", ""),
                                                                                  git_address,
                                                                                  mode="ethernet")
                # TODO work on this quickfix (Make Factory use the right CapUris!)
                adapter.cap_uris = [cap.replace("commands:", "") for cap in v_devices[v_dev]]
                adapter.sub_caps = self.sparql.get_direct_subcaps(v_dev)
                adapter.attach(self)
                adapter.controller = self
                adapter.start()
                # Needed, The Factory takes time to get a recently opened Port as used right
                sleep(.5)

    def on_device_remove(self, adapter: AbstractAdapter):
        """
        Gets called when an adapter fails.

        :param adapter: the failing adapter
        :return: None
        """
        print(f"[SerialPortListener] {adapter.graph} on port {adapter.port} failed, deleting...")
        if adapter.__class__ is ArduinoAdapter.__class__:
            self.ports_not_to_use += [adapter.port]
        if adapter in self.list_of_adapter:
            self.list_of_adapter.remove(adapter)
        self.sparql.recalculate_devices(adapter)

    def check_cap_status(self, sub_cap: str) -> bool:
        for adapter in self.list_of_adapter:
            try:
                if sub_cap in adapter.cap_uris:
                    return adapter.running
            except:
                print(f"ADAPTER IS NONE!: {adapter}")
        return False

    def closing(self):
        print("[SerialPortListener] Closing...")
        for adapter in self.list_of_adapter:
            adapter.kill()
        self.server.kill()


if __name__ == "__main__":
    # Needed for properly closing when process is being stopped with SIGTERM signal
    def handler(signum, frame):
        print("[Main] Received SIGTERM signal")
        listener.closing()
        quit(1)


    listener = SerialPortListener()
    signal.signal(signal.SIGTERM, handler)
    try:
        listener.run()
    # Needed for properly closing, when program is being stopped wit a Keyboard Interrupt
    except KeyboardInterrupt:
        print("[Main] Received KeyboardInterrupt")
        listener.closing()
