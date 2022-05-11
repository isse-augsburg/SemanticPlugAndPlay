import json
import socket
from subprocess import Popen
from time import sleep
from AbstractAdapter import AbstractAdapter


class EthernetAdapter(AbstractAdapter):
    def __init__(self, uri: str, port: int, pathToVirtualCapability: str):
        AbstractAdapter.__init__(self)
        self.port = port
        self.graph = uri
        self.dev_name = f"[EthernetAdapter] - {self.graph}"
        self.path = pathToVirtualCapability
        self.vCap = None
        self.socket: socket = None


    def execute_command_implementation(self, trigger_command: dict) -> None:
        if self.socket is None:
            self.format_print(f"Failed invoking command {trigger_command}")
            self.kill()
        else:
            self.send_message(trigger_command)

    def transmit_subcapability_response(self, command: dict):
        if self.socket is None:
            self.format_print(f"Failed transmitting command {command}")
            self.kill()
        else:
            self.send_message(command)

    def setup_implementation(self) -> bool:
        try:
            self.vCap = Popen(["python", self.path, str(self.port), self.graph])
        except Exception as e:
            self.format_print(f"Starting VCap resulted in Error: {repr(e)}")
            return False
        # Wait until the Server is runnning...
        # self.format_print(self.vCap.poll())
        sleep(1)
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect(("localhost", self.port))
            self.socket.settimeout(None)
        except OSError as e:
            self.format_print(f"Error -- {repr(e)} -- and stopped Virtual Capability")
            return False
        if self.socket is None:
            return False
        return True

    def loop(self):
        try:
            data = self.socket.recv(512)
            if data != b'':
                try:
                    self.message_received(data.decode())
                except Exception as e:
                    self.format_print(f"Some Error occured while receiving: {repr(e)}")
                    self.kill()
        except:
            print("error")
            self.socket.accept()

    def kill_implementation(self):
        self.format_print("Stopping")
        self.running = False
        if self.socket is not None:
            self.socket.send("kill".encode())
            self.socket.shutdown(socket.SHUT_RDWR)

    def send_message(self, msg: dict):
        if self.running:
            try:
                self.socket.send(json.dumps(msg).encode())
                #self.format_print(f"Sent Message {msg}")
                sleep(0.1)
            except BrokenPipeError as e:
                self.format_print(f"Connection Broken: {repr(e)}")
                self.kill()
        else:
            self.format_print(f"Trying to send {msg}, but Adapter is no longer running!")

    def message_received(self, received: str):
        #self.format_print(f"Received {received}, notifying {[a.graph for a in self.observers]}")
        self.notify(received)
