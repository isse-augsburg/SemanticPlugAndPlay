package Commands.data;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;

public class CapabilityRequirement {
    private HashSet<String> capability = new HashSet<>();

    public CapabilityRequirement(){

    }

    @Override
    public boolean equals(Object other){
        if(other.getClass() != this.getClass())
            return false;
        return ((CapabilityRequirement) other).capability.equals(capability);
    }

    @Override
    public int hashCode() {
        return toString().hashCode();
    }

    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        for(String s:capability){
            ret.append(s).append(",");
        }
        return ret.toString();
    }

    public CapabilityRequirement(String... reqs) {
        Collections.addAll(capability, reqs);
    }

    public CapabilityRequirement(ArrayList<String> reqs){
        capability.addAll(reqs);
    }

    public CapabilityRequirement addRequirement(String... reqs){
        Collections.addAll(capability, reqs);
        return this;
    }

    public HashSet<String> getCapability() {
        return capability;
    }

}
