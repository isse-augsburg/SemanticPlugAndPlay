import rdflib
from SPARQL import StringArithmetics


# @TODO here multiple Devices.
class sparql_endpoint:
    def __init__(self, uri: str):
        # @TODO This is a bit hacky, since rdflib takes the absolute PATH, and this can be joined with the absolute Path provided by uri...
        self.json_translation_cnr = 0

        self.sparql = rdflib.Graph()
        self.format_print("Parsing Uri: " + uri)
        self.sparql.parse(uri)

        # determine all devices described
        self.all_devices_in_Ontology = []
        res = self.sparql.query("SELECT ?devs WHERE{ ?devs rdf:type commands:Device .}")
        for i, a in enumerate(res):
            for j, b in enumerate(a):
                self.all_devices_in_Ontology += [b.split("/")[-1].replace("#", ":")]
        print("[SPARQL]All devices in SPARQL: " + str(self.all_devices_in_Ontology))

        self.json_translation_callback_nrs = []

        # Map devive URI to it´s Capabilities -> "uri"->["cap1uri", "cap2uri"]
        self.current_devices = {}
        self.all_blueprints = []

    @DeprecationWarning
    def getJsonTranslation(self, dev_names: list) -> dict:
        '''Create a JSON-translation. Remember, more than one device can exist foreach Semantic Adapter
        :param dev_names:
        :return:
        '''
        dev_names = ["commands:" + d for d in dev_names]
        for dev_name in dev_names:
            if dev_name not in self.all_devices_in_Ontology:
                print("[SPARQL] " + dev_name + " is not in that list.")
                return None

        list_of_all_caps = []

        for device in dev_names:
            # CAPS
            res = self.sparql.query(
                "SELECT ?a WHERE{{ {} commands:hasCapability ?a . ?a rdf:type commands:Capability.}}".format(device))
            cap_uris = []
            for i, a in enumerate(res):
                for j, b in enumerate(a):
                    cap_uris += [b.split("/")[-1].replace("#", ":")]
            for cap in cap_uris:
                list_of_all_caps += [self.__parseCapabilityFromCapName(cap)]

        json_translation = {}
        # Creating the json_translation table
        for cap in list_of_all_caps:
            first_dict_key = cap["sendCommand"]["message"]
            json_translation[first_dict_key] = {"callback_number": self.json_translation_cnr}
            self.json_translation_cnr += 1

            # helper_string
            field = ""
            for a in cap["sendCommand"]["variables"]:
                field += a["key"] + ","
            field = field[:-1]
            json_translation[first_dict_key]["send"] = field

            try:  # If there is no receiveCommand, can happen. sendCommand is always there
                field = ""
                for a in cap["receiveCommand"]["variables"]:
                    field += a["key"] + ","
                field = field[:-1]
                json_translation[first_dict_key]["receive"] = field
                json_translation[first_dict_key]["answer"] = cap["receiveCommand"]["message"]

            except Exception as e:
                json_translation[first_dict_key]["receive"] = ""
                json_translation[first_dict_key]["answer"] = ""

        self.format_print("Successfully created JSON-Translation, sending json-files to [SerialPortListener]..")
        return json_translation


    def onNewDeviceConnected(self)->list:
        '''
        CAUTION
        '''
        rets = []
        for bp in self.all_blueprints:
            rets += [self.getJsonDictFromBlueprint(bp)]
        return rets


    # Matching. aka Brainfuck blueprint=query/requirement, threshhold=??
    def getJsonDictFromBlueprint(self, blueprint: dict, threshhold: float = 0.25):
        self.format_print("Starting decrypting device: {}".format(blueprint))
        if blueprint not in self.all_blueprints:
            self.all_blueprints += [blueprint]
        ret = {}
        ret["src"] = blueprint["src"]
        ret["type"] = "device"
        queryDevProperties = blueprint["dev_props"]
        queryCapProperties = blueprint["capabilities"]
        # physical device is meant. First check deviceProperties than check CapabilityProperties
        if len(queryDevProperties) > 0:
            self.format_print(
                "Parsing whole phyical device from properties: {} and cap properties: {}".format(queryDevProperties,
                                                                                                 queryCapProperties))

            # Current highest dev_confidence/match
            device_match_value = 0
            # current Selected/matched device (device with greatest dev_confidence)
            final_selected_device = ""
            final_selected_capabilities = []

            for adjacentDevice in self.current_devices.keys():
                # Calculate Distance between Properties we want and Properties we have
                #TODO include dynamix
                dev_confidence = StringArithmetics.calculate_string_array_similarity(queryDevProperties,
                                                                                     self.getSimplePropertyList(
                                                                                      adjacentDevice))
                # No specific Caps requested, taking "natural" caps from device
                if len(queryCapProperties) is 0:
                    current_selected_capabilities = self.getCapabilityNames(adjacentDevice)
                    cap_confidence = 1.
                else:

                    # Get the Capability which are described by the SPARQL and are in the semantic adapter
                    cap_actual = list(set.intersection(set(self.getCapabilityNames(adjacentDevice)), set(self.current_devices[adjacentDevice])))

                    cap_confidence, current_selected_capabilities = self.selectCapabilities(
                        cap_requirements=queryCapProperties, cap_actual=cap_actual,
                        threshhold=threshhold)
                    # Cap not found...
                    if cap_confidence == 0:
                        dev_confidence = 0.

                # Recalculating dev_confidence
                dev_confidence = float(dev_confidence + cap_confidence) / 2.
                # Print foreach existing device
                self.format_print(
                    "[{}] properties: ({}...), matchvalue={}, from dev_requirement={} | Caps: {} from cap_requirement: {}, Capmatchvalue={}".format(
                        adjacentDevice.replace("commands:", ""), self.getSimplePropertyList(adjacentDevice)[:2],
                        dev_confidence, queryDevProperties, current_selected_capabilities, queryCapProperties,
                        cap_confidence))

                # Look for best Match
                if dev_confidence > device_match_value and dev_confidence > threshhold:
                    # found a new device with greater match
                    final_selected_device = adjacentDevice
                    device_match_value = dev_confidence
                    final_selected_capabilities = current_selected_capabilities

            self.format_print(
                "Device properties {} has matched with actual Device {}. Capabilities used: {} (from cap requirements: {}). Matchvalue: {}".format(
                    queryDevProperties, final_selected_device, final_selected_capabilities, queryCapProperties,
                    device_match_value))

            # No match found
            if final_selected_device is "":
                ret["json"] = {}
                return ret
            ret["json"] = self.parseDeviceFromNameAndCaps(final_selected_device, final_selected_capabilities)
        # Just query from all current capabilitities to construct a virtual device
        else:
            self.format_print("Creating a virtual Device from requirements: {}".format(queryCapProperties))
            list_of_all_caps = []
            for dev in self.current_devices.keys():
                cap_actual = list(set.intersection(set(self.getCapabilityNames(dev)),
                                                   set(self.current_devices[dev])))
                list_of_all_caps += cap_actual

            cap_confidence, final_selected_capabilities = self.selectCapabilities(queryCapProperties, list_of_all_caps,
                                                                                  threshhold=threshhold)

            self.format_print("Capability Properties {} have matched with Capabilities: {}, confidence is: {}".format(
                queryCapProperties, final_selected_capabilities, cap_confidence))
            ret["json"] = self.parseDeviceFromNameAndCaps("", final_selected_capabilities)

        if "json" in ret.keys():
            ret["json"]["requirements"] = queryDevProperties
            if len(queryCapProperties) > 0:
                for i, c in enumerate(ret["json"]["capabilities"]):
                    c["requirements"] = queryCapProperties[i]
        return ret

    def selectCapabilities(self, cap_requirements: list, cap_actual: list, threshhold: float) -> (float, list):
        """Selects Capabilities according to requirements
        Selects capabilities from a list of requirements. Returns normed confidence and list of capnames

        :param cap_requirements: a list of strings
        :param cap_actual: a list of cap-uris
        :param threshhold: a float, the minimum the string matching should have
        :return: the confidence, a list of uris of the selected caps
        """
        self.format_print(
            "Selecting capabilities based on: {}, from list of capabilities: {}".format(cap_requirements, cap_actual))
        final_cap_confidence = 0
        selected_capabilities = []

        # For each Capability we want we search an actual Capability with the greatest Match value(=capability_match_value)
        for qCap in cap_requirements:
            capability_match_value = 0
            best_capability_match = None
            for aCap in cap_actual:
                # already selected this capability @TODO This is Firstfit, maybe another strategy is more convenient
                # Maybe We want several times the same cap
                if aCap not in selected_capabilities:
                    cap_confidence = StringArithmetics.calculate_string_array_similarity(qCap,
                                                                                         self.getSimplePropertyList(aCap),
                                                                                         level_of_wrongness=0.4)
                    # self.format_print("Current Confidence={} ({})".format(cap_confidence, aCap))
                    # Found a better matching capability
                    if cap_confidence > capability_match_value and cap_confidence > threshhold:
                        capability_match_value = cap_confidence
                        best_capability_match = aCap

            # Capability couldn´t be matched/found
            if capability_match_value is 0:
                return 0, []
            # Found a cap, adding it to return value
            else:
                final_cap_confidence += capability_match_value
                selected_capabilities += [best_capability_match]

        # @TODO maybe a better solution to determine value of cap-matching
        return final_cap_confidence / float(len(cap_requirements)), selected_capabilities

    def getSimplePropertyList(self, thing) -> list:
        '''Helper to extract strings from the properties

            Queries all the Properties from am Command:Thing (Like a Device, Capability, Variable....)
            :param thing: the URI to be queried.
            :return: a list of strings.
        '''
        # add URI to simple property
        ret_list = [thing.replace("commands:", "")]
        res = self.sparql.query(
            "SELECT ?name ?description WHERE{{ {} rdfs:label ?name . {} rdfs:comment ?description.}}".format(thing,
                                                                                                             thing))
        name = "None"
        description = "None"
        for i, a in enumerate(res):
            for j, b in enumerate(a):
                # print(b)
                if j is 0:
                    name = b.split("/")[-1].replace("#", ":")
                elif j is 1:
                    description = b.split("/")[-1].replace("#", ":")

        ret_list += [name]
        # ret_list += [description]

        res = self.sparql.query(
            "SELECT ?prop WHERE{{ {} commands:hasProperty ?prop .}}".format(thing))
        properties = []
        for i, a in enumerate(res):
            for j, b in enumerate(a):
                if j is 0:
                    properties += [b.split("/")[-1].replace("#", ":")]
        for prop in properties:
            name = "None"
            desc = "None"
            res = self.sparql.query(
                "SELECT DISTINCT ?name ?des WHERE{{ {} rdfs:label ?name . {} rdfs:comment ?des}}".format(prop, prop))
            for i, a in enumerate(res):
                for j, b in enumerate(a):
                    if j is 0:
                        name = b.split("/")[-1].replace("#", ":")
                    if j is 1:
                        desc = b.split("/")[-1].replace("#", ":")
            res = self.sparql.query(
                "SELECT DISTINCT ?a WHERE{{ {} commands:propertyContent ?a .}}".format(prop))
            obj = {}
            for i, a in enumerate(res):
                for j, b in enumerate(a):
                    obj = b.split("/")[-1].replace("#", ":")

            # @TODO try to find out valueType
            ret_list += [name]
            # ret_list += [desc]
            ret_list += [obj]
        return ret_list

    def getCapabilityNames(self, deviceName) -> list:
        '''Get Capability URIs from a device

            Important to use the device URI here.
            :param deviceName: the URI of the device
            :return: a list of URIS (strings) from capabilities
        '''
        # CAPS
        res = self.sparql.query(
            "SELECT ?a WHERE{{ {} commands:hasCapability ?a . ?a rdf:type commands:Capability.}}".format(deviceName))
        caps = []
        for i, a in enumerate(res):
            for j, b in enumerate(a):
                caps += [b.split("/")[-1].replace("#", ":")]
        return caps

    def parseDeviceFromNameAndCaps(self, devname: str, capnames: list):
        '''Creates a json/dict which is used to instantiate devices in the ood-api

           :param devname: is the uri of the device, from which the device properties come from
           :param capnames: are the uri of the capabilities
           :return: a dict/json for a Device
        '''
        # @TODO Here we should doublecheck if the device has these caps
        cancer = {}
        cancer["properties"] = []
        cancer["capabilities"] = []

        if devname is not "" and devname is not None:
            cancer["properties"] += self.__parsePropertiesFromThing(devname)

        # CAPS
        for cap in capnames:
            cap_dict = self.__parseCapabilityFromCapName(cap)
            cancer["capabilities"] += [cap_dict]

        return cancer

    def __parseCapabilityFromCapName(self, cap):
        '''creates a json/dict for a capability

            Gets called by @parseDeviceFromNameAndCaps
        :param cap: an URI of a thing
        :return: a dict/json as representation of a Capability in OOD-API
        '''
        ret_list = {}
        ret_list["properties"] = self.__parsePropertiesFromThing(cap)
        # get Commands
        res = self.sparql.query(
            "SELECT ?a WHERE{{ {} commands:hasCommand ?a . ?a rdf:type commands:Command.}}".format(cap))
        comms = []
        for i, a in enumerate(res):
            for j, b in enumerate(a):
                comms += [b.split("/")[-1].replace("#", ":")]

        # get Variables for each command. Command can be receive or transmit
        for com in comms:
            # Variables.
            res = self.sparql.query(
                "SELECT ?var ?val ?key WHERE{{ {} commands:hasVariables ?var . ?var commands:variableType ?val . ?var commands:keyContent ?key .}}".format(
                    com))

            variables = []
            # var_list = []
            for i, a in enumerate(res):
                # var_list += [str(a[0]).split("/")[-1].replace("#", ":")]
                variable = {}
                variable["key"] = str(a[2])
                variable["valueType"] = str(a[1])

                variable["properties"] = self.__parsePropertiesFromThing(str(a[0]).split("/")[-1].replace("#", ":"))
                variables += [variable]
            # Command String
            res = self.sparql.query("SELECT ?message  WHERE{{ {} commands:messageContent ?message . }}".format(com))

            command_str = {}
            for i, a in enumerate(res):
                for j, b in enumerate(a):
                    command_str = b.split("/")[-1].replace("#", ":")
                    if j > 1:
                        raise Exception("more than one Rx or Tx")

            # Rx or Tx ??
            res = self.sparql.query("SELECT ?a WHERE{{ {} commands:isRxOrTx ?a .}}".format(com))

            rxOrTx = ""
            for i, a in enumerate(res):
                for j, b in enumerate(a):
                    rxOrTx = b.split("/")[-1].replace("#", ":")
                    if j > 1:
                        raise Exception("more than one Rx or Tx")

            if rxOrTx == "commands:Rx":
                ret_list["sendCommand"] = {"message": command_str, "variables": variables,
                                           "properties": self.__parsePropertiesFromThing(com)}
            elif rxOrTx == "commands:Tx":
                ret_list["receiveCommand"] = {"message": command_str, "variables": variables,
                                              "properties": self.__parsePropertiesFromThing(com)}

        return ret_list

    def __parsePropertiesFromThing(self, thing):
        '''creates a property to json/dict

        :param thing: an URI of a thing
        :return: a dict/json as representation of a Property in OOD-API
        '''
        ret_list = []
        res = self.sparql.query(
            "SELECT ?name ?description WHERE{{ {} rdfs:label ?name . {} rdfs:comment ?description.}}".format(thing,
                                                                                                             thing))
        name = "None"
        description = "None"
        for i, a in enumerate(res):
            for j, b in enumerate(a):
                # print(b)
                if j is 0:
                    name = b.split("/")[-1].replace("#", ":")
                elif j is 1:
                    description = b.split("/")[-1].replace("#", ":")

        name_val = {"object": name, "valueType": "STRING"}
        des_val = {"object": description, "valueType": "STRING"}
        ret_list += [{"name": "name", "description": "the name (aka rdfs:label)", "value": name_val}]
        ret_list += [{"name": "description", "description": "the description (aka rdfs:comment)", "value": des_val}]

        res = self.sparql.query(
            "SELECT ?prop WHERE{{ {} commands:hasProperty ?prop .}}".format(thing))
        properties = []
        for i, a in enumerate(res):
            for j, b in enumerate(a):
                if j is 0:
                    properties += [b.split("/")[-1].replace("#", ":")]
        for prop in properties:
            name = "None"
            desc = "None"
            res = self.sparql.query(
                "SELECT DISTINCT ?name ?des WHERE{{ {} rdfs:label ?name . {} rdfs:comment ?des}}".format(prop, prop))
            for i, a in enumerate(res):
                for j, b in enumerate(a):
                    if j is 0:
                        name = b.split("/")[-1].replace("#", ":")
                    if j is 1:
                        desc = b.split("/")[-1].replace("#", ":")
            res = self.sparql.query(
                "SELECT DISTINCT ?a WHERE{{ {} commands:propertyContent ?a .}}".format(prop))
            obj = {}
            for i, a in enumerate(res):
                for j, b in enumerate(a):
                    obj = {"object": b.split("/")[-1].replace("#", ":"), "valueType": "STRING"}

            # @TODO try to find out valueType
            ret_list += [{"name": name, "description": desc, "value": obj}]
        return ret_list

    def format_print(self, string):
        #return
        print("[SPARQL]{}".format(string))
