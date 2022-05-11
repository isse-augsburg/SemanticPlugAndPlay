package data.Property;

import data.ValueType;

public class Pair {
    private Object object;
    private ValueType valueType;

    public Pair(){

    }

    public Pair(Object object, ValueType valueType) {
        this.object = object;
        this.valueType = valueType;
    }

    public Object getObject() {
        return object;
    }

    public void setObject(Object object) {
        this.object = object;
    }

    public ValueType getValueType() {
        return valueType;
    }

    public void setValueType(ValueType valueType) {
        this.valueType = valueType;
    }
}
