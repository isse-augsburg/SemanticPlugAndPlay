package data.Property;

import data.ValueType;

public class StaticProperty extends Property {

    public StaticProperty(String name, String description, Object property, ValueType valueType){
        this.setValue(property, valueType);
        this.setName(name);
        this.setDescription(description);
    }

    public StaticProperty(String name, String description, Pair pair){
        this.setName(name);
        this.setValue(pair);
        this.setDescription(description);
    }

    public StaticProperty(){

    }

}
