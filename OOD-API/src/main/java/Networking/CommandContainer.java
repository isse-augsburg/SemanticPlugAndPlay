package Networking;

import Commands.*;
import data.Command;
import data.Devices.Device;
import data.Devices.DeviceContainer;

import java.util.HashMap;

class CommandContainer extends Thread {
    private HashMap<BasicCommand, CommandCallback> map = new HashMap<>();
    private HashMap<String, AnswerThread> answerThreadHashMap = new HashMap<>();

    boolean check(BasicCommand command){
        return map.containsKey(command) && answerThreadHashMap.containsKey(command.getSrc());
    }

    void insertCommand(BasicCommand command, CommandCallback callback) throws CommandAlreadyInvokedException, InvalidCommandException {
        if(command.getSrc() == null || command.getSrc().isEmpty() || command.getType() == null || command.getType().isEmpty())
            throw new InvalidCommandException("Command is invalid!");
        if(map.containsKey(command))
            throw new CommandAlreadyInvokedException("Command already invoked!!");
        if(callback != null)
            map.put(command, callback);
    }

    void addAnswerThread(BasicCommand b, AnswerThread a){
        this.answerThreadHashMap.put(b.getSrc(), a);
    }

    void handleResponse(ResponseOfCapabilityCommand command) {
        if(answerThreadHashMap.containsKey(command.getSrc())) {
            answerThreadHashMap.get(command.getSrc()).addAnswers(command.getParameters());
            answerThreadHashMap.remove(command.getSrc());
        }
            try {
            if (checkSrc(command.getSrc())) {
                BasicCommand srcCommand = getCommand(command.getSrc());
                map.get(srcCommand).callback(new ParameterOrganizer(command.getParameters()));
                if (((InvokeCapabilityCommand) srcCommand).getStreaming() == null || ((InvokeCapabilityCommand) srcCommand).getStreaming() == 0.0)
                    map.remove(srcCommand);
            }
        } catch (CommandNotFoundException e){
            e.printStackTrace();
        }
    }

    void handleDevice(InstantiateDeviceCommand command)  {
        try {
            BasicCommand srcCommand = getCommand(command.getSrc());
            ((Device) map.get(srcCommand)).transformDevice(command.getJson());
            //map.remove(srcCommand);
        } catch (CommandNotFoundException e) {
            e.printStackTrace();
        }

    }

    void handleRemove(DeviceRemovedCommand command) {
        if(checkSrc(command.getSrc())){
            try {
                ((Device) map.get(getCommand(command.getSrc()))).deleteData();
                map.remove(getCommand(command.getSrc()));
            } catch (CommandNotFoundException e) {
                e.printStackTrace();
            }
        } else {
            Device deleted = DeviceContainer.getInstance().getDevice(command.getDev_req());
            deleted.deleteData();
            deleted.registerDevice();
            System.out.println("Removing Device " + deleted.getRequirements().toString() + " and reregistered it.");
        }

    }

    private BasicCommand getCommand(String src) throws CommandNotFoundException {
        for(BasicCommand c:map.keySet()){
            if(c.getSrc().equals(src))
                return c;
        }
        throw new CommandNotFoundException(String.format("No Command found for src %s!", src));
    }

    private boolean checkSrc(String src){
        for(BasicCommand c:map.keySet()){
            if(c.getSrc().equals(src))
                return true;
        }
        return false;
    }


    public void run(){

    }
}
