package Commands;

import Commands.data.Parameter;
import Networking.AnswerThread;
import Networking.ParameterOrganizer;
import data.Devices.DeviceNotInstantiatedException;

import java.io.Serializable;
import java.util.ArrayList;

public interface CommandCallback extends Serializable {

    void callback(ParameterOrganizer parameterOrganizer);
}