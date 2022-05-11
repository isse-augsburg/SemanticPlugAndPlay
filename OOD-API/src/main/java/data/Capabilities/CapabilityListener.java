package data.Capabilities;

import Commands.data.Parameter;
import data.Devices.DeviceNotInstantiatedException;

import java.io.Serializable;
import java.util.ArrayList;

public interface CapabilityListener extends Serializable {
    void onReceiveEvent(Capability sender, ArrayList<Parameter> parameter);
}