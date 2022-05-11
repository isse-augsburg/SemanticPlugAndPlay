package data.Capabilities;

public class CapabilityNotFoundException extends Exception {
    public CapabilityNotFoundException(String s) {
        super(s);
    }

    public CapabilityNotFoundException(String s, Throwable cause) {
        super(s, cause);
    }
}
