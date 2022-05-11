import json
import socket
from time import sleep
from AbstractAdapter import AbstractAdapter


class DockerAdapter(AbstractAdapter):
    def __init__(self, uri: str, port: int, container: any):
        AbstractAdapter.__init__(self)
        self.port = port
        self.graph = uri
        self.dev_name = f"[DockerAdapter] - {self.graph}"
        self.container = container
        try:
            sleep(0.5)
            self.running = True
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(("localhost", self.port))
        except OSError as e:
            self.format_print(f"Error -- {repr(e)} -- and stopped Virtual Capability")
            self.running = False
            self.connected = False
            self.format_print("Stopping")

    def execute_command_implementation(self, trigger_command: dict) -> None:
        self.send_message(trigger_command)

    def transmit_subcapability_response(self, command: dict):
        self.send_message(command)

    def loop(self):
        try:
            data = self.socket.recv(512)
            if data != b'':
                try:
                    self.message_received(data.decode())
                except Exception as e:
                    self.format_print(f"Some Error was received {repr(e)}")
                    self.socket.send("Error".encode())
        except:
            self.socket.accept()

    def kill_implementation(self):
        self.format_print("Stopping")
        self.running = False
        self.socket.send("kill".encode())
        self.socket.shutdown(socket.SHUT_RDWR)

    def send_message(self, msg: dict):
        if self.running:
            try:
                self.socket.send(json.dumps(msg).encode())
                sleep(0.1)
            except BrokenPipeError as e:
                self.format_print(f"Connection Broken: {repr(e)}")
                self.kill()
        else:
            self.format_print(f"Trying to send {msg}, but Adapter is no longer running!")

    def message_received(self, received: str):
        self.format_print(f"Received {received}")
        self.notify(received)
