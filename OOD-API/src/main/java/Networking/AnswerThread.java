package Networking;

import Commands.data.Parameter;

import java.util.ArrayList;
import java.util.Collections;

public class AnswerThread {
    private Thread thread = null;

    private ParameterOrganizer organizer = null;

    public Thread getThread() {
        return thread;
    }

    AnswerThread(Runnable runnable){
        thread = new Thread(runnable);
        thread.start();
    }

    public ParameterOrganizer waitForAnswer(){
        try {
            thread.join();
            while (organizer == null) {
                Thread.sleep(1000);

            }
        }catch (Exception e){
            e.printStackTrace();
        }
        return organizer;
    }

    public Object waitForAnswer(String uri){
        try {
            thread.join();
            while (organizer == null) {
                Thread.sleep(1000);

            }
        }catch (Exception e){
            e.printStackTrace();
        }
        return organizer.getContent(uri);
    }

    public ParameterOrganizer getOrganizer() {
        return organizer;
    }

    public void join(){
        try {
            thread.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    void addAnswers(ArrayList<Parameter> parameters) {
        organizer = new ParameterOrganizer(parameters);
    }

}
