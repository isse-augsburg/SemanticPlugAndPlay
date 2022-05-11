
import Commands.data.CapabilityRequirement;
import Commands.data.DeviceRequirement;
import Commands.data.Parameter;
import Networking.ThinClient;
import data.Capabilities.Capability;
import data.Capabilities.CapabilityNotFoundException;
import data.Capabilities.CapabilityNotInitiatedException;
import data.Devices.Device;
import data.Devices.DeviceNotInstantiatedException;

import java.io.IOException;


public class Main {

    public static void main(String[] args) throws InterruptedException, IOException, CapabilityNotFoundException, DeviceNotInstantiatedException, CapabilityNotInitiatedException {

        DeviceRequirement req = new DeviceRequirement();

        Device myDev = new Device(new Capability[]{}, "SearchGridDevice");
        //myDev.registerDevice().join();

        System.out.println("Continuing.... ");
        Capability cap = new Capability("TestField", "Boundaries", "Get");

        Capability cap2 = new Capability("TestField", "Boundaries", "Set");
        Device newDevice = new Device(cap, cap2);
        newDevice.registerDevice().join();

        Device TestFieldCapDevice = cap.TransformToDevice();

        TestFieldCapDevice.registerDevice().join();
        TestFieldCapDevice.printCompleteDescription();

        myDev.getCapability("SearchGridGetNextPosition").addListener((capability, objects) -> {
            try {
                System.out.println("CAPLISTENER: " + myDev.getCapabilities().get(0).getURI() + " has a new Response! ");
            } catch (CapabilityNotInitiatedException ignored) {

            }
            for(Parameter p:objects)
                System.out.println(p.getUri() + " - " + p.getContent());
        });

        ThinClient.getInstance().addResponseListener((response) -> {
            System.out.println("RESPONSE-LISTENER: "  +response.getCapability() + " has a new Response!");
            for(Parameter p:response.getParameters())
                System.out.println(p.getUri() + " - " + p.getContent());
        });

        Device capDevice = myDev.getCapability("SearchGridGetNextPosition").TransformToDevice();
        capDevice.triggerCapability(0, .05, (params) -> {
            System.out.println("Getting parameter" + params);
        });
        capDevice.printCompleteDescription();

        /*
        myDev.getCapabilities().get(0).triggerCapability((objects)->{
            System.out.println("CALLBACK-LISTENER");
            for(Parameter p:objects)
                System.out.println(p.getUri() + " - " + p.getContent());
        }, new Parameter[]{});
        */

        //myDev.triggerCapability("SearchGridGetNextPosition").join();
        myDev.triggerCapability("SearchGridGetNextPosition").waitForAnswer();
        Thread.sleep(1000);
        myDev.unregisterDevice().join();
        //myDev2.getCapability("SetTestFieldBoundaries").triggerCapability(new Parameter[]{new Parameter("TestFieldPointA", "[1.,0.,0.]"), new Parameter("TestFieldPointB", "[1.,0.,0.]")});

        //myDev.getCapabilities().get(0).triggerCapability(new Parameter[]{new Parameter("", 1)., 2., 43.});

        //System.out.println(c.getType());
        /*
        Presenter p = new Presenter();
        ThinClient.getInstance();
        p.start();

        /*
        HomeAutomationSystem system = new HomeAutomationSystem();
        ThinClient.getInstance();
        system.start();

        */
    }

}
