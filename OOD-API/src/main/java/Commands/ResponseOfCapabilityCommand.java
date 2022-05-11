package Commands;

import Commands.data.Parameter;

import java.util.ArrayList;

public class ResponseOfCapabilityCommand extends BasicCommand {
    private ArrayList<Parameter> parameters = new ArrayList<>();
    private String capability;

    public ResponseOfCapabilityCommand() {
        super();
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


}
