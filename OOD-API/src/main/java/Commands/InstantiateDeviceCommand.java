package Commands;

import data.Devices.Device;

public class InstantiateDeviceCommand extends BasicCommand {

    private Device json;

    public InstantiateDeviceCommand(){
        super();
    }

    public Device getJson() {
        return json;
    }

    public void setJson(Device json) {
        this.json = json;
    }
}
