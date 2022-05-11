package Commands;

public class CommandAlreadyInvokedException extends Exception {
    public CommandAlreadyInvokedException(String s) {
        super(s);
    }

    public CommandAlreadyInvokedException(String s, Throwable cause) {
        super(s, cause);
    }
}

