package Networking;

import Commands.data.Parameter;

import java.util.ArrayList;
import java.util.Collections;

public class ParameterOrganizer {
    ArrayList<Parameter> parameters = new ArrayList<>();


    ParameterOrganizer(Parameter[] parameters){
        Collections.addAll(this.parameters, parameters);
    }

    ParameterOrganizer(ArrayList<Parameter> parameters){
        this.parameters.addAll(parameters);
    }

    public Object getContent(String key){
        for(Parameter p : this.parameters){
            if(p.getUri().equals(key))
                return p.getContent();
        }
        return null;
    }

    public ArrayList<Parameter> getAsList() {
        return parameters;
    }
}