package Commands;

import Commands.data.Parameter;

import java.util.ArrayList;
import java.util.Arrays;

public class InvokeCapabilityCommand extends BasicCommand {
    private ArrayList<Parameter> parameters = new ArrayList<>();
    private String capability;
    private String device;
    private Double streaming = 0.;

    public InvokeCapabilityCommand() {
        super();
    }

    public InvokeCapabilityCommand(String capability, double streaming, Parameter[] objects) {
        this.streaming = streaming;
        this.setType("trigger");
        parameters.addAll(Arrays.asList(objects));
        this.capability = capability;
    }

    public InvokeCapabilityCommand(String capability, Parameter[] objects) {
        this.setType("trigger");
        parameters.addAll(Arrays.asList(objects));
        this.capability = capability;
    }

    public ArrayList<Parameter> getParameters() {
        return parameters;
    }

    public void setParameters(ArrayList<Parameter> parameters) {
        this.parameters = parameters;
    }

    public String getCapability() {
        return capability;
    }

    public void setCapability(String capability) {
        this.capability = capability;
    }

    public Double getStreaming() {
        return streaming;
    }

    public void setStreaming(Double streaming) {
        this.streaming = streaming;
    }

    public String getDevice() {
        return device;
    }

    public void setDevice(String device) {
        this.device = device;
    }
}
