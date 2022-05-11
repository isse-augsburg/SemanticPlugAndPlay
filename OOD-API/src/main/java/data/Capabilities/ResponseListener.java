package data.Capabilities;

import Commands.ResponseOfCapabilityCommand;
import data.Devices.DeviceNotInstantiatedException;

public interface ResponseListener {
    /**
     *
     * @param response The response got from ThinClient
     */
    public void fireNewResponse(ResponseOfCapabilityCommand response);
}
