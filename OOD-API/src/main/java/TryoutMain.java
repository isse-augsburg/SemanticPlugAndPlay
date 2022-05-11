
import Commands.data.DeviceRequirement;
import Commands.data.Parameter;
import Networking.AnswerThread;
import Networking.ThinClient;
import data.Capabilities.Capability;
import data.Capabilities.CapabilityNotFoundException;
import data.Capabilities.CapabilityNotInitiatedException;
import data.Devices.Device;
import data.Devices.DeviceNotInstantiatedException;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;


public class TryoutMain {

    public static void main(String[] args) throws InterruptedException, IOException, CapabilityNotFoundException, DeviceNotInstantiatedException, CapabilityNotInitiatedException {

        //DeviceRequirement req = new DeviceRequirement();

        //Getting Device which has Capability SpiralFlight.
        // SubCapabilities would be SearchAlgorithmDevice get next position and IsseCopter FlyToPosition
        Device myDev = new Device(new DeviceRequirement("ConstiVorfuehrungDevice"));
        myDev.registerDevice().join();
        //This is the Pixycam
        Device pixy = new Device(new DeviceRequirement("PixyCam", "Camera"));
        pixy.registerDevice().join();
        //This is the Quadcopter
        Device copter = new Device(new DeviceRequirement("ISSECIPTER", "Flying"));
        copter.registerDevice().join();

        copter.printCompleteDescription();

        //This listens to all Capability Responses.
        ThinClient.getInstance().addResponseListener((response) -> {
            /*System.out.println("RESPONSE-LISTENER: "  +response.getCapability() + " has a new Response!");
            for(Parameter p:response.getParameters())
                System.out.println(p.getUri() + " - " + p.getContent());
            */
        });

        //These variables should store the values received by the pixycam.
        //Has to be AtomicIntergers because they are used inside a lambda function. Java not smart...
        AtomicInteger xpos = new AtomicInteger(-1);
        int ypos =-1;
        int width = -1;
        int height= -1;
        int sig= -1;

        //Start streaming PixyCam Capability with 1 Hz, searching for the SignatureNumber 0 (Preset inside the cam)
        pixy.triggerCapability("PixyCamDetectObject",1,  (params) -> {
            //Java is stupid....
            int content = (int) Double.parseDouble(params.getContent("PixyCamXPosition").toString());
            //This Variable is set inside the arduino to be random numbers between -30 and 5
            xpos.set(content);
            //System.out.println("ATOMIC "+ xpos + " VS " + content);

        }, new Parameter("PixyCamSignatureNumber", 0)); //This is asyncronous.

        //Starting SpiralFlight. Save the Thread to join it later, so no position get overwritten by the SpiralFlight
        AnswerThread SpiralWaiter = myDev.triggerCapability("SpiralFlight");
        System.out.println("Start" + xpos);

        //Wait until the pseudo response of the pixycam is true ...
        while(xpos.get() <= 0 ){
            //System.out.println("Still waiting...." + xpos);
            Thread.sleep(1000);
        }

        //Ending the Stream of the pixycam
        pixy.triggerCapability("PixyCamDetectObject", -1., new Parameter("PixyCamSignatureNumber", 0)).join();

        //Cancel the spiralflight synchronously
        myDev.triggerCapability("CancelSpiralFlight").join();

        //Synchronously calls the Getter of the dynamix IsseCopterPosition, store position in pos
        Object[] pos = (Object[])copter.triggerCapability("GetISSECopterPosition").waitForAnswer("Position3D");

        //Wait till SpiralFlight is truely canceled,
        SpiralWaiter.join();

        //F
        copter.triggerCapability("FlyToPosition", new Parameter("Position3D" , pos)).join();

    }

}
