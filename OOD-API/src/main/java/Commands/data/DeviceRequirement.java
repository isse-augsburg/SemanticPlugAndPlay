package Commands.data;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;

public class DeviceRequirement {
    private HashSet<String> device = new HashSet<>();
    private HashSet<CapabilityRequirement> capabilities = new HashSet<>();

    public DeviceRequirement(){

    }

    public DeviceRequirement(String... reqs){
        Collections.addAll(device, reqs);
    }

    public DeviceRequirement(ArrayList<CapabilityRequirement> capreqs, String... reqs){
        Collections.addAll(device, reqs);
        capabilities.addAll(capreqs);
    }

    public DeviceRequirement(CapabilityRequirement[] capreqs, String... reqs){
        Collections.addAll(device, reqs);
        capabilities.addAll(Arrays.asList(capreqs));
    }

    public DeviceRequirement(CapabilityRequirement... capreqs){
        capabilities.addAll(Arrays.asList(capreqs));
    }

    public boolean equals(Object other){
        if(other.getClass() != this.getClass())
            return false;
        return ((DeviceRequirement) other).device.equals(device) && ((DeviceRequirement) other).capabilities.equals(capabilities);
    }

    @Override
    public String toString() {
        String ret = "";
        for(String s: device)
            ret = ret.concat(s + ",");
        for(CapabilityRequirement cap: capabilities){
            ret = ret.concat(cap.toString());
        }
        return ret;
    }

    public DeviceRequirement addDeviceRequirement(String... reqs){
        Collections.addAll(device, reqs);
        return this;
    }

    /**
     * Adds one (!) new Capability requirement.
     * @param cap_reqs the capability requirement(s)
     * @return this instance
     */
    public DeviceRequirement addCapabilityRequirement(String... cap_reqs){
        capabilities.add(new CapabilityRequirement(cap_reqs));
        return this;
    }

    /**
     * Adds all new Capability requirements².
     * @param cap_reqs the capability requirement(s)
     * @return this instance
     */
    public DeviceRequirement addCapabilityRequirement(CapabilityRequirement... cap_reqs){
        Collections.addAll(capabilities, cap_reqs);
        return this;
    }

    public boolean isComposed(){
        return device.isEmpty() && !capabilities.isEmpty();
    }

    public boolean isEmpty() {
        return this.capabilities.isEmpty() && this.device.isEmpty();
    }

    public HashSet<String> getDevice() {
        return device;
    }

    public HashSet<CapabilityRequirement> getCapabilities() {
        return capabilities;
    }

}
