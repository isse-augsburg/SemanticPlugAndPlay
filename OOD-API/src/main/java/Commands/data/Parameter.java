package Commands.data;

import data.ValueType;

public class Parameter {
    private String uri;
    private Object content;

    public Parameter() {
    }

    public Parameter(String uri, Object content) {
        this.content = content;
        this.uri = uri;
    }

    public Object getContent() {
        return content;
    }

    public void setContent(Object content) {
        this.content = content;
    }

    public String getUri() {
        return uri;
    }

    public void setUri(String uri) {
        this.uri = uri;
    }
}
