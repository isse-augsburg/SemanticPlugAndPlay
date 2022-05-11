# Semantic Adapter

## PyCom protocol
The syntax is provided in the code below:
```
Statement = '<',{Statement},TypeByte,{Statement},Payload,'>'
TypeByte = 'a'|'b'|'c'|'d'|'e'|'h'|'l'|'r'|'s'|'w'
Payload = (Statement|ASCII_Byte|'<<'|'<>'),Payload|ϵ$
```
`a` is used for invoking a measurement/actuation (usage: `<a:(cap_number):payload>`)

`s` is used for invoking a stream of measurements/actuations (usage: `<s:(cap_number):payload>`)

`b` for saving strings to RAM (usage: `<b:(all ASCII added % 1451):payload>`)

`c` for retreiving strings from RAM (usage: `<c(virtual RAM adress)>`)

`d` for deleting strings from RAM (usage: `<d(virtual RAM adress)>`)

`w` or `l` for writing/loading to/from EEPROM into RAM (usage: `<w>` or `<l>`)

These statements can be nested inside other statements. (usage example: `<a:<a:1:param1>0:param2>`)

## Programing an Semantic Adapter
Example provided: [examples](https://gitlab.isse.de/robotik/semanticplugandplay/semanticplugandplay/-/tree/master/Examples/SemanticAdapterExamples)