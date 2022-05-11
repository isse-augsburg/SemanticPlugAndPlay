package Commands;

import Commands.data.DeviceRequirement;
import data.Devices.Device;

import java.util.ArrayList;

public class RemoveDeviceRequestCommand extends BasicCommand {
    private DeviceRequirement dev_req;

    public RemoveDeviceRequestCommand(){

    }

    public RemoveDeviceRequestCommand(String src, Device device){
        super("remdev", src);
        this.dev_req = device.getRequirements();
    }

    public RemoveDeviceRequestCommand(Device device, String src){
        super("remdev", src);
        this.dev_req = device.getRequirements();
    }


    public DeviceRequirement getDev_req() {
        return dev_req;
    }

    public void setDev_req(DeviceRequirement dev_req) {
        this.dev_req = dev_req;
    }
}
