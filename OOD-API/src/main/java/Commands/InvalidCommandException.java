package Commands;

public class InvalidCommandException extends Exception {
    public InvalidCommandException(String s) {
        super(s);
    }

    public InvalidCommandException(String s, Throwable cause) {
        super(s, cause);
    }
}
