package Commands;

import Commands.data.DeviceRequirement;

public class DeviceRemovedCommand extends BasicCommand {
    private DeviceRequirement dev_req;

    public DeviceRemovedCommand(){

    }

    public DeviceRequirement getDev_req() {
        return dev_req;
    }

    public void setDev_req(DeviceRequirement dev_req) {
        this.dev_req = dev_req;
    }
}
