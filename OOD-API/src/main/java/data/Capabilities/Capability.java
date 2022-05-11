package data.Capabilities;

import Commands.*;
import Commands.data.CapabilityRequirement;
import Commands.data.DeviceRequirement;
import Commands.data.Parameter;
import Networking.AnswerThread;
import Networking.ThinClient;
import com.google.gson.annotations.Expose;
import data.Devices.Device;
import data.Devices.DeviceContainer;
import data.Property.Property;

import java.util.ArrayList;

/**
 * Normally a abstract class, but Gson prohibits this.
 * Capabilities consist of a command
 */
public class Capability implements ResponseListener {

    private ArrayList<CapabilityParameter> sendCapabilityParameter = new ArrayList<>();
    private ArrayList<CapabilityParameter> receiveCapabilityParameter = new ArrayList<>();
    private ArrayList<Property> properties = new ArrayList<Property>();

    @Expose(serialize = false, deserialize = true)
    private CapabilityRequirement requirements = new CapabilityRequirement();
    @Expose(serialize = false, deserialize = false)
    private transient ArrayList<CapabilityListener> capabilityListeners = new ArrayList<>();
    @Expose(serialize = false, deserialize = false)
    private transient ArrayList<Object> lastReceivedResponse = new ArrayList<>();
    @Expose(serialize = false, deserialize = false)
    private transient boolean registered = false;

    /**
     *
     */
    public Capability(String... requirements) {
        this.requirements = new CapabilityRequirement(requirements);
    }


    public Capability() {

    }

    /**
     * Creates a new Device containing a COPY!! of this Capability
     * @return a new Device
     */
    public Device TransformToDevice() throws CapabilityNotFoundException {
        if(this.requirements.getCapability().isEmpty() && !registered)
            throw new CapabilityNotFoundException("This Capability has no Requirements!");
        DeviceRequirement requirement = new DeviceRequirement(this.requirements);
        if(DeviceContainer.getInstance().checkDevice(requirement))
            return DeviceContainer.getInstance().getDevice(requirement);

        if(registered){
            Device dev = new Device(requirement);
            ArrayList<Capability> list = new ArrayList<>();
            Capability n = new Capability();
            n.transformCapability(this);
            list.add(n);
            dev.setCapabilities(list);
            dev.getProperties().addAll(properties);
            dev.setRegistered(true);
            return dev;
        } else {
            return new Device(requirement);
        }
    }

    public void deleteData() {
        this.properties = new ArrayList<>();
        this.sendCapabilityParameter = new ArrayList<>();
        this.receiveCapabilityParameter = new ArrayList<>();
        this.registered = false;
    }

    public AnswerThread triggerCapability(Parameter... parameters) {
        return this.triggerCapability(null, 0, parameters);
    }

    public AnswerThread triggerCapability(CommandCallback commandCallback, Parameter... parameters) {
        return this.triggerCapability(commandCallback, 0, parameters);
    }

    public AnswerThread triggerCapability(double freq, Parameter... parameters) {
        return this.triggerCapability(null, freq, parameters);
    }

    public AnswerThread triggerCapability(CommandCallback callback, double freq, Parameter... params) {
        if(!checkParameters(params))
            throw new IllegalArgumentException("Parameters didn´t check.");
        InvokeCapabilityCommand c = new InvokeCapabilityCommand(this.getCapabilityPropertyByName("name"), freq, params);
        try {
            return ThinClient.getInstance().invokeCapability(c, callback);
        } catch (InvalidCommandException | CommandAlreadyInvokedException e) {
            e.printStackTrace();
        }
        throw new NullPointerException("Capability couldn't be invoked!");
    }

    public AnswerThread triggerCapability(CommandCallback callback, double freq, String device, Parameter... params) {
        if(!checkParameters(params))
            throw new IllegalArgumentException("Parameters didn´t check.");
        InvokeCapabilityCommand c = new InvokeCapabilityCommand(this.getCapabilityPropertyByName("name"), freq, params);
        if(device != null && !device.equals(""))
            c.setDevice(device);
        try {
            return ThinClient.getInstance().invokeCapability(c, callback);
        } catch (InvalidCommandException | CommandAlreadyInvokedException e) {
            e.printStackTrace();
        }
        throw new NullPointerException("Capability couldn't be invoked!");
    }

    public String getCapabilityPropertyByName(String name) {
        for (Property property : properties) {
            if (property.getName().equals(name)) {
                return property.getValue().getObject().toString();
            }
        }
        return "";
    }

    public String getURI() throws CapabilityNotInitiatedException {
        for (Property property : properties) {
            if (property.getName().equals("name")) {
                return property.getValue().getObject().toString();
            }
        }
        throw new CapabilityNotInitiatedException("Capability hasn´t been initialized yet or has been unregistered!");
    }

    public void addListener(CapabilityListener capListener) {
        if (!capabilityListeners.contains(capListener)) {
            System.out.println("Adding Listener " + capListener.toString() + " to " + this.getCapabilityPropertyByName("name"));
            this.capabilityListeners.add(capListener);
        }
    }

    /**
     * Adds all Capabilities and Properties from dummy to this.
     * Gets called to instantiate this Capability.
     * @param dummy another Capability
     */
    public void transformCapability(Capability dummy){
        //this.requirements.clear();
        this.sendCapabilityParameter.clear();
        this.receiveCapabilityParameter.clear();
        this.sendCapabilityParameter.addAll(dummy.sendCapabilityParameter);
        this.receiveCapabilityParameter.addAll(dummy.receiveCapabilityParameter);
        this.properties.clear();
        this.properties.addAll(dummy.properties);
        registered = true;
    }

    @Override
    public void fireNewResponse(ResponseOfCapabilityCommand response) {
        if (this.getReceiveCapabilityParameter() == null)
            return;
        this.lastReceivedResponse.clear();
        this.lastReceivedResponse.addAll(response.getParameters());
        for (CapabilityListener capabilityListener : this.capabilityListeners)
            capabilityListener.onReceiveEvent(this, response.getParameters());
    }

    /**
     * Getter and Setter
     * Mostly needed for serialize/deserialize
     **/
    public ArrayList<Property> getProperties() {
        return properties;
    }

    public void setProperties(ArrayList<Property> properties) {
        this.properties = properties;
    }

    public CapabilityRequirement getRequirements() {
        return requirements;
    }

    public ArrayList<CapabilityParameter> getSendCapabilityParameter() {
        return sendCapabilityParameter;
    }

    public void setSendCapabilityParameter(ArrayList<CapabilityParameter> sendCapabilityParameter) {
        this.sendCapabilityParameter = sendCapabilityParameter;
    }

    public ArrayList<CapabilityParameter> getReceiveCapabilityParameter() {
        return receiveCapabilityParameter;
    }

    public void setReceiveCapabilityParameter(ArrayList<CapabilityParameter> receiveCapabilityParameter) {
        this.receiveCapabilityParameter = receiveCapabilityParameter;
    }


    private boolean checkParameters(Parameter... parameters){
        for(Parameter p : parameters)
            System.out.println("Checking Parameret " + p.getUri() + " - " + p.getContent());
        return true;
    }

    public boolean isRegistered() {
        return registered;
    }

}
