package data;

import data.Property.Property;

import java.util.ArrayList;

public class Variable {
    private String key;
    private ValueType valueType;
    private ArrayList<Property> properties = new ArrayList<>();

    public Variable(){

    }

    public Variable(String var, ValueType valtype, Property property) {
        this.key = var;
        this.valueType = valtype;
        this.properties.add(property);
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public ValueType getValueType() {
        return valueType;
    }

    public void setValueType(ValueType valueType) {
        this.valueType = valueType;
    }

    public ArrayList<Property> getProperties() {
        return properties;
    }

    public void setProperties(ArrayList<Property> properties) {
        this.properties = properties;
    }

    public String toString(){
        return key + " | " + valueType;
    }
}
