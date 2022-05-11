# Semantic Controller
![SemanticControllerDiagram.pdf](/uploads/df48b1f34507f51c9106c1282884aac1/SemanticControllerDiagram.pdf)

Run the Serialportlistener:
```bash
python3 Serialportlistener.py
```

## Observer/Observable
These classes follow the Oberverer Pattern.
```python
def update(self, observable: Observable, string: str) -> None:
```
Gets called upon
```python
def notify(self, string: str) -> None:
```
was called in an Observable.

## Adapter
This Class has a one-on-one connection with Semantic Adapter.
Therefor it implements pycom from python side.

## sparql_endpoint
This gets called by Serialportlistener upon a recognition of a new device on a port.
(inside the update of Serialportlistener).

## Serialportlistener
This is the main Semantic Controller class.
It manages a little server on which the ood-api can connect.
controls the UART-ports and starts Adapter for each.

Communicates with via Oberverer pattern.