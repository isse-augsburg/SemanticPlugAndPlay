package data.Property;

import data.ValueType;

import java.util.ArrayList;

public class Property {

    private String name;
    private String description;
    private Pair value;

    Property() {

    }

    public Property(String name, String description, Pair value_pair) {
        this.name = name;
        this.description = description;
        this.value = value_pair;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Pair getValue() {
        return value;
    }

    public void setValue(Pair value) {
        this.value = value;
    }

    public void setValue(Object object, ValueType valueType) {
        this.value = new Pair(object, valueType);
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
