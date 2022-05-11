import Commands.data.Parameter;
import Networking.ThinClient;
import data.Capabilities.Capability;
import data.Capabilities.CapabilityNotFoundException;
import data.Capabilities.CapabilityNotInitiatedException;
import data.Devices.Device;
import data.Devices.DeviceNotInstantiatedException;

import java.io.IOException;
import java.util.ArrayList;

public class Main2 {
    public static void main(String[] args) throws InterruptedException, IOException, CapabilityNotFoundException, CapabilityNotInitiatedException {

        Device myDev = new Device(new Capability[]{}, "PixyCam");
        myDev.registerDevice().join();
        System.out.println("Weight PixyCam: " + myDev.triggerCapability("GetWeight").waitForAnswer().getContent("SimpleDoubleParameter"));

        Device magnet = new Device(new Capability[]{}, "ElectroMAgnet");
        magnet.registerDevice().join();
        System.out.println("Weight Electromagnet: " + magnet.triggerCapability("GetWeight").waitForAnswer().getContent("SimpleDoubleParameter"));
    }

}
