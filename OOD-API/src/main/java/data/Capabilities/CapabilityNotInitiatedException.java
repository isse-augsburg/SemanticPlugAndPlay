package data.Capabilities;

public class CapabilityNotInitiatedException extends Exception {
    public CapabilityNotInitiatedException(String s) {
        super(s);
    }

    public CapabilityNotInitiatedException(String s, Throwable cause) {
        super(s, cause);
    }
}
