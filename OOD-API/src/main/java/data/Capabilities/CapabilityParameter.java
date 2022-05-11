package data.Capabilities;

import data.Property.Property;
import data.ValueType;

import java.util.ArrayList;

public class CapabilityParameter {
    private ArrayList<Property> properties = new ArrayList<>();
    private ValueType valueType = ValueType.STRING;

    public CapabilityParameter(){}

    public CapabilityParameter(Property p, ValueType type){
        valueType = type;
        this.properties.add(p);
    }

    public ArrayList<Property> getProperties() {
        return properties;
    }

    public void setProperties(ArrayList<Property> properties) {
        this.properties = properties;
    }

    public ValueType getValueType() {
        return valueType;
    }

    public void setValueType(ValueType valueType) {
        this.valueType = valueType;
    }

    public String getPropertyByName(String name) {
        for (Property property : properties) {
            if (property.getName().equals(name)) {
                return property.getValue().getObject().toString();
            }
        }
        return "";
    }
}
