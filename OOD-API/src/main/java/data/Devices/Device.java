package data.Devices;

import Commands.CommandAlreadyInvokedException;
import Commands.CommandCallback;
import Commands.InvalidCommandException;
import Commands.data.DeviceRequirement;
import Commands.data.Parameter;
import Networking.AnswerThread;
import Networking.ParameterOrganizer;
import Networking.ThinClient;
import com.google.gson.annotations.Expose;
import data.Capabilities.*;
import data.Property.Property;
import data.Variable;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;

public class Device implements CommandCallback {
    private ArrayList<Capability> capabilities = new ArrayList<Capability>();
    private ArrayList<Property> properties = new ArrayList<Property>();

    @Expose(serialize = false, deserialize = true)
    private DeviceRequirement requirements = new DeviceRequirement();
    @Expose(serialize = false, deserialize = false)
    private transient HashMap<Integer, CapabilityListener> map = new HashMap<>();
    @Expose(serialize = false, deserialize = false)
    private transient volatile boolean registered = false;

    //Do NOT call this Method. Just for Serialize/Deserialize
    public Device() {

    }

    public Device(Capability[] capabilities, String... devProperties) {
        if (devProperties != null)
            this.requirements.addDeviceRequirement(devProperties);
        if (capabilities != null) {
            for (Capability cap : capabilities) {
                if (requirements.getCapabilities().contains(cap.getRequirements())) {
                    System.err.println("Capability already added!");
                }else {
                    requirements.addCapabilityRequirement(cap.getRequirements());
                    this.capabilities.add(cap);
                }
            }
        }
        DeviceContainer.getInstance().addDevice(this);
    }

    public Device(Capability... capabilities) {
        if (capabilities != null) {
            for (Capability cap : capabilities) {
                if (requirements.getCapabilities().contains(cap.getRequirements())) {
                    System.err.println("Capability already added!");
                }else {
                    requirements.addCapabilityRequirement(cap.getRequirements());
                    this.capabilities.add(cap);
                }
            }
        }
        DeviceContainer.getInstance().addDevice(this);
    }

    public Device(DeviceRequirement requirements){
        if(!requirements.isEmpty())
            this.requirements = requirements;
        else
            System.err.println("No Requirements passed!!!");
        DeviceContainer.getInstance().addDevice(this);
    }

    /**
     * Registers the Device in the Semantic Controller
     * @return a Thread which ends when the Device is instantiated
     * @throws DeviceNotInstantiatedException if the Device has already been registered
     */
    public Thread registerDevice() throws DeviceNotInstantiatedException {
        if(registered) {
            System.out.println(Arrays.toString(new DeviceNotInstantiatedException("This Device has already been registered!").getStackTrace()));
            //throw new DeviceNotInstantiatedException("This Device has already been registered!");
            Thread t = new Thread();
            t.start();
            return t;
        }
        try {
            return ThinClient.getInstance().registerDevice(this);
        } catch (CommandAlreadyInvokedException e) {
            throw new DeviceNotInstantiatedException("This Device has already been registered!", e);
        } catch (InvalidCommandException e1){
            throw new DeviceNotInstantiatedException("Something went wrong!", e1);
        }
    }

    /**
     * Unregisters this Device
     * @return a Thread which ends if the Device has been deleted inside the Semantic Controller
     * @throws DeviceNotInstantiatedException if the Device hasn't been registered or already has been unregistered
     */
    public Thread unregisterDevice() throws DeviceNotInstantiatedException {
        if(!registered)
            throw new DeviceNotInstantiatedException("This Device is not registered!");
        try {
            return ThinClient.getInstance().unregisterDevice(this);
        } catch (CommandAlreadyInvokedException e) {
            throw new DeviceNotInstantiatedException("Device has already been unregistered!", e);
        }catch (InvalidCommandException e1){
            throw new DeviceNotInstantiatedException("Something went wrong!", e1);
        }
    }

    /**
     * Deletes all data, clears the class.
     */
    public void deleteData() {
        for(Capability c : capabilities) {
            c.deleteData();
        }
        this.capabilities = new ArrayList<>();
        this.registered = false;
        this.properties = new ArrayList<>();
    }

