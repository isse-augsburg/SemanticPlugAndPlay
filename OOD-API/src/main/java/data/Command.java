package data;

import data.Property.Property;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.IllegalFormatConversionException;

/**
 * Normally a abstract class, but Gson prohibits this.
 * A Command consists of a message, in which keys in Form of Strings exist
 */
public class Command {
    //Message = "setRed(val)"
    //message_tobe = "setRed(777)"
    private String message;
    //val -> int
    //private HashMap<String, ValueType> variables = new HashMap<String, ValueType>();
    private ArrayList<Variable> variables = new ArrayList<>();
    private ArrayList<Property> properties = new ArrayList<>();

    /**
     * Empty Constructor
     */
    public Command() {

    }

    public Command(String message) {
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    /**
     * @param objects the Parameters for a function
     * @return the "new" message, when keys are replaced by concrete values.
     */
    public String check(Object[] objects) throws IllegalArgumentException {
        String h = this.message;
        int i = 0;
        if (objects.length != this.variables.size())
            throw new IllegalArgumentException("[Command] Received a different Number of Parameters: Expected " + this.getVariables().size() + "| Received " + objects.length);
        for (Variable variable : this.variables) {
            Object object = objects[i++];
            switch (variable.getValueType()) {
                case INTEGER:
                    if (object.getClass() != java.lang.Integer.class)
                        throw new IllegalArgumentException("Object is no Integer, aborting...");
                    break;

                case DOUBLE:
                    if (object.getClass() != java.lang.Double.class)
                        throw new IllegalArgumentException("Object is no Double, aborting...");
                    break;

                case STRING:
                    if (object.getClass() != java.lang.String.class)
                        throw new IllegalArgumentException("Object is no String, aborting...");
                    break;

                case BYTE:
                    if (object.getClass() != java.lang.Byte.class)
                        throw new IllegalArgumentException("Object is no Byte, aborting...");
                    break;

                case BOOLEAN:
                    if (object.getClass() != java.lang.Boolean.class)
                        throw new IllegalArgumentException("Object is no Boolean, aborting...");
                    break;
            }
            h = h.replace(variable.getKey(), object.toString());
        }
        return h;
    }

    public void addVariable(String var, ValueType valtype, Property property) {
        this.variables.add(new Variable(var, valtype, property));
    }


    public ArrayList<Variable> getVariables() {
        return variables;
    }

    public void setVariables(ArrayList<Variable> variables) {
        this.variables = variables;
    }

    public ArrayList<Property> getProperties() {
        return properties;
    }

    public void setProperties(ArrayList<Property> properties) {
        this.properties = properties;
    }
}
