package Networking;

import Commands.*;
import Commands.data.CapabilityRequirement;
import Commands.data.Parameter;
import com.google.gson.*;
import com.google.gson.reflect.TypeToken;
import data.Capabilities.Capability;
import data.Capabilities.CapabilityNotInitiatedException;
import data.Capabilities.ResponseListener;
import data.Devices.Device;
import data.Devices.DeviceNotInstantiatedException;

import java.io.*;
import java.lang.reflect.Type;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class ThinClient extends Thread {

    private boolean running;
    private int udpPort;
    private Socket socket;
    private static ThinClient instance;
    private BufferedReader bufferedReader;
    private ArrayList<ResponseListener> responseListeners = new ArrayList<>();

    private CommandContainer commandContainer = new CommandContainer();

    private Gson gson;

    public static ThinClient getInstance() {
        if (instance == null) {
            instance = new ThinClient(1500, "127.0.0.1");
        }
        return instance;
    }

    private ThinClient(int port, String ipAddress) {
        try {
            this.socket = new Socket(ipAddress, port);
            this.socket.setSoTimeout(1000);
            this.running = true;
            this.bufferedReader =
                    new BufferedReader(
                            new InputStreamReader(
                                    this.socket.getInputStream()));
        } catch (IOException e) {
            System.err.println("No INTERNET!!!");
        }
        GsonBuilder builder = new GsonBuilder();
        JsonSerializer<ArrayList<Parameter>> serializer = new JsonSerializer<ArrayList<Parameter>>() {
            @Override
            public JsonElement serialize(ArrayList<Parameter> src, Type typeOfSrc, JsonSerializationContext context) {
                JsonObject newJson = new JsonObject();
                for (Parameter p : src) {
                    if (p.getContent() instanceof Number)
                        newJson.addProperty(p.getUri(), (Number) p.getContent());
                    else if (p.getContent() instanceof String)
                        newJson.addProperty(p.getUri(), (String) p.getContent());
                    else if (p.getContent() instanceof Character)
                        newJson.addProperty(p.getUri(), (Character) p.getContent());
                    else if (p.getContent() instanceof Boolean)
                        newJson.addProperty(p.getUri(), (Boolean) p.getContent());
                    else if (p.getContent() instanceof  Object[]) {
                        JsonArray arr = new JsonArray();
                        for(Object o : (Object[])p.getContent())
                            arr.add((double)o);
                        newJson.add(p.getUri(), arr);
                    }
                }
                return newJson;
            }
        };
        Type parameterListType = new TypeToken<ArrayList<Parameter>>() {
        }.getType();

        builder.registerTypeAdapter(parameterListType, serializer);

        JsonDeserializer<ArrayList<Parameter>> deserializer = new JsonDeserializer<ArrayList<Parameter>>() {
            @Override
            public ArrayList<Parameter> deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
                ArrayList<Parameter> parameters = new ArrayList<>();
                JsonObject obj = jsonElement.getAsJsonObject();

                for (Map.Entry<String, JsonElement> entry : obj.entrySet()) {
                    JsonElement p = entry.getValue();
                    if(p.isJsonPrimitive()) {
                        if (p.getAsJsonPrimitive().isBoolean())
                            parameters.add(new Parameter(entry.getKey(), p.getAsBoolean()));
                        else if (p.getAsJsonPrimitive().isNumber())
                            parameters.add(new Parameter(entry.getKey(), p.getAsDouble()));
                        else if (p.getAsJsonPrimitive().isString())
                            parameters.add(new Parameter(entry.getKey(), p.getAsString()));
                    }
                    else if(p.isJsonArray()){
                        List<Double> list = new ArrayList<>();

                        for(JsonElement sda: p.getAsJsonArray()){
                            list.add(sda.getAsDouble());
                        }
                        parameters.add(new Parameter(entry.getKey(), list.toArray()));
                    }
                }
                return parameters;
            }
        };

        builder.registerTypeAdapter(parameterListType, deserializer);

        JsonSerializer<CapabilityRequirement> serializerReq = new JsonSerializer<CapabilityRequirement>() {
            @Override
            public JsonElement serialize(CapabilityRequirement src, Type typeOfSrc, JsonSerializationContext context) {
                JsonArray ret = new JsonArray();
                for (String s : src.getCapability())
                    ret.add(s);
                return ret;
            }
        };
        builder.registerTypeAdapter(CapabilityRequirement.class, serializerReq);

        JsonDeserializer<CapabilityRequirement> deserializerReq = new JsonDeserializer<CapabilityRequirement>() {
            @Override
            public CapabilityRequirement deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext jsonDeserializationContext) throws JsonParseException {
                System.out.println("Trying to do sth: " + jsonElement);
                CapabilityRequirement capabilityRequirement = new CapabilityRequirement();
                for (JsonElement e : jsonElement.getAsJsonArray()) {
                    capabilityRequirement.addRequirement(e.getAsString());
                }
                return capabilityRequirement;
            }
        };
        builder.registerTypeAdapter(CapabilityRequirement.class, deserializerReq);

        builder.setLenient();
        this.gson = builder.create();
        //Device c = gson.fromJson("{\"src\": \"ood-api-query-{\\\"device\\\":[\\\"SearchGridDevice\\\"],\\\"capabilities\\\":[]}\", \"type\": \"device\", \"json\": {\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"SearchGridDevice\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:SearchGridDevice\", \"valueType\": \"STRING\"}}], \"capabilities\": [{\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"GetISSECopterPosition\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:GetISSECopterPosition\", \"valueType\": \"STRING\"}}], \"sendParameter\": [], \"receiveParameter\": [{\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"Position3D\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:Position3D\", \"valueType\": \"STRING\"}}], \"valueType\": \"NONE\"}]}, {\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"SearchGridGetNextPosition\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:SearchGridGetNextPosition\", \"valueType\": \"STRING\"}}], \"sendParameter\": [], \"receiveParameter\": [{\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"Position3D\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:Position3D\", \"valueType\": \"STRING\"}}], \"valueType\": \"NONE\"}, {\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"Position3D\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:Position3D\", \"valueType\": \"STRING\"}}], \"valueType\": \"NONE\"}, {\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"TestFieldPointA\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:TestFieldPointA\", \"valueType\": \"STRING\"}}], \"valueType\": \"NONE\"}, {\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"TestFieldPointB\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:TestFieldPointB\", \"valueType\": \"STRING\"}}], \"valueType\": \"NONE\"}]}, {\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"GetTestFieldBoundaries\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:GetTestFieldBoundaries\", \"valueType\": \"STRING\"}}], \"sendParameter\": [], \"receiveParameter\": [{\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"TestFieldPointA\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:TestFieldPointA\", \"valueType\": \"STRING\"}}], \"valueType\": \"NONE\"}, {\"properties\": [{\"name\": \"name\", \"description\": \"the name (aka rdfs:label)\", \"value\": {\"object\": \"TestFieldPointB\", \"valueType\": \"STRING\"}}, {\"name\": \"description\", \"description\": \"the description (aka rdfs:comment)\", \"value\": {\"object\": \"unkown\", \"valueType\": \"STRING\"}}, {\"name\": \"uri\", \"description\": \"the URI of this object\", \"value\": {\"object\": \"commands:TestFieldPointB\", \"valueType\": \"STRING\"}}], \"valueType\": \"NONE\"}]}], \"requirements\": [\"SearchGridDevice\"]}}", InstantiateDeviceCommand.class).getJson();
        //c.printCompleteDescription();
        this.start();
    }

    public Thread registerDevice(Device device) throws CommandAlreadyInvokedException, InvalidCommandException {
        //@TODO transform to query
        QueryDeviceCommand command = new QueryDeviceCommand(device, "ood-api-query-" + device.getRequirements().toString());
        this.commandContainer.insertCommand(command, device);
        Thread ret = new Thread(() -> {
            sendMessage(gson.toJson(command, QueryDeviceCommand.class));
            while (!device.getRegistered());
        });
        ret.start();
        return ret;
    }

    public Thread unregisterDevice(Device device) throws CommandAlreadyInvokedException, InvalidCommandException, DeviceNotInstantiatedException {
        RemoveDeviceRequestCommand command = new RemoveDeviceRequestCommand("ood-api-remove-" + device.getPropertyByName("name"), device);
        this.commandContainer.insertCommand(command, device);

        Thread ret = new Thread(() -> {
            sendMessage(gson.toJson(command, RemoveDeviceRequestCommand.class));
            while (commandContainer.check(command)) ;
        });
        ret.start();
        return ret;
    }

    /**
     * Invokes a Capability, with optional Routine to be called upon receiving results
     *
     * @param invokeCapabilityCommand A Command to invoke the cap
     * @param callback                nullable
     */
    public AnswerThread invokeCapability(InvokeCapabilityCommand invokeCapabilityCommand, CommandCallback callback) throws InvalidCommandException, CommandAlreadyInvokedException {
        //If a callback for this specific
        invokeCapabilityCommand.setSrc(String.format("ood-api-%s-invoke-%d", invokeCapabilityCommand.getCapability(), System.currentTimeMillis()));
        AnswerThread a = new AnswerThread(() -> {
            sendMessage(gson.toJson(invokeCapabilityCommand, InvokeCapabilityCommand.class));
            //if(invokeCapabilityCommand.getStreaming() > 0)
            while (commandContainer.check(invokeCapabilityCommand));
        });
        this.commandContainer.addAnswerThread(invokeCapabilityCommand, a);
        this.commandContainer.insertCommand(invokeCapabilityCommand, callback);
        return a;
    }

    private void sendMessage(String message) {
        try {
            System.out.println("[ThinClient] Sending Message: " + message);
            PrintWriter printWriter =
                    new PrintWriter(
                            new OutputStreamWriter(
                                    socket.getOutputStream()));
            printWriter.print(message);
            printWriter.flush();
        } catch (IOException e) {
            System.out.println("[ThinClient] Has Lost connection, shutting down... ");
            System.exit(-1);
        }
    }

    public void run() {
        while (running) {
            try {
                char[] buff = new char[8192];
                int length = this.bufferedReader.read(buff, 0, buff.length);
                String received = new String(buff, 0, length);
                System.out.println("[ThinClient] Received: " + received);
                if (received.charAt(0) == '{') {
                    BasicCommand b = gson.fromJson(received, BasicCommand.class);
                    //System.out.format("[ThinClient] Received Command type: %s for src: %s\n", b.getType(), b.getSrc());
                    switch (b.getType()) {
                        case "device":
                            InstantiateDeviceCommand q = gson.fromJson(received, InstantiateDeviceCommand.class);
                            commandContainer.handleDevice(q);
                            break;
                        case "response":
                            ResponseOfCapabilityCommand c = gson.fromJson(received, ResponseOfCapabilityCommand.class);
                            commandContainer.handleResponse(c);
                            newResponse(c);
                            break;
                        case "removed":
                            DeviceRemovedCommand d = gson.fromJson(received, DeviceRemovedCommand.class);
                            commandContainer.handleRemove(d);
                            break;
                        default:
                            System.out.println("DEFAULT");
                            break;
                    }
                }
            } catch (SocketTimeoutException timeout) {
                continue;
            } catch (Exception exception) {
                exception.printStackTrace();
                continue;
            }
        }
    }

    public void kill() {
        this.running = false;
    }

    public void addResponseListener(ResponseListener listener) {
        //System.out.println("[ThinClient] Adding Response Listener: " + listener);
        if (responseListeners.contains(listener))
            return;
        responseListeners.add(listener);
    }

    public void removeResponseListener(ResponseListener listener) {
        responseListeners.remove(listener);
    }

    private void newResponse(ResponseOfCapabilityCommand message) {
        for (ResponseListener l : responseListeners) {
            if (l.getClass() == Capability.class) {
                try {
                    if (((Capability) l).getURI().equals(message.getCapability()))
                        l.fireNewResponse(message);
                } catch (CapabilityNotInitiatedException e) {
                    //System.out.println("Capability no longer running!");
                }
            } else {
                l.fireNewResponse(message);
            }
        }
    }

}