    public AnswerThread triggerCapability(String uri) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(uri, 0, (CommandCallback)null);
    }

    public AnswerThread triggerCapability(String uri, Parameter... parameters) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(uri, 0, (CommandCallback) null, parameters);
    }

    public AnswerThread triggerCapability(String uri, double streaming, Parameter... parameters) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(uri, streaming, null, parameters);
    }

    public AnswerThread triggerCapability(String uri, CommandCallback callback) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(uri, 0, callback);
    }

    public AnswerThread triggerCapability(String uri, CommandCallback callback, Parameter... parameters) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(uri, 0, callback, parameters);
    }

    public AnswerThread triggerCapability(int num) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(num, null, 0);
    }

    public AnswerThread triggerCapability(int num, CommandCallback callback) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(num, callback, 0);
    }

    public AnswerThread triggerCapability(int num, double stream, CommandCallback callback) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        return triggerCapability(num, callback, stream);
    }

    public AnswerThread triggerCapability(String uri, double stream, CommandCallback callback) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        int num = 0;
        for(num = 0; num < capabilities.size(); num++){
            if(capabilities.get(num).getURI().equals(uri))
                break;
        }
        if(num >= capabilities.size())
            throw new CapabilityNotFoundException("Index out of range for uri: " + uri);
        return triggerCapability(num, callback, stream);
    }

    public AnswerThread triggerCapability(String uri, double stream, CommandCallback callback, Parameter... parameters) throws CapabilityNotFoundException, CapabilityNotInitiatedException {
        int num = 0;
        for(num = 0; num < capabilities.size(); num++){
            if(capabilities.get(num).getURI().equals(uri))
                break;
        }
        if(num >= capabilities.size())
            throw new CapabilityNotFoundException("Index out of range for uri: " + uri);
        return triggerCapability(num, callback, stream, parameters);
    }

    private AnswerThread triggerCapability(int i, CommandCallback callback, double stream, Parameter... parameters) throws CapabilityNotFoundException, CapabilityNotInitiatedException, DeviceNotInstantiatedException {
        if(!registered)
            throw new DeviceNotInstantiatedException("This Device is not registered!");
        if(i >= capabilities.size() || i < 0)
            throw new CapabilityNotFoundException("This Capability doesn't exist (Capability number: " + i + ")");
        Capability cap = this.capabilities.get(i);
        if(!cap.isRegistered())
            throw new CapabilityNotInitiatedException("This Capability isn't instantiated!");
        return cap.triggerCapability(callback, stream, getPropertyByName("uri"), parameters);
    }

    /**
     * Adds all Capabilities and Properties from dummy to this
     * Gets called to instantiate this Device.
     *
     * @param dummy another Device
     */
    public void transformDevice(Device dummy) throws DeviceNotInstantiatedException {
        //assume the right order TODO
        if (!this.requirements.equals(dummy.requirements))
            throw new DeviceNotInstantiatedException("Device not instantiable: "+this.requirements + "vs: " + dummy.requirements);
        if (!capabilities.isEmpty()) {
            for (Capability a : capabilities) {
                for (Capability b : dummy.capabilities) {
                    if (a.getRequirements().equals(b.getRequirements())) {
                        a.transformCapability(b);
                        ThinClient.getInstance().addResponseListener(a);
                    }
                }
            }
        } else {
            //if the capability was queried too.
            for (Capability b : dummy.capabilities) {
                Capability a = new Capability();
                a.transformCapability(b);
                capabilities.add(a);
                ThinClient.getInstance().addResponseListener(a);
            }
        }
        this.properties.clear();
        this.properties.addAll(dummy.getProperties());
        registered = true;
        int i = 0;
    }

    public void registerCapabilityListener(int capNumber, CapabilityListener capabilityListener) {
        try {
            this.capabilities.get(capNumber).addListener(capabilityListener);
        } catch (IndexOutOfBoundsException e) {
            map.put(capNumber, capabilityListener);
        }
    }

    @Override
    public void callback(ParameterOrganizer parameterOrganizer) {

    }

    /**
     * Getter and Setter
     * Mostly needed for serialize/deserialize
     **/
    public void setCapabilities(ArrayList<Capability> capabilities) {
        this.capabilities = capabilities;
    }

    public ArrayList<Capability> getCapabilities() {
        return capabilities;
    }

    public ArrayList<Property> getProperties() {
        return properties;
    }

    private void setProperties(ArrayList<Property> properties) {
        this.properties = properties;
    }

    public DeviceRequirement getRequirements() {
        return requirements;
    }

    /**
     * Utility Functions
     */
    public void printCompleteDescription() throws DeviceNotInstantiatedException {
        if(!registered)
            throw new DeviceNotInstantiatedException("This Device is not registered!");
        System.out.println("\nName of this device: " + this.getPropertyByName("name"));
        System.out.println("----------------------------------------");
        System.out.println("Device properties: ");
        printProperties(this.properties, 1);
        System.out.println("----------------------------------------");
        System.out.format("This device has %d capabilities. \n", this.capabilities.size());
        System.out.println();
        int j = 1, i = 1;
        for (Capability capability : this.capabilities) {
            System.out.format("%d. capability properties: ", i++);
            System.out.println();
            printProperties(capability.getProperties(), 1);
            System.out.println();
            System.out.println("\tAdditional Properties for triggering this capability: ");
            if (!capability.getSendCapabilityParameter().isEmpty()) {
                ArrayList<Property> properties = new ArrayList<>();
                for (CapabilityParameter a : capability.getSendCapabilityParameter())
                    properties.addAll(a.getProperties());
                printProperties(properties, 2);
                System.out.println();
                System.out.format("It requires %d parameters, with the following order of datatypes: \n", capability.getSendCapabilityParameter().size());
                j = 1;
                for (CapabilityParameter a : capability.getSendCapabilityParameter()) {
                    System.out.println("\t" + j++ + ". parameter name: " + a.getPropertyByName("name") + " datatype: " + a.getValueType());
                    //printValues(variable);
                    printProperties(a.getProperties(), 2);
                }
            } else {
                System.out.println("This Capability doesn't require parameter.");
            }
            if (!capability.getReceiveCapabilityParameter().isEmpty()) {
                System.out.println("\nThis capability does have a callback, with the following order of datatypes: ");
                System.out.println();
                System.out.println("\tAdditional Properties for receiving the Results (callback) of this capability: ");
                ArrayList<Property> properties = new ArrayList<>();
                for (CapabilityParameter a : capability.getReceiveCapabilityParameter())
                    properties.addAll(a.getProperties());
                printProperties(properties, 2);
                j = 1;
                for (CapabilityParameter a : capability.getReceiveCapabilityParameter()) {
                    System.out.println("\t" + j++ + ". parameter name: " + a.getPropertyByName("name") + " datatype: " + a.getValueType());
                    printProperties(a.getProperties(), 2);
                }
            } else {
                System.out.println("This capability doesn't have a callback.");
            }
            System.out.println("----------------------------------------");
        }
    }

    private void printProperties(ArrayList<Property> properties, int number_indents) {
        for (Property property : properties) {
            for (int i = 0; i < number_indents; i++)
                System.out.print("\t");
            System.out.print(property.getName() + "(" + property.getDescription() + ")" + ": ");
            System.out.print(property.getValue().getObject() + " (" + property.getValue().getValueType() + "), ");
            System.out.println();
        }
    }

    private void printValues(Variable variable) {
        System.out.print(variable.getValueType());

        /* This can be put. then it displays the java classes needed, for now this has no use
        switch (variable.getValueType()) {
            case INTEGER:
                System.out.print(Integer.class);
                break;

            case DOUBLE:
                System.out.print(Double.class);
                break;

            case STRING:
                System.out.print(String.class);
                break;

            case BYTE:
                System.out.print(Byte.class);
                break;

            case BOOLEAN:
                System.out.print(Boolean.class);
                break;

            default:
                break;
        }*/
        System.out.println();
        System.out.print("\tProperties: \n");
        printProperties(variable.getProperties(), 2);
        System.out.println();
    }


    public Capability getCapability(int i) throws CapabilityNotFoundException {
        try {
            return capabilities.get(i);
        } catch (IndexOutOfBoundsException e) {
            throw new CapabilityNotFoundException("This Capability seems not to be instantiated. (Capability number: " + i + ")", e);
        }
    }

    public Capability getCapability(String s) {//throws CapabilityNotFoundException {
        if(!registered)
            throw new DeviceNotInstantiatedException("This Device is not registered!");
        for (Capability c : capabilities) {
            if (c.getCapabilityPropertyByName("name").equals(s))
                return c;
        }
        return null;
        //throw new CapabilityNotFoundException("This Capability seems not to be instantiated. (Capability name: " + s + ")");
    }

    public String getPropertyByName(String name) throws DeviceNotInstantiatedException {
        if(!registered)
            throw new DeviceNotInstantiatedException("This Device is not registered!");
        for (Property property : properties) {
            if (property.getName().equals(name)) {
                return property.getValue().getObject().toString();
            }
        }
        return "";
    }

    /**
     * DO NOT TOUCH!
     * @param registered
     */
    public void setRegistered(boolean registered) {
        this.registered = registered;
    }

    public boolean getRegistered() {
        return registered;
    }
}