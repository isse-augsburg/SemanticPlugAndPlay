package Commands;

public class BasicCommand {
    private String type = "";
    private String src;

    public BasicCommand(){

    }

    public BasicCommand(String type, String src){
        this.type = type;
        this.src = src;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getSrc() {
        return src;
    }

    public void setSrc(String src) {
        this.src = src;
    }
}
