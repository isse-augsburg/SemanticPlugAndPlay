package data.Devices;

import Commands.data.DeviceRequirement;

import java.util.HashMap;

/**
 * A Singleton Container for Devices
 */
public class DeviceContainer {
    private static DeviceContainer instance = null;
    private HashMap<DeviceRequirement, Device> container = new HashMap<>();


    private DeviceContainer(){
        instance = this;
    }

    public static DeviceContainer getInstance(){
        return instance == null ? new DeviceContainer() : instance;
    }

    public boolean checkDevice(DeviceRequirement requirement){
        return container.get(requirement) != null;
    }

    /**
     * Returns the queried Device
     * @param requirement the key
     * @return the Device
     */
    public Device getDevice(DeviceRequirement requirement) {
        if(checkDevice(requirement))
            return container.get(requirement);
        throw new IllegalArgumentException("No such Device!");
    }

    /**
     * Registers a Device to the container
     * @param device the Device to register
     */
    public void addDevice(Device device) {
        if(device.getRequirements() == null)
            throw new IllegalArgumentException("A Device needs Requirements!");
        if(checkDevice(device.getRequirements()))
            throw new IllegalArgumentException("Device already exists!");
        container.put(device.getRequirements(), device);
    }
}
