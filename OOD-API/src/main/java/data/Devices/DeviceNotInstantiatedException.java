package data.Devices;

public class DeviceNotInstantiatedException extends NullPointerException {
    public DeviceNotInstantiatedException(String s) {
        super(s);
    }

    public DeviceNotInstantiatedException(String s, Throwable cause) {
        super(s + "from " + cause.getLocalizedMessage());
    }
}
