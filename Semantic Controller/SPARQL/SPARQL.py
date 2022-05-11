import json

import rdflib

from AbstractAdapter import AbstractAdapter
from SPARQL.StringArithmetics import calculate_string_array_similarity


class SPARQL_python_endpoint(AbstractAdapter):

    def __init__(self, uri: str):
        """Constructor of the SPARQL endpoint

        :param uri: address of the ontology (can be online)
        """
        super().__init__()
        self.dev_name = "SPARQLEndpoint"
        self.graph = "SPARQLEndpoint"
        self.port = uri
        self.sparql = rdflib.Graph()
        self.format_print("Parsing Uri: " + uri)
        self.sparql.parse(uri)
        self.prefix = "commands:"

        # determine all devices described
        self.all_devices_in_Ontology = self.sparql_query(f"SELECT ?devs WHERE{{ ?devs rdf:type {self.prefix}Device .}}")
        print("[SPARQL]All devices in Ontology: " + str(self.all_devices_in_Ontology))
        # List of all Virtual Capability Devices
        self.all_virtual_capabilities_devices = list(set(self.sparql_query("SELECT ?c WHERE{ "
                                                                           f"?a rdf:type {self.prefix}VirtualCapability . "
                                                                           f"?c {self.prefix}hasCapability ?a . "
                                                                           f"?c rdf:type {self.prefix}Device}}") +
                                                         self.sparql_query("Select ?c WHERE { "
                                                                           f"?a rdf:type {self.prefix}Dynamic_Property ."
                                                                           f"?a {self.prefix}hasCapability ?b ."
                                                                           f"?b rdf:type {self.prefix}VirtualCapability ."
                                                                           f"?c {self.prefix}hasProperty ?a ."
                                                                           f"?c rdf:type {self.prefix}Device }}")))

        # Map device URI to it´s Capabilities -> "{self.prefix}uri"->["{self.prefix}cap1uri", "{self.prefix}cap2uri"]
        self.current_devices = {
            f"{self.prefix}SPARQLEndpoint": [f"{self.prefix}SPARQLCalculateAll", f"{self.prefix}SPARQLquery"]
        }

        self.all_blueprints = []
        self.serializer = DeviceSerializer(self.sparql_query, self.sparql, self.prefix)
        self.cap_uris = ["SPARQLCalculateAll", "SPARQLquery"]
        """
        for d in self.all_devices_in_Ontology:
            self.current_devices[d] = self.sparql_query(
                f"SELECT ?a WHERE{{ {d} {self.prefix}hasCapability ?a . ?a rdf:type {self.prefix}Capability.}}")
        """

    @property
    def current_capabilities(self):
        ls = list()
        for caps in self.current_devices.values():
            ls += caps
        return ls

    def execute_command_implementation(self, trigger_command: dict) -> None:
        if trigger_command["capability"] == "SPARQLquery":
            response = {
                "type": "response",
                "src": trigger_command["src"],
                "capability": "SPARQLquery",
                "parameters": {
                    "SPARQLqueryResult": str(self.sparql_query(trigger_command["QueryString"]))
                }
            }
            self.notify(json.dumps(response))
            return
        elif trigger_command["capability"] == "SPARQLCalculateAll":
            all_queries = []
            to_query = trigger_command["parameters"]["CalculateAllParameter"]
            for dev in self.current_devices:
                all_queries += self.sparql_query(f"SELECT ?b WHERE{{ {dev} {self.prefix}hasProperty ?a ."
                                                 f"?a rdfs:label {to_query}."
                                                 f"?a {self.prefix}isType ?b}}")
            response = {
                "type": "response",
                "src": trigger_command["src"],
                "capability": "CalculateAll",
                "parameters": {
                    "CalculateAllReturnParameter": str(all_queries)
                }
            }
            self.notify(json.dumps(response))
            return
        self.format_print(f"Unkown Command {trigger_command}")

    def setup_implementation(self) -> bool:
        return True

    def loop(self):
        pass

    def kill_implementation(self):
        self.sparql.close()

    def transmit_subcapability_response(self, command: dict):
        pass

    # def format_print(self, string) -> None:
    #   pass

    def sparql_query(self, query_string: str) -> list:
        """A simple SPARQL query

        :param query_string: the query
        :return: a list of results
        """
        res = []

        query_result = self.sparql.query(query_string)  # .serialize(format='json')
        for x in query_result.bindings:
            for var in x:
                raw = str(x[var]).split("/")[-1].replace("#", ":")
                if raw not in res:
                    res += [raw]
        return res

    def get_git_repository(self, device_uri: str) -> str:
        self.format_print(f"Getting Git Repository address: {device_uri}")
        query = self.sparql.query(f"SELECT ?a {{{device_uri} {self.prefix}GitRepository ?a .}}")
        res = []
        for x in query.bindings:
            for var in x:
                raw = x[var]
                if raw not in res:
                    res += [raw]
        return res[0]

    def onNewDeviceConnected(self) -> list:
        '''
        CAUTION
        '''
        rets = []
        for bp in self.all_blueprints:
            rets += [self.translate_blueprint(bp)]
        return rets

    def calculate_virtual_capabilities(self, current_devices: dict) -> dict:
        """Calculates all devices which are possible, based on current devices as starting point

        :param current_devices: starting point. just some devices with {"device":["cap1", "cap2"]}
        :return: a dict with devices, which are currently possible to start/be used
        """
        # important, call by value!
        local_current_devices = dict(current_devices)

        def get_current_capabilities():
            ls = list()
            for caps in local_current_devices.values():
                ls += caps
            return ls

        for v_cap_dev in self.all_virtual_capabilities_devices:
            caps = []

            for v_cap in self.get_all_capabilities(v_cap_dev)[v_cap_dev]:
                sub_caps = self.sparql_query(f"SELECT ?a WHERE{{ {v_cap} {self.prefix}hasSubCapabilities ?a .}}")
                # self.format_print(f"Device {v_cap_dev} hasCap {v_cap} SubCaps {sub_caps}")
                req_fulfills = True
                for s_cap in sub_caps:
                    req_fulfills &= s_cap in get_current_capabilities()
                if req_fulfills:
                    caps += [v_cap]

            local_current_devices[v_cap_dev] = caps

        if local_current_devices != current_devices:
            # Recursion: Next SubCapabilities!
            return self.calculate_virtual_capabilities(local_current_devices)
        return local_current_devices

    # Matching. aka Brainfuck blueprint=query/requirement, threshhold=??
    def translate_blueprint(self, blueprint: dict, threshhold: float = 0.25) -> dict:
        """Translates a blueprint command to the ood-api representation

        :param blueprint: The blueprint command
        :param threshhold: Threshhold is the minimum similarity to match to a device
        :return: Returns a parsed device
        """
        self.format_print("Starting decrypting device: {}".format(blueprint))
        if blueprint not in self.all_blueprints:
            self.all_blueprints += [blueprint]
        ret = {}
        ret["src"] = blueprint["src"]
        ret["type"] = "device"
        # a list of strings
        queryDevProperties = blueprint["dev_props"]["device"]
        # A List of lists of strings
        queryCapProperties = blueprint["dev_props"]["capabilities"]

        # current Selected/matched device (device with greatest dev_confidence)
        final_selected_device = ""

        # physical device is meant. First check deviceProperties than check CapabilityProperties
        if len(queryDevProperties) > 0:
            self.format_print(
                f"Parsing whole phyical device from properties: {queryDevProperties} and cap properties: {queryCapProperties}")
            # Current highest dev_confidence/match
            device_match_value = 0
            final_selected_capabilities = []

            for adjacentDevice in self.calculate_virtual_capabilities(self.current_devices).keys():
                # Calculate Distance between Properties we want and Properties we have
                # TODO include dynamix
                dev_confidence = calculate_string_array_similarity(queryDevProperties,
                                                                   self.get_simple_property(
                                                                       adjacentDevice))
                # No specific Caps requested, taking "natural" caps from device
                if len(queryCapProperties) == 0:
                    current_selected_capabilities = self.sparql_query(
                        f"SELECT ?a WHERE{{ {adjacentDevice} {self.prefix}hasCapability ?a .}}")
                    cap_confidence = dev_confidence
                else:
                    # Get the Capability which are described by the SPARQL and are in the semantic adapter
                    cap_actual = list(set.intersection(set(self.sparql_query(
                        f"SELECT ?a WHERE{{ {adjacentDevice} {self.prefix}hasCapability ?a .}}")),
                        set(self.current_devices[adjacentDevice])))
                    cap_confidence, current_selected_capabilities = self.select_capabilities(
                        cap_requirements=queryCapProperties, cap_actual=cap_actual,
                        threshhold=threshhold)
                    # Cap not found... -> No Device with the specific Capability {queryCapProperties}
                    if cap_confidence == 0:
                        dev_confidence = 0.

                # Recalculating dev_confidence
                dev_confidence = float(dev_confidence + cap_confidence) / 2.
                # Print foreach existing device
                self.format_print(
                    "[{}] properties: ({}...), matchvalue={}, from dev_requirement={} | Caps: {} from cap_requirement: {}, Capmatchvalue={}".format(
                        adjacentDevice.replace(f"{self.prefix}", ""), self.get_simple_property(adjacentDevice)[:2],
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
            if final_selected_device == "":
                ret["json"] = {}
                return ret
        # Just query from all current capabilitities to construct a virtual device
        else:
            self.format_print(f"Creating a virtual Device from requirements: {queryCapProperties}")
            list_of_all_caps = []
            '''
            for dev in self.calculate_virtual_capabilities(self.current_devices).keys():
                first = set(self.sparql_query(f"SELECT ?a WHERE{{ {dev} {self.prefix}hasCapability ?a .}}"))
                second = set(self.calculate_virtual_capabilities(self.current_devices)[dev])
                cap_actual = list(set.intersection(set(self.sparql_query(
                    f"SELECT ?a WHERE{{ {dev} {self.prefix}hasCapability ?a .}}")),
                    # TODO look if this works
                    set(self.calculate_virtual_capabilities(self.current_devices)[dev])))
                list_of_all_caps += cap_actual

                self.format_print(f"{dev}: {first} intersect {second}  --> {cap_actual} \n\n{list_of_all_caps}")
            '''
            for val in self.calculate_virtual_capabilities(self.current_devices).values():
                list_of_all_caps += val

            # self.format_print(f"All current possible Capabilities: {list_of_all_caps} from {self.calculate_virtual_capabilities(self.current_devices)} from {self.current_devices}")
            cap_confidence, final_selected_capabilities = self.select_capabilities(queryCapProperties, list_of_all_caps,
                                                                                   threshhold=threshhold)

            self.format_print(
                f"Capability Properties {queryCapProperties} have matched with Capabilities: {final_selected_capabilities}, confidence is: {cap_confidence}")

        # "transform" device
        ret["json"] = self.serializer.parseDeviceFromNameAndCaps(final_selected_device, final_selected_capabilities)
        # Add requirements for matching in ood-api

        if "json" in ret.keys():
            # ret["json"]["requirements"] = blueprint["dev_props"]
            ret["json"]["requirements"] = {}
            (ret["json"]["requirements"])["device"] = queryDevProperties
            (ret["json"]["requirements"])["capabilities"] = queryCapProperties
            if len(queryCapProperties) > 0:
                for i, c in enumerate(ret["json"]["capabilities"]):
                    print(queryCapProperties)
                    c["requirements"] = []
                    c["requirements"] = queryCapProperties[i]
        # create a new adapter to start the virtual caps
        if final_selected_device in self.all_virtual_capabilities_devices:
            # TODO include if a virtual Capability is queried
            DevicesToStart = self.get_caps_and_sub_caps_recursive(final_selected_device)
            self.format_print(
                f"Waiting for the device {final_selected_device} to startup... Implied devices: {DevicesToStart}")
            self.controller.start_virtual_capabilities(DevicesToStart)
            while final_selected_device not in self.current_devices:
                pass
            # self.format_print(f"Continuing ({final_selected_device}) .... \n\n{ret}")

        return ret

    def select_capabilities(self, cap_requirements: list, cap_actual: list, threshhold: float) -> (float, list):
        """Selects Capabilities according to requirements
        Selects capabilities from a list of requirements. Returns normed confidence and list of capnames

        :param cap_requirements: a list of strings
        :param cap_actual: a list of cap-uris
        :param threshhold: a float, the minimum the string matching should have
        :return: the confidence, a list of uris of the selected caps
        """
        self.format_print(
            f"Selecting capabilities based on: {cap_requirements}, from list of capabilities: {cap_actual}")
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
                    cap_confidence = calculate_string_array_similarity(qCap,
                                                                       self.get_simple_property(aCap),
                                                                       level_of_wrongness=0.4)
                    # Found a better matching capability
                    if cap_confidence > capability_match_value and cap_confidence > threshhold:
                        capability_match_value = cap_confidence
                        best_capability_match = aCap

            # Capability couldn´t be matched/found
            if capability_match_value == 0:
                return 0, []
            # Found a cap, adding it to return value
            else:
                final_cap_confidence += capability_match_value
                selected_capabilities += [best_capability_match]

        # @TODO maybe a better solution to determine value of cap-matching
        return final_cap_confidence / float(len(cap_requirements)), selected_capabilities

    def get_simple_property(self, thing) -> list:
        '''Helper to extract strings from the properties

            Queries all the Properties from am Command:Thing (Like a Device, Capability, Variable....)
            :param thing: the URI to be queried.
            :return: a list of strings.
        '''
        # add URI to simple property
        ret_list = [thing]
        ret_list += self.sparql_query(f"SELECT ?name WHERE{{ {thing} rdfs:label ?name . }}")

        for prop in self.sparql_query(f"SELECT ?prop WHERE{{ {thing} {self.prefix}hasProperty ?prop .}}"):
            ret_list += self.sparql_query(f"SELECT ?name WHERE{{ {prop} rdfs:label ?name . }}")
            ret_list += self.sparql_query(f"SELECT DISTINCT ?a WHERE{{ {prop} {self.prefix}propertyContent ?a .}}")

        return [x.replace("{self.prefix}", "") for x in ret_list]

    def get_caps_and_sub_caps_recursive(self, device) -> dict:
        """
        Get a dict device:caps from a device.
        Includes all "subdevices". This function is needed for starting a virtual Device/Cap.

        :param device: uri of the first device
        :return: the dict
        """
        ret = {}
        caps = list(set(self.sparql_query(f"SELECT ?s {{{device} {self.prefix}hasCapability ?s .}}") +
                        self.sparql_query(
                            "Select ?b WHERE { "
                            f"{device} {self.prefix}hasProperty ?a ."
                            f"?a rdf:type {self.prefix}Dynamic_Property ."
                            "?a {self.prefix}hasCapability ?b .}")))

        ret[device] = caps
        sub_devices = []
        for cap in caps:
            sub_devices += set(self.sparql_query(
                f"SELECT ?devices {{"
                f"{cap} {self.prefix}hasSubCapabilities ?sub . "
                f"?devices {self.prefix}hasCapability ?sub . "
                f"?devices rdf:type {self.prefix}Device .}}") +
                              self.sparql_query(
                                  f"SELECT ?devices {{{cap} {self.prefix}hasSubCapabilities ?sub . "
                                  f"?dynamix {self.prefix}hasCapability ?sub . "
                                  f"?dynamix rdf:type {self.prefix}Dynamic_Property . "
                                  f"?devices {self.prefix}hasProperty ?dynamix .}}"))

        for sub_device in sub_devices:
            if sub_device not in ret.keys():
                rec_return = self.get_caps_and_sub_caps_recursive(sub_device)
                for rec_return_key in rec_return.keys():
                    ret[rec_return_key] = rec_return[rec_return_key]
        return ret

    def get_all_capabilities(self, device: str) -> dict:
        """
        Queries all Capabilities from a Device incuding Dynamix.

        :param device: The Uri of the Device
        :return: dict of form: {device:[cap1, cap2...]}
        """
        return {device: set(self.sparql_query(f"SELECT ?caps {{ {device} {self.prefix}hasCapability ?caps}}") +
                            self.sparql_query(f"SELECT ?caps {{ "
                                              f"{device} {self.prefix}hasProperty ?dynamix ."
                                              f"?dynamix rdf:type {self.prefix}Dynamic_Property ."
                                              f"?dynamix {self.prefix}hasCapability ?caps .}}"))}

    def get_direct_subcaps(self, device) -> dict:
        f"""
        Get the subcaps from {device}. This is {{cap:{{subcap:None}} and so on
        
        :param device: The URI of the device
        :return: a dictionary mapping Capability of the device to it's subcaps
        """
        ret = {}
        caps = self.get_all_capabilities(device)[device]
        for cap in caps:

            sub_caps = self.sparql_query(f"SELECT ?caps {{ {cap} {self.prefix}hasSubCapabilities ?caps}}")
            ret[cap.replace("{self.prefix}", "")] = []
            for sub_cap in sub_caps:
                ret[cap.replace(f"{self.prefix}", "")] += [sub_cap.replace(f"{self.prefix}", "")]
        return ret

    def recalculate_devices(self, adapter: AbstractAdapter):
        if len(self.all_blueprints) > 0:
            self.format_print("RECALCULATING DEVICES!")
            try:
                if not adapter.running:
                    self.current_devices.pop(f"{self.prefix}" + adapter.graph)
            except:
                pass
            for bp in self.all_blueprints:
                self.notify(json.dumps(self.translate_blueprint(bp)))

    def isVirtualDevice(self, v_dev) -> bool:
        """
        Checks if a Device is a virtual Device

        :param v_dev: the uri of the device to check
        :return: true if virtual (has virtual caps)
        """
        virtual_capabilities = set(self.sparql_query(f"SELECT ?caps {{ {v_dev} {self.prefix}hasCapability ?caps . "
                                                 f"?caps rdf:type {self.prefix}VirtualCapability .}}") +
                                   self.sparql_query(f"SELECT ?caps {{ "
                                                     f"{v_dev} {self.prefix}hasProperty ?dynamix ."
                                                     f"?dynamix rdf:type {self.prefix}Dynamic_Property ."
                                                     f"?dynamix {self.prefix}hasCapability ?caps ."
                                                     f"?caps rdf:type {self.prefix}VirtualCapability .}}"))
        return len(virtual_capabilities) > 0



class DeviceSerializer(object):
    def __init__(self, query, sparql, prefix):
        self.query = query
        self.sparql = sparql
        self.prefix = prefix

    def parseDeviceFromNameAndCaps(self, devname: str, capnames: list):
        '''Creates a json/dict which is used to instantiate devices in the ood-api

           :param devname: is the uri of the device, from which the device properties come from
           :param capnames: are the uri of the capabilities
           :return: a dict/json for a Device
        '''
        cancer = {}
        cancer["properties"] = []
        cancer["capabilities"] = []
        additional_capnames_from_dynamix = list()
        additional_capnames_from_sub_caps = list()

        if devname != "" and devname is not None:
            cancer["properties"] += self.__parsePropertiesFromThing(devname)
            for dynamix in self.query(
                    f"SELECT ?dynamix {{{devname} {self.prefix}hasProperty ?dynamix . ?dynamix rdf:type {self.prefix}Dynamic_Property .}}"):
                additional_capnames_from_dynamix += self.query(f"SELECT ?a {{{dynamix} {self.prefix}hasCapability ?a .}}")

        for cap in set(capnames + additional_capnames_from_dynamix):
            if cap != "" and cap is not None:
                additional_capnames_from_sub_caps += self.query(f"SELECT ?a {{{cap} {self.prefix}hasSubCapabilities ?a .}}")

        # CAPS
        for cap in set(capnames + additional_capnames_from_dynamix + additional_capnames_from_sub_caps):
            if cap != "" and cap is not None:
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
        send_param_list, receive_param_list = self.__get_params_plus_subcap_params(cap)

        ret_list["sendCapabilityParameter"] = self.__parse_parameter(send_param_list)
        ret_list["receiveCapabilityParameter"] = self.__parse_parameter(receive_param_list)
        return ret_list

    def __get_params_plus_subcap_params(self, cap) -> (list, list):
        send_params = self.query(
            f"SELECT ?a WHERE{{ {cap} {self.prefix}hasSendParameter ?a . ?a rdf:type {self.prefix}Parameter.}}")
        receive_params = self.query(
            f"SELECT ?a WHERE{{ {cap} {self.prefix}hasReceiveParameter ?a . ?a rdf:type {self.prefix}Parameter.}}")

        for subcap in self.query(f"SELECT ?a WHERE {{{cap} {self.prefix}hasSubCapabilities ?a . }}"):
            subcap_send_params, subcap_receive_params = self.__get_params_plus_subcap_params(subcap)
            send_params += subcap_send_params
            receive_params += subcap_receive_params
        return send_params, receive_params

    def __parse_parameter(self, param_uris: list) -> list:
        """ Creates a list of parsed parameters from a list of parameter uris

        :param param_uris: List of parameter uris
        :return: a list of parsed parameter
        """
        param_list = []
        for p in param_uris:
            param = {}
            param["properties"] = self.__parsePropertiesFromThing(p)
            try:
                valType = self.query(f"SELECT ?a WHERE{{ {p} {self.prefix}isType ?a .}}")[0].replace("{self.prefix}", "")
            except IndexError as e:
                valType = "NONE"

            param["valueType"] = valType
            param_list += [param]
        return param_list

    def __parsePropertiesFromThing(self, thing):
        '''creates a property to json/dict

        :param thing: an URI of a thing
        :return: a dict/json as representation of a Property in OOD-API
        '''
        ret_list = []

        try:
            name = self.query(f"SELECT DISTINCT ?name WHERE {{ {thing} rdfs:label ?name .}}")[0]
        except IndexError as e:
            name = thing.replace(f"{self.prefix}", "")
        try:
            description = self.query(f"SELECT ?name WHERE {{ {thing} rdfs:comment ?name .}}")[0]
        except IndexError as e:
            description = "unkown"

        name_val = {"object": name, "valueType": "STRING"}
        des_val = {"object": description, "valueType": "STRING"}
        ret_list += [{"name": "name", "description": "the name (aka rdfs:label)", "value": name_val}]
        ret_list += [{"name": "description", "description": "the description (aka rdfs:comment)", "value": des_val}]
        ret_list += [
            {"name": "uri", "description": "the URI of this object", "value": {"object": thing, "valueType": "STRING"}}]

        for prop in self.query(f"SELECT ?prop WHERE{{ {thing} {self.prefix}hasProperty ?prop .}}"):
            try:
                name = self.query(f"SELECT DISTINCT ?name WHERE {{ {prop} rdfs:label ?name .}}")[0].replace("{self.prefix}",
                                                                                                            "")
            except IndexError as e:
                name = prop.replace(f"{self.prefix}", "")
            try:
                desc = self.query(f"SELECT ?name WHERE {{ {prop} rdfs:comment ?name .}}")[0]
            except IndexError as e:
                desc = "unkown"

            try:
                valType = self.query(f"SELECT ?a WHERE{{ {prop} {self.prefix}isType ?a .}}")[0].replace("{self.prefix}", "")
            except IndexError as e:
                valType = "NONE"

            obj = {"object": None,
                   "valueType": valType}

            ret_list += [{"name": name, "description": desc, "value": obj}]
        return ret_list
