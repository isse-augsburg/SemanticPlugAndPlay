from SPARQL import StringArithmetics
import sparql_endpoint

sparql = sparql_endpoint.sparql_endpoint("../SPARQL/CommandOntology.owl")
#print(sparql.getJsonTranslation(["DHT_11"]))
sparql.current_devices = sparql.all_devices_in_Ontology
print(sparql.getSimplePropertyList("commands:MeasureHumidityCapability"))
print(StringArithmetics.calculate_string_array_similarity(["Hallo"], ["Halo"], 0.8))

a = sparql.getJsonDictFromBlueprint({"type": "blueprint", "src":1, "dev_props":["dht11"], "capabilities":[["Tempatur"], ["Humidity"]]}, threshhold=0.25)
print("A: {}".format(a))
b = sparql.getJsonDictFromBlueprint({"type": "blueprint", "src":1, "dev_props":["dht11"], "capabilities":[]}, threshhold=0.25)
print("B: {}".format(b))
c = sparql.getJsonDictFromBlueprint({"type": "blueprint", "src":1, "dev_props":[], "capabilities":[["Tempature"]]}, threshhold=0.25)
print("C: {}".format(c["json"]))

