package Commands;

import Commands.data.DeviceRequirement;
import data.Devices.Device;

public class QueryDeviceCommand extends BasicCommand{
    private DeviceRequirement dev_props = new DeviceRequirement();

    public QueryDeviceCommand(){

    }

    public QueryDeviceCommand(Device device, String src){
        super("blueprint", src);
        this.dev_props = device.getRequirements();
    }

    public DeviceRequirement getDev_props() {
        return dev_props;
    }

    public void setDev_props(DeviceRequirement dev_props) {
        this.dev_props = dev_props;
    }
}
