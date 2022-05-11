import json
import time
from abc import abstractmethod
from threading import Thread
from Observer import Observer
from Observable import Observable


class AdapterTimeoutException(Exception):
    pass


class AbstractAdapter(Thread, Observable, Observer):
    """ A SemanticAdapter interface

    Provides basic necessities and some functions
    """

    def __init__(self):
        """ Starts the SemanticAdapter

        Starts the Thread.
        :rtype: object the initiated object
        """
        Thread.__init__(self, daemon=True)
        Observable.__init__(self)
        self.running = False
        # Semantic Adapter Controller
        self.controller = None
        # List of Observers
        self.observers = []
        # The Port (either Serial Port or TCP)
        self.port = None
        # List of Uris from implemented Capabilities
        self.cap_uris: list = None
        # List of Dynamic Properties
        self.dynamix = None
        # The name of the device
        self.dev_name = ["Unkown Device"]
        # This is "just" the URI
        self.graph = None
        # SubCapabilities. Example: {'SearchGridGetNextPosition': ['GetISSECopterPosition', 'GetTestFieldBoundaries']}
        self.sub_caps = {}

    # DO NOT OVERRIDE!!!
    def run(self):
        """!DO NOT OVERRIDE!

        The Thread run function. should be kill-able with ''kill''
        """
        self.setup()
        if self.running:
            self.format_print("Configuration done")
            while self.running:
                self.loop()
        else:
            self.format_print(f"ERROR: {self.graph} could not be started")
        self.controller.on_device_remove(self)
        e =  Exception(f"Capability {self.graph} on port {self.port} ended {not self.running}ly...")

    def attach(self, observer: Observer) -> None:
        if observer not in self.observers:
            self.observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self.observers.remove(observer)

    def notify(self, string: str) -> None:
        for observer in self.observers:
            observer.update(self, string)

    def get_sub_caps(self) -> list:
        ret = set()
        for key, value in self.sub_caps.items():
            if value != None:
                for sub_cap in value:
                    ret.add(sub_cap)
        return list(ret)

    def format_print(self, string) -> str:
        """ Prints better, tells where something comes from

        :param string: The things to print
        """
        toPrint = f"[{self.dev_name} on {self.port}] {string}"
        print(toPrint)
        return toPrint

    # @abstractmethod
    def update(self, observable: Observable, string: str) -> None:
        """ React to Input from the sub Capabilities

        :param observable: The Device which manages sub capability
        :param string: the content. Is a dict

        {'SearchGridGetNextPosition': {'commands:GetISSECopterPosition': None, 'commands:GetTestFieldBoundaries': None}}
        """

        #self.format_print(f"Update from {observable.graph}: {string}")
        d = json.loads(string.replace("'", "\""))
        # Transitive trigger commands shall not invoke superDevices
        if d["type"] == "response" and d["capability"] in self.get_sub_caps():
            self.transmit_subcapability_response(d)

    # DO NOT OVERRIDE!!!
    def execute_command(self, trigger_command: dict) -> None:
        """ Executes a command !DO NOT OVERRIDE!

        This function is called if a specific capability is triggered from outside.
        The Implementation should gather all needed information and invoke the actual (Arduino/Docker) functions.

        :param trigger_command: The Command with information, like parameters and src
        """
        if(trigger_command["type"] == "trigger") and trigger_command["capability"] in self.cap_uris:
            cap = trigger_command.get("capability")
            params = trigger_command.get("parameters")
            #self.format_print(f"Executing {cap} with parameter: {params}")
            self.execute_command_implementation(trigger_command)
        else:
            self.format_print(f"Unkown Command: {trigger_command}")

    @abstractmethod
    def transmit_subcapability_response(self, command: dict):
        """
        This method transmits a response from a previously invoked capability to the actual Device
        :param command: The response from the sub capability
        :return: None
        """
        raise NotImplementedError

    @abstractmethod
    def execute_command_implementation(self, trigger_command: dict):
        """
        Here goes the implementation in the subclasses
        :return: None
        """
        pass

    def setup(self):
        """Setup before the loop

        Here the implementation of the setup takes place
        """
        # check if subcaps are needed
        self.running = self.setup_implementation()
        if self.running:
            sub_class_init = False or all([len(self.sub_caps[cap]) == 0 for cap in self.cap_uris])
            # wait until all subcaps are present
            while not sub_class_init:
                sub_class_init = True
                for cap in self.cap_uris:
                    for sub_cap in self.sub_caps[cap]:
                        sub_class_init &= self.controller.check_cap_status(sub_cap)
                time.sleep(.1)
            self.controller.on_device_configured(self)

    @abstractmethod
    def setup_implementation(self) -> bool:
        """
        Special Setup for specific adapter

        :return: success
        """
        raise NotImplementedError

    @abstractmethod
    def loop(self):
        """The main running loop inside a specific adapter

        This method gets called repeatedly
        """
        raise NotImplementedError

    def kill(self):
        """Kill the thread, remove residues

        """
        self.kill_implementation()
        self.controller.on_device_remove(self)

    @abstractmethod
    def kill_implementation(self):
        """
        Kill the thread, remove residues
        """
        raise NotImplementedError

