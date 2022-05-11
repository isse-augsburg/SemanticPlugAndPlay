import Commands.data.Parameter;
import data.Capabilities.Capability;
import data.Capabilities.CapabilityNotFoundException;
import data.Capabilities.CapabilityNotInitiatedException;
import data.Devices.Device;
import data.Devices.DeviceNotInstantiatedException;

import java.awt.*;
import java.awt.event.KeyEvent;
import java.util.ArrayList;

public class Presenter extends Thread {
    public Presenter(){

    }
    private Robot robot;

    {
        try {
            robot = new Robot();
        } catch (AWTException e) {
            e.printStackTrace();
        }
    }

    private Device presenter = new Device(null, new String[]{"Presenter"});
    private boolean running = true;

    public void run() {
        System.out.println("starting Presenter");
        presenter.registerCapabilityListener(0, (
                Capability sender, ArrayList<Parameter> objects) ->

        {
            //System.out.println("Button Pressed:  + objects.get(0));
            if((objects.get(0).getContent()).equals("FASTFORWARD")){
                robot.keyPress(KeyEvent.VK_RIGHT);
                robot.keyRelease(KeyEvent.VK_RIGHT);
            } else if((objects.get(0).getContent()).equals("FASTBACK")){
                robot.keyPress(KeyEvent.VK_LEFT);
                robot.keyRelease(KeyEvent.VK_LEFT);
            } else if((objects.get(0).getContent()).equals("PAUSE")){
                robot.keyPress(KeyEvent.VK_ENTER);
                robot.keyRelease(KeyEvent.VK_ENTER);
            }else if((objects.get(0).getContent()).equals("VOL+")){
                robot.keyPress(KeyEvent.VK_UP);
                robot.keyRelease(KeyEvent.VK_UP);
            }else if((objects.get(0).getContent()).equals("VOL-")){
                robot.keyPress(KeyEvent.VK_DOWN);
                robot.keyRelease(KeyEvent.VK_DOWN);
            } else if((objects.get(0).getContent()).equals("UP")){
                robot.keyPress(KeyEvent.VK_UP);
                robot.keyRelease(KeyEvent.VK_UP);
            } else if((objects.get(0).getContent()).equals("DOWN")){
                robot.keyPress(KeyEvent.VK_DOWN);
                robot.keyRelease(KeyEvent.VK_DOWN);
            }else if((objects.get(0).getContent()).equals("POWER")){
                robot.keyPress(KeyEvent.VK_ESCAPE);
                robot.keyRelease(KeyEvent.VK_ESCAPE);
            }else if((objects.get(0).getContent()).equals("9")){
                try {
                    presenter.printCompleteDescription();
                } catch (DeviceNotInstantiatedException e) {
                    e.printStackTrace();
                }
            }
        });

        while (true) {
            try {
                loop();
            } catch (Exception e) {
                //e.printStackTrace();
            }
        }
    }


    void loop() throws DeviceNotInstantiatedException, CapabilityNotFoundException, CapabilityNotInitiatedException {

            presenter.triggerCapability(0);
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }
}
