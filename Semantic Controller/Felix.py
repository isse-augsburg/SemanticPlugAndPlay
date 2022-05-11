from time import sleep

from VirtualCapabilities.VirtualCapabilityFactory import VirtualCapabilityFactoryProvider

cap = VirtualCapabilityFactoryProvider().getVirtualCapability("TestField",
                                                              "https://github.com/TheRealSwagrid/TestField.git", mode="ethernet")
cap.start()
sleep(3)
cap.execute_command({"type": "trigger",
                     "capability": "GetTestFieldBoundaries",
                     "parameters": []})

cap.execute_command({"type": "trigger",
                     "capability": "SetTestFieldBoundaries",
                     "parameters": [{"uri": "TestFieldPointA", "content": [1., 2., 3.]},
                                 {"uri": "TestFieldPointB", "content": [3., 2., 1.]}]})

cap.execute_command({"type": "trigger",
                     "capability": "GetTestFieldBoundaries",
                     "parameters": []})
try:
    cap.join()
except KeyboardInterrupt as e:
    print("exiting")
    cap.kill()
except:
    print("E")
    cap.kill()
