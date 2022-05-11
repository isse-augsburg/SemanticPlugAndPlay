package Commands;

public class CommandNotFoundException extends Exception {
    public CommandNotFoundException(String s) {
        super(s);
    }

    public CommandNotFoundException(String s, Throwable cause) {
        super(s, cause);
    }
}
